import csv
from typing import List
from math import log

def orderSums(maxOrder: int) -> List[int]:
    res = []
    for i in range(1, maxOrder + 1):
        total = 0
        with open(f"/content/{i}.csv", mode="r", newline="") as f:
            reader = csv.reader(f)
            next(reader, None)  # skip header
            for row in reader:
                count = int(row[-1])
                total += count
        res.append(total)
    return res

def convertToLog(sums: List[int], maxOrder: int):
    if maxOrder > len(sums):
        raise ValueError("Don't have enough sums to compute probabilities")

    # log of denominators (history counts) for each order
    totals = [log(n) for n in sums]

    for i in range(1, maxOrder + 1):
        with open(f"/content/{i}.csv", mode="r", newline="") as fin, \
             open(f"/content/{i}L.csv", mode="w", newline="") as fout:

            reader = csv.reader(fin)
            writer = csv.writer(fout)

            header = next(reader, None)
            if header:
                writer.writerow(header[:-1] + ["log_prob"])  # replace count column

            for row in reader:
                count = int(row[-1])
                logProb = log(count) - totals[i-1]  # log C(h,c) - log C(h)
                writer.writerow(row[:-1] + [logProb])
