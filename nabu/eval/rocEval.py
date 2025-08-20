# nabu/eval/rocEval.py
from __future__ import annotations
import random
from itertools import islice
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple, Any

from .keyspace import MonoSubKeyspace
from .pairwise import (
    build_random_pool,
    build_local_pool_exact_radius,
    build_pairwise_dataset,
    auc_from_pairs,
    tpr_at_zero,
)
from .oracle import normalised_levenshtein

class MonoSubEvaluator:
    """
    Evaluate a monoalphabetic substitution fitness function by global and local (Cayley-ball) AUC.
    """
    def __init__(self, alphabet: str = "abcdefghijklmnopqrstuvwxyz", rngSeed: Optional[int] = 12345) -> None:
        self.alphabet = alphabet
        self.ks = MonoSubKeyspace(alphabet, rngSeed)
        self.rng = random.Random(rngSeed)

    def evaluate(
        self,
        *,
        plaintext: str,
        fitnessFunc: Callable[[str], float],
        globalNumKeys: int = 500,
        globalMaxPairs: int = 50_000,
        localRadii: Sequence[int] = (1, 2, 3),
        localSeeds: int = 3,
        localPerSeed: int = 200,
        localMaxPairs: int = 50_000,
        includeTrueKeyDiagnostic: bool = True,
    ) -> Dict[str, Any]:
        ks = self.ks
        # Pick a random true key and form ciphertext
        trueKey = ks.random_key()
        ciphertext = ks.encrypt(plaintext, trueKey)

        # ---------- Global ----------
        globalPool = build_random_pool(ks, ciphertext, fitnessFunc, num_keys=globalNumKeys, rng=self.rng)
        yGlob, zGlob = build_pairwise_dataset(ks, globalPool, g=plaintext, max_pairs=globalMaxPairs, rng=self.rng)
        globalAUC = auc_from_pairs(yGlob, zGlob)
        globalTPR0 = tpr_at_zero(yGlob, zGlob)

        # Auxiliary: "true key vs rest" AUC (binary classification on oracle distance)
        auxGlobalBin = float("nan")
        if includeTrueKeyDiagnostic:
            # Add the true key candidate and compute AUC of oracle-distance vs score
            xTrue = ks.decrypt(ciphertext, trueKey)
            sTrue = fitnessFunc(xTrue)
            poolAux = globalPool + [(trueKey, xTrue, sTrue, 0.0)]
            # Treat label = 1 if candidate equals true plaintext (oracle distance 0), else 0
            labels = [1 if normalised_levenshtein(x, plaintext) == 0.0 else 0 for (_, x, _, _) in poolAux]
            scores = [s for (_, _, s, _) in poolAux]
            if len(set(labels)) == 2:
                from sklearn.metrics import roc_auc_score
                auxGlobalBin = roc_auc_score(labels, scores)

        # ---------- Local (ball semantics) ----------
        localAUCs: Dict[int, float] = {}
        localTPR0s: Dict[int, float] = {}
        auxLocalBin: Dict[int, float] = {}
        for r in localRadii:
            localPool = build_local_pool_exact_radius(
                ks, trueKey, ciphertext, fitnessFunc,
                radius=r, per_seed=localPerSeed, n_seeds=localSeeds, rng=self.rng
            )
            yLoc, zLoc = build_pairwise_dataset(
                ks, localPool, g=plaintext, max_pairs=localMaxPairs, rng=self.rng, local_radius_cap=r
            )
            localAUCs[r] = auc_from_pairs(yLoc, zLoc)
            localTPR0s[r] = tpr_at_zero(yLoc, zLoc)

            if includeTrueKeyDiagnostic:
                xTrue = ks.decrypt(ciphertext, trueKey)
                sTrue = fitnessFunc(xTrue)
                poolAux = localPool + [(trueKey, xTrue, sTrue, 0.0)]
                labels = [1 if normalised_levenshtein(x, plaintext) == 0.0 else 0 for (_, x, _, _) in poolAux]
                scores = [s for (_, _, s, _) in poolAux]
                from sklearn.metrics import roc_auc_score
                if len(set(labels)) == 2:
                    auxLocalBin[r] = roc_auc_score(labels, scores)
                else:
                    auxLocalBin[r] = float("nan")

        return {
            "aggregate": {
                "global_auc_pairwise": globalAUC,
                "global_tpr_at_zero": globalTPR0,
                "local_auc_pairwise": localAUCs,
                "local_tpr_at_zero": localTPR0s,
                "aux_global_true_vs_rest_auc": auxGlobalBin,
                "aux_local_true_vs_rest_auc": auxLocalBin,
            },
            "true_key": trueKey,
        }

    def evaluate_many(
        self,
        *,
        plaintextIter: Iterable[str],
        fitnessFunc: Callable[[str], float],
        maxTexts: int = 30,
        minLen: int = 150,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Consume exactly 'maxTexts' qualifying plaintexts (len≥minLen) from 'plaintextIter' and evaluate each.
        Using islice ensures progress bars wrap cleanly even if the inner loop does not exhaust the outer iterator.
        """
        filtered = (p for p in plaintextIter if len(p) >= minLen)
        perText: List[Dict[str, Any]] = []
        for t, plain in enumerate(islice(filtered, maxTexts), start=1):
            rep = self.evaluate(plaintext=plain, fitnessFunc=fitnessFunc, **kwargs)
            perText.append({"id": t-1, "len": len(plain), "report": rep})

        # Macro-averages
        def safe_mean(vals: List[Optional[float]]) -> float:
            xs = [v for v in vals if v == v]  # drop NaNs
            return sum(xs)/len(xs) if xs else float("nan")

        globalAUCs = [r["report"]["aggregate"]["global_auc_pairwise"] for r in perText]
        globalTPR0s = [r["report"]["aggregate"]["global_tpr_at_zero"] for r in perText]

        # For locals, average per radius over texts
        localRadii = set().union(*[
            set(r["report"]["aggregate"]["local_auc_pairwise"].keys()) for r in perText
        ]) if perText else set()

        localAUCmacro: Dict[int, float] = {}
        localTPR0macro: Dict[int, float] = {}
        for r in sorted(localRadii):
            localAUCmacro[r] = safe_mean([rpt["report"]["aggregate"]["local_auc_pairwise"].get(r, float("nan")) for rpt in perText])
            localTPR0macro[r] = safe_mean([rpt["report"]["aggregate"]["local_tpr_at_zero"].get(r, float("nan")) for rpt in perText])

        return {
            "aggregate": {
                "global_auc_pairwise_macro": safe_mean(globalAUCs),
                "global_tpr_at_zero_macro": safe_mean(globalTPR0s),
                "local_auc_pairwise_macro": localAUCmacro,
                "local_tpr_at_zero_macro": localTPR0macro,
            },
            "per_text": perText,
        }
