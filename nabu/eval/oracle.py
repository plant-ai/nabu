# nabu/eval/oracle.py
from __future__ import annotations
try:
    from Levenshtein import distance as levenshtein_distance
except Exception:  # pragma: no cover
    # Lightweight fallback if python-Levenshtein is not available.
    def levenshtein_distance(a: str, b: str) -> int:
        m, n = len(a), len(b)
        dp = list(range(n+1))
        for i, ca in enumerate(a, 1):
            prev = dp[0]
            dp[0] = i
            for j, cb in enumerate(b, 1):
                cur = dp[j]
                if ca == cb:
                    dp[j] = prev
                else:
                    dp[j] = 1 + min(prev, dp[j], dp[j-1])
                prev = cur
        return dp[n]

def normalised_levenshtein(x: str, g: str) -> float:
    """
    Oracle distance in [0,1]: lower is better (closer to ground-truth).
    """
    longestLength = max(len(x), len(g), 1)
    return levenshtein_distance(x, g) / longestLength
