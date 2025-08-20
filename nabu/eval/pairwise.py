# nabu/eval/pairwise.py
from __future__ import annotations
import itertools
import math
import random
from typing import Callable, List, Optional, Sequence, Tuple

from sklearn.metrics import roc_auc_score
from .oracle import normalised_levenshtein
from .keyspace import MonoSubKeyspace

# A candidate is (key, plaintext, score, oracle_dist)
Candidate = Tuple[str, str, float, float]

def sample_pair_indices(n: int, max_pairs: int, rng: random.Random) -> Sequence[Tuple[int, int]]:
    """
    Uniformly sample up to max_pairs unordered pairs (i<j) without replacement.
    """
    if n < 2 or max_pairs <= 0:
        return []
    # total possible pairs
    # For large n, sample by rejection; for small n, enumerate then shuffle.
    if n <= 2000 and max_pairs >= (n*(n-1))//2:
        pairs = [(i, j) for i in range(n) for j in range(i+1, n)]
        rng.shuffle(pairs)
        return pairs[:max_pairs]
    pairs = set()
    attempts = 0
    while len(pairs) < max_pairs and attempts < max_pairs*10:
        i = rng.randrange(n-1)
        j = rng.randrange(i+1, n)
        pairs.add((i, j))
        attempts += 1
    return list(pairs)

def build_random_pool(
    ks: MonoSubKeyspace,
    ciphertext: str,
    fitness: Callable[[str], float],
    *,
    num_keys: int,
    rng: random.Random,
) -> List[Candidate]:
    """
    Sample random keys from the keyspace; decrypt and score.
    Oracle distances are filled later when the gold plaintext g is known.
    """
    pool: List[Candidate] = []
    for _ in range(num_keys):
        k = ks.random_key()
        x = ks.decrypt(ciphertext, k)
        s = fitness(x)
        pool.append((k, x, s, 0.0))
    return pool

def build_local_pool_exact_radius(
    ks: MonoSubKeyspace,
    true_key: str,
    ciphertext: str,
    fitness: Callable[[str], float],
    *,
    radius: int,
    per_seed: int,
    n_seeds: int,
    rng: random.Random,
) -> List[Candidate]:
    """
    Build a *ball* of candidates around multiple seeds (seed itself + neighbours at all radii ≤ r).
    Seeds are: {true_key} plus (n_seeds-1) random keys.
    For each seed and each d in 1..radius, sample 'per_seed' neighbours at exact distance d.
    """
    seeds = [true_key] + [ks.random_key() for _ in range(max(0, n_seeds - 1))]
    pool: List[Candidate] = []
    for seed in seeds:
        # include the seed (radius 0) so r=1 has valid seed↔neighbour pairs
        x0 = ks.decrypt(ciphertext, seed)
        s0 = fitness(x0)
        pool.append((seed, x0, s0, 0.0))
        for d in range(1, radius+1):
            for _ in range(per_seed):
                k = ks.neighbour_by_swaps(seed, d)
                if k == seed:
                    continue
                x = ks.decrypt(ciphertext, k)
                s = fitness(x)
                pool.append((k, x, s, 0.0))
    return pool

def build_pairwise_dataset(
    ks: MonoSubKeyspace,
    pool: List[Candidate],
    *,
    g: str,
    max_pairs: int,
    rng: random.Random,
    local_radius_cap: Optional[int] = None,
) -> Tuple[List[int], List[float]]:
    """
    From a pool of candidates, construct pairwise labels y and score-differences z.
    y = 1 if candidate i is *closer* to gold plaintext g (smaller oracle distance) than j; else 0.
    z = s_i - s_j, i.e., positive if fitness ranks i above j.
    If local_radius_cap is not None, keep only pairs whose *mutual* Cayley distance ≤ cap.
    """
    # fill oracle distances
    pool2: List[Candidate] = [(k, x, s, normalised_levenshtein(x, g)) for (k, x, s, _) in pool]
    n = len(pool2)
    if n < 2:
        return [], []
    keys = [k for (k, _, _, _) in pool2]
    dists = [d for (_, _, _, d) in pool2]
    scores = [s for (_, _, s, _) in pool2]

    y: List[int] = []
    z: List[float] = []

    for i, j in sample_pair_indices(n, max_pairs, rng):
        if local_radius_cap is not None:
            if ks.cayley_distance(keys[i], keys[j]) > local_radius_cap:
                continue
        di, dj = dists[i], dists[j]
        if di == dj:
            continue  # ignore ties in oracle
        yi = 1 if di < dj else 0
        zi = scores[i] - scores[j]
        y.append(yi)
        z.append(zi)
        if len(y) >= max_pairs:
            break

    return y, z

def auc_from_pairs(y: Sequence[int], z: Sequence[float]) -> float:
    """
    Compute AUC treating (y,z) as positives/negatives with scores=score-differences.
    Returns NaN if less than two classes present.
    """
    if not y:
        return float("nan")
    try:
        return roc_auc_score(y, z)
    except Exception:
        return float("nan")

def tpr_at_zero(y: Sequence[int], z: Sequence[float]) -> float:
    """
    Pairwise accuracy at threshold 0:
      correct if (z>0 and y=1) or (z<0 and y=0). Ties (z=0) ignored.
    """
    correct = 0
    total = 0
    for yi, zi in zip(y, z):
        if zi == 0:
            continue
        total += 1
        if (zi > 0 and yi == 1) or (zi < 0 and yi == 0):
            correct += 1
    return correct / total if total else float("nan")
