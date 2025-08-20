# nabu/eval/viz.py
from __future__ import annotations
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple
import random
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, roc_auc_score

# flexible imports: package or flat scripts
try:
    from .keyspace import MonoSubKeyspace
    from .pairwise import (
        build_random_pool,
        build_local_pool_exact_radius,
        build_pairwise_dataset,
    )
except ImportError:  # running from nabu/eval as scripts
    from keyspace import MonoSubKeyspace
    from pairwise import (
        build_random_pool,
        build_local_pool_exact_radius,
        build_pairwise_dataset,
    )

# ---------------------------
# Utilities
# ---------------------------

def _safeAuc(y: List[int], z: List[float]) -> float:
    if not y or len(set(y)) < 2:
        return float("nan")
    try:
        return roc_auc_score(y, z)
    except Exception:
        return float("nan")

def bootstrapAucCI(y: List[int], z: List[float], *, rng: random.Random, B: int = 1000, alpha: float = 0.05) -> Tuple[float, float, float]:
    """
    Nonparametric bootstrap CI for AUC on (y,z). Returns (auc, lo, hi).
    If degenerate (no positives/negatives), returns (nan, nan, nan).
    """
    auc = _safeAuc(y, z)
    if not y or len(set(y)) < 2:
        return float("nan"), float("nan"), float("nan")
    n = len(y)
    aucs = []
    # Use numpy RNG for speed but seeded via Python RNG for reproducibility
    np_rng = np.random.default_rng(rng.randrange(2**63))
    idx = np.arange(n)
    for _ in range(B):
        samp = np_rng.choice(idx, size=n, replace=True)
        yy = [y[i] for i in samp]
        zz = [z[i] for i in samp]
        val = _safeAuc(yy, zz)
        if val == val:
            aucs.append(val)
    if not aucs:
        return auc, float("nan"), float("nan")
    lo, hi = np.quantile(aucs, [alpha/2, 1 - alpha/2])
    return auc, float(lo), float(hi)

def computeRoc(y: List[int], z: List[float]) -> Tuple[np.ndarray, np.ndarray, float]:
    """
    Return (fpr, tpr, auc). If degenerate, returns empty arrays and NaN AUC.
    """
    if not y or len(set(y)) < 2:
        return np.array([]), np.array([]), float("nan")
    fpr, tpr, _ = roc_curve(y, z)
    auc = roc_auc_score(y, z)
    return fpr, tpr, auc

# ---------------------------
# Pair builders (mirror evaluator)
# ---------------------------

def buildGlobalPairs(
    *,
    ks: MonoSubKeyspace,
    plaintext: str,
    ciphertext: str,
    fitnessFunc: Callable[[str], float],
    rng: random.Random,
    globalNumKeys: int,
    globalMaxPairs: int,
) -> Tuple[List[int], List[float]]:
    pool = build_random_pool(ks, ciphertext, fitnessFunc, num_keys=globalNumKeys, rng=rng)
    y, z = build_pairwise_dataset(ks, pool, g=plaintext, max_pairs=globalMaxPairs, rng=rng)
    return y, z

def buildLocalPairsForRadius(
    *,
    ks: MonoSubKeyspace,
    trueKey: str,
    plaintext: str,
    ciphertext: str,
    fitnessFunc: Callable[[str], float],
    rng: random.Random,
    radius: int,
    localSeeds: int,
    localPerSeed: int,
    localMaxPairs: int,
) -> Tuple[List[int], List[float]]:
    pool = build_local_pool_exact_radius(
        ks, trueKey, ciphertext, fitnessFunc,
        radius=radius, per_seed=localPerSeed, n_seeds=localSeeds, rng=rng
    )
    y, z = build_pairwise_dataset(
        ks, pool, g=plaintext, max_pairs=localMaxPairs, rng=rng, local_radius_cap=radius
    )
    return y, z

# ---------------------------
# Visualiser
# ---------------------------

