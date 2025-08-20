# example.py
from __future__ import annotations
from itertools import islice
from typing import List, Dict, Any
from tqdm import tqdm

from nabu.eval.rocEval import MonoSubEvaluator
from nabu.eval.streaming import stream_plaintexts_from_hf, default_clean_text
from nabu.eval.viz import plotRocPanelForPlaintext


def myFitness(text: str) -> float:
    """
    Unigram log-likelihood score: sum_i log p(char_i).
    Assumes input is already cleaned to [a-z] only.
    Higher is better (less negative).
    """
    logProbs = {
        'a': -2.4966452483625, 'b': -4.2354233094168, 'c': -3.3486757306932,
        'd': -3.3128001327250, 'e': -2.1169743058026, 'f': -3.8213517734372,
        'g': -3.8547433177710, 'h': -3.1595087861602, 'i': -2.5737619670459,
        'j': -6.4227092328015, 'k': -4.9393292753621, 'l': -3.1604294954037,
        'm': -3.6835202980909, 'n': -2.6297692035200, 'o': -2.5676852552873,
        'p': -3.7746674480023, 'q': -6.7270353094652, 'r': -2.7442558598409,
        's': -2.6958171182545, 't': -2.4177946239161, 'u': -3.5206505642792,
        'v': -4.4720428823618, 'w': -4.1357029373497, 'x': -6.0327463593828,
        'y': -3.9765738593564, 'z': -6.7842837617938
    }
    unknown = -10.0
    return sum(logProbs.get(ch, unknown) for ch in text)


def safe_mean(xs):
    vals = [v for v in xs if v == v]  # drop NaNs
    return sum(vals) / len(vals) if vals else float("nan")


if __name__ == "__main__":
    # Always evaluate exactly 3 texts
    maxTexts = 100
    minLen = 150

    # Build a Hugging Face streaming dataset and collect exactly 3 cleaned texts
    stream = stream_plaintexts_from_hf(
        dataset="HuggingFaceFW/fineweb-edu",
        name="sample-10BT",
        split="train",
        minLen=minLen,
        maxSamples=250,              # oversample so we can collect 3
        clean_fn=default_clean_text,
    )
    texts = list(islice(stream, maxTexts))
    if len(texts) < maxTexts:
        raise RuntimeError(f"Only found {len(texts)} texts ≥{minLen} chars")

    # Close the stream so the script exits cleanly after work
    try:
        stream.close()
    except Exception:
        pass

    evaluator = MonoSubEvaluator(alphabet="abcdefghijklmnopqrstuvwxyz", rngSeed=3)

    # Manual loop with explicit tqdm so it always reaches 3/3
    per_reports: List[Dict[str, Any]] = []
    with tqdm(total=len(texts)) as bar:
        for plain in texts:
            rep = evaluator.evaluate(
                plaintext=plain,
                fitnessFunc=myFitness,
                globalNumKeys=300,
                globalMaxPairs=20_000,
                localRadii=[1, 2, 3],
                localSeeds=3,
                localPerSeed=200,
                localMaxPairs=20_000,
                includeTrueKeyDiagnostic=True,
            )
            per_reports.append(rep)
            bar.update(1)

    # Aggregate results (macro averages) to match previous reporting
    globalAUCs = [r["aggregate"]["global_auc_pairwise"] for r in per_reports]
    globalTPR0s = [r["aggregate"]["global_tpr_at_zero"] for r in per_reports]

    localRadii = sorted(set().union(*[
        set(r["aggregate"]["local_auc_pairwise"].keys()) for r in per_reports
    ]))

    local_auc_macro = {
        r: safe_mean([rep["aggregate"]["local_auc_pairwise"].get(r, float("nan")) for rep in per_reports])
        for r in localRadii
    }
    local_tpr0_macro = {
        r: safe_mean([rep["aggregate"]["local_tpr_at_zero"].get(r, float("nan")) for rep in per_reports])
        for r in localRadii
    }

    aggregate = {
        "global_auc_pairwise_macro": safe_mean(globalAUCs),
        "global_tpr_at_zero_macro": safe_mean(globalTPR0s),
        "local_auc_pairwise_macro": local_auc_macro,
        "local_tpr_at_zero_macro": local_tpr0_macro,
    }
    print(aggregate)

    vizMetrics = plotRocPanelForPlaintext(
        alphabet="abcdefghijklmnopqrstuvwxyz",
        plaintext=texts[0],                 # reuse the first collected text
        fitnessFunc=myFitness,
        rngSeed=123,
        globalNumKeys=300,
        globalMaxPairs=20_000,
        localRadii=(1, 2, 3),
        localSeeds=3,
        localPerSeed=200,
        localMaxPairs=20_000,
        bootstrapB=400,                     # adjust for speed/precision
        savePath="roc_panel.png",           # writes a figure next to the script
    )
    print("viz:", vizMetrics)
