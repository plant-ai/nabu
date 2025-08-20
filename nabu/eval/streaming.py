# nabu/eval/streaming.py
from __future__ import annotations
import re
from typing import Callable, Iterator, Optional
from datasets import load_dataset

def default_clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'[^\x00-\x7F]', '', text)
    text = re.sub(r'[^a-z]', '', text)
    return text.strip()

def stream_plaintexts_from_hf(
    dataset: str = "HuggingFaceFW/fineweb-edu",
    name: str = "sample-10BT",
    split: str = "train",
    *,
    minLen: int = 150,
    maxSamples: Optional[int] = None,
    clean_fn: Optional[Callable[[str], str]] = None,
) -> Iterator[str]:
    """
    Stream cleaned a–z plaintexts from HF Datasets (streaming=True).

    Returns a *closable generator*: you may (optionally) call .close() on the
    returned iterator to stop background streaming threads immediately.

    This function already enforces `minLen` and (if provided) `maxSamples`.
    """
    clean = clean_fn or default_clean_text
    ds = load_dataset(dataset, name=name, split=split, streaming=True)
    it = iter(ds)

    def gen():
        n = 0
        try:
            for row in it:
                raw = row.get("text", "")
                plain = clean(raw)
                if len(plain) < minLen:
                    continue
                yield plain
                n += 1
                if maxSamples is not None and n >= maxSamples:
                    return  # triggers finally, then closes underlying iterator
        finally:
            # Best-effort cleanup so the process can exit immediately.
            close = getattr(it, "close", None)
            if callable(close):
                try:
                    close()
                except Exception:
                    pass
    return gen()