def plotRocPanelForPlaintext(
    *,
    alphabet: str,
    plaintext: str,
    fitnessFunc: Callable[[str], float],
    rngSeed: int = 12345,
    globalNumKeys: int = 500,
    globalMaxPairs: int = 50_000,
    localRadii: Sequence[int] = (1, 2, 3),
    localSeeds: int = 3,
    localPerSeed: int = 200,
    localMaxPairs: int = 50_000,
    bootstrapB: int = 500,
    savePath: Optional[str] = None,
) -> Dict[str, Dict[str, float]]:
    """
    Build ROC curves and AUC CIs for:
      - Global random-key pairs
      - Local Cayley-ball pairs for each radius in localRadii
    Returns a dict of metrics and optionally saves a PNG at savePath.
    """
    rng = random.Random(rngSeed)
    ks = MonoSubKeyspace(alphabet, rngSeed)
    trueKey = ks.random_key()
    ciphertext = ks.encrypt(plaintext, trueKey)

    # Global
    yG, zG = buildGlobalPairs(
        ks=ks, plaintext=plaintext, ciphertext=ciphertext, fitnessFunc=fitnessFunc,
        rng=rng, globalNumKeys=globalNumKeys, globalMaxPairs=globalMaxPairs
    )
    fprG, tprG, aucG = computeRoc(yG, zG)
    aucG, loG, hiG = bootstrapAucCI(yG, zG, rng=rng, B=bootstrapB)

    # Local per radius
    rocDataLocal: Dict[int, Tuple[np.ndarray, np.ndarray, float]] = {}
    aucStatsLocal: Dict[int, Tuple[float, float, float]] = {}

    for r in localRadii:
        yL, zL = buildLocalPairsForRadius(
            ks=ks, trueKey=trueKey, plaintext=plaintext, ciphertext=ciphertext,
            fitnessFunc=fitnessFunc, rng=rng, radius=r,
            localSeeds=localSeeds, localPerSeed=localPerSeed, localMaxPairs=localMaxPairs
        )
        fpr, tpr, _ = computeRoc(yL, zL)
        a, lo, hi = bootstrapAucCI(yL, zL, rng=rng, B=bootstrapB)
        rocDataLocal[r] = (fpr, tpr, a)
        aucStatsLocal[r] = (a, lo, hi)

    # ---- Plot panel ----
    nCols = 1 + len(localRadii)
    fig, axes = plt.subplots(1, nCols, figsize=(4*nCols, 4), constrained_layout=True)

    def _plotOne(ax, fpr, tpr, auc, lo, hi, title: str):
        ax.plot([0,1], [0,1], linestyle="--", linewidth=1, alpha=0.6)
        if fpr.size and tpr.size:
            ax.plot(fpr, tpr, linewidth=2)
        ax.set_xlabel("FPR")
        ax.set_ylabel("TPR")
        ax.set_title(f"{title}\nAUC={auc:.3f} [{lo:.3f},{hi:.3f}]")
        ax.set_xlim(0,1); ax.set_ylim(0,1)
        ax.grid(True, alpha=0.2)

    # Global
    _plotOne(axes[0], fprG, tprG, aucG, loG, hiG, "Global")

    # Local
    for i, r in enumerate(localRadii, start=1):
        fpr, tpr, _ = rocDataLocal[r]
        a, lo, hi = aucStatsLocal[r]
        _plotOne(axes[i], fpr, tpr, a, lo, hi, f"Local r={r}")

    if savePath:
        fig.savefig(savePath, dpi=160)
    # Return metrics for logging
    out: Dict[str, Dict[str, float]] = {
        "global": {"auc": float(aucG), "lo": float(loG), "hi": float(hiG)},
        "local": {int(r): {"auc": float(aucStatsLocal[r][0]),
                           "lo": float(aucStatsLocal[r][1]),
                           "hi": float(aucStatsLocal[r][2])}
                  for r in localRadii}
    }
    return out
