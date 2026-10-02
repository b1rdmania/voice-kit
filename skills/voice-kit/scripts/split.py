#!/usr/bin/env python3
"""Split a corpus into date-ordered chunks of about N words.

Usage: python3 split.py ~/voice/corpus.jsonl [--words 60000]
Writes chunk1.txt, chunk2.txt ... next to the corpus, one "[date] text" line per message.
"""

import argparse
import json
import os


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("corpus")
    ap.add_argument("--words", type=int, default=60000)
    a = ap.parse_args()
    path = os.path.expanduser(a.corpus)
    rows = sorted((json.loads(l) for l in open(path)), key=lambda r: r["t"])
    chunks, current, count = [], [], 0
    for r in rows:
        current.append(r)
        count += len(r["text"].split())
        if count >= a.words:
            chunks.append(current)
            current, count = [], 0
    if current:
        chunks.append(current)
    folder = os.path.dirname(path)
    for n, chunk in enumerate(chunks, 1):
        with open(os.path.join(folder, f"chunk{n}.txt"), "w") as o:
            o.write("\n".join(f"[{r['t']}] {r['text']}" for r in chunk))
        print(f"chunk{n}.txt: {chunk[0]['t']} to {chunk[-1]['t']}, {len(chunk)} messages")


if __name__ == "__main__":
    main()
