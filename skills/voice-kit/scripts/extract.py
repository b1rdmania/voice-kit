#!/usr/bin/env python3
"""Extract the messages a person typed or dictated to their AI tools.

Usage:
  python3 extract.py --source claude-code [--since 2026-01-01] --out ~/voice/corpus.jsonl
  python3 extract.py --source codex --out ~/voice/corpus.jsonl
  python3 extract.py --source chatgpt --path conversations.json --out ~/voice/corpus.jsonl
  python3 extract.py --source samples --path my-writing.txt --out ~/voice/corpus.jsonl

Sources:
  claude-code  ~/.claude/projects/**/*.jsonl
  codex        ~/.codex/sessions/**/*.jsonl
  chatgpt      conversations.json from a ChatGPT data export
  samples      a text file, one message or post per blank-line-separated block

Keeps only the person's own messages. Drops tool output, system text, pastes
(messages over 2,500 characters) and duplicates. Drops whole messages that mention
health, money, legal or ID matters. Redacts secrets, emails, URLs, handles,
phone numbers, card and bank numbers, ID numbers, postcodes, street addresses,
IP addresses and usernames in file paths. Replaces every capitalised word used
mid-sentence anywhere in the corpus, wherever it appears, with [name]: people,
places and companies all go. Voice lives in structure, not names.
Writes one JSON object per line: {"t": date, "source": ..., "text": ...}.

The corpus is private. Keep it in ~/voice/ and never commit or share it.
"""

import argparse
import glob
import json
import os
import re
import sys

MAX_CHARS = 2500  # longer messages are almost always pastes
SKIP_PREFIXES = ("<", "Base directory for this skill", "[Request interrupted",
                 "Caveat:", "This session is being continued", "[SYSTEM")
REDACT = [
    # Secrets first, so later patterns do not split them.
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.S), "[key]"),
    (re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"), "[token]"),
    (re.compile(r"\b(AKIA|ASIA)[A-Z0-9]{16}\b"), "[key]"),
    (re.compile(r"\b(sk|pk|rk|ghp|gho|ghs|github_pat|xox[abpr]|AIza)[-_A-Za-z0-9]{16,}"), "[key]"),
    (re.compile(r"(?i)\b(api[_-]?key|token|secret|password|passwd|pwd|bearer|auth)\b\s*[:=]\s*\S+"), r"\1=[secret]"),
    (re.compile(r"\b[A-Za-z0-9+/_-]{32,}={0,2}"), "[token]"),
    # Contact details and identifiers.
    (re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), "[email]"),
    (re.compile(r"https?://\S+|www\.\S+"), "[url]"),
    (re.compile(r"(?<![\w@])@[A-Za-z0-9_]{2,30}\b"), "[handle]"),
    (re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"), "[ip]"),
    (re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b"), "[id]"),
    (re.compile(r"\b[A-Z]{2}\d{2}(?: ?[A-Z0-9]{4}){3,7}(?: ?[A-Z0-9]{1,3})?\b"), "[iban]"),
    (re.compile(r"\b\d(?:[ -]?\d){12,18}\b"), "[card]"),
    (re.compile(r"\b\d{2}-\d{2}-\d{2}\b"), "[sort-code]"),
    (re.compile(r"\b[A-CEGHJ-PR-TW-Z]{2}\s?\d{2}\s?\d{2}\s?\d{2}\s?[A-D]\b"), "[ni-number]"),
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "[ssn]"),
    (re.compile(r"\+?\d[\d ()-]{9,}\d"), "[phone]"),
    (re.compile(r"\b[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}\b"), "[postcode]"),
    (re.compile(r"\b\d{1,4}\s+[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\s(?:Street|St|Road|Rd|Avenue|Ave|Lane|Ln|Close|Way|Drive|Place|Square|Terrace|Gardens|Grove|Mews|Court)\b"), "[address]"),
    # Usernames inside file paths.
    (re.compile(r"(/Users/|/home/|C:\\Users\\)[^/\\\s]+"), r"\1[user]"),
]

# Messages that mention any of these are dropped whole, not redacted.
SENSITIVE = re.compile(
    r"(?i)\b(passport|diagnos\w*|prescription|therapist|therapy|medication|pregnan\w*|"
    r"bank account|sort code|account number|credit card|mortgage|debt|overdraft|"
    r"divorce|lawsuit|arrest\w*|salary|password|login details|date of birth|"
    r"national insurance|social security|nhs number)\b")


COMMON = {"I", "I'm", "I've", "I'll", "I'd", "Monday", "Tuesday", "Wednesday", "Thursday",
          "Friday", "Saturday", "Sunday", "January", "February", "March", "April", "May",
          "June", "July", "August", "September", "October", "November", "December",
          "English", "British", "American", "European"}
MID_SENTENCE_CAP = re.compile(r"(?<=[a-z0-9,;:)] )([A-Z][a-z]+(?:'s)?)\b")


def clean(text):
    text = re.sub(r"<system-reminder>.*?</system-reminder>", "", text, flags=re.S)
    text = re.sub(r"<pasted_content[^>]*>.*?</pasted_content[^>]*>", "[paste]", text, flags=re.S)
    text = text.strip()
    for pattern, label in REDACT:
        text = pattern.sub(label, text)
    return text


def find_names(rows):
    """Every capitalised word used mid-sentence: people, places, companies."""
    import collections
    capital, lower = collections.Counter(), collections.Counter()
    for r in rows:
        lower.update(re.findall(r"\b[a-z]+\b", r["text"]))
        for m in MID_SENTENCE_CAP.finditer(r["text"]):
            capital[m.group(1).removesuffix("'s")] += 1
    # A word written in lowercase at least twice as often is an ordinary word
    # ("Note: The plan" must not hide every "The").
    return {w for w, c in capital.items()
            if w not in COMMON and lower[w.lower()] < 2 * c}


def hide_names(rows, names):
    if not names:
        return
    pattern = re.compile(r"\b(" + "|".join(re.escape(n) for n in sorted(names, key=len, reverse=True)) + r")\b")
    for r in rows:
        r["text"] = pattern.sub("[name]", r["text"])


def text_of(content, kinds=("text", "input_text")):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        if any(isinstance(b, dict) and b.get("type") == "tool_result" for b in content):
            return ""
        return " ".join(b.get("text", "") for b in content
                        if isinstance(b, dict) and b.get("type") in kinds)
    return ""


def claude_code(_path):
    for f in glob.glob(os.path.expanduser("~/.claude/projects/**/*.jsonl"), recursive=True):
        if "/subagents/" in f:
            continue
        for line in open(f, errors="ignore"):
            try:
                d = json.loads(line)
            except ValueError:
                continue
            if d.get("type") != "user" or d.get("isSidechain") or d.get("isMeta"):
                continue
            yield d.get("timestamp", "")[:10], text_of(d.get("message", {}).get("content"))


def codex(_path):
    for f in glob.glob(os.path.expanduser("~/.codex/sessions/**/*.jsonl"), recursive=True):
        for line in open(f, errors="ignore"):
            try:
                d = json.loads(line)
            except ValueError:
                continue
            p = d.get("payload", {})
            if d.get("type") == "response_item" and p.get("type") == "message" and p.get("role") == "user":
                yield d.get("timestamp", "")[:10], text_of(p.get("content"))


def chatgpt(path):
    import datetime
    for conv in json.load(open(path)):
        for node in conv.get("mapping", {}).values():
            m = node.get("message") or {}
            if (m.get("author") or {}).get("role") != "user":
                continue
            parts = (m.get("content") or {}).get("parts") or []
            ts = m.get("create_time")
            date = datetime.date.fromtimestamp(ts).isoformat() if ts else ""
            yield date, " ".join(p for p in parts if isinstance(p, str))


def samples(path):
    for block in re.split(r"\n\s*\n", open(path).read()):
        yield "", block


SOURCES = {"claude-code": claude_code, "codex": codex, "chatgpt": chatgpt, "samples": samples}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--source", required=True, choices=SOURCES)
    ap.add_argument("--path", help="file for chatgpt or samples")
    ap.add_argument("--since", default="")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.source in ("chatgpt", "samples") and not a.path:
        sys.exit(f"--source {a.source} needs --path")

    seen, rows, dropped = set(), [], 0
    for date, raw in SOURCES[a.source](a.path):
        raw = raw or ""
        if SENSITIVE.search(raw):
            dropped += 1
            continue
        text = clean(raw)
        if len(text) < 12 or len(text) > MAX_CHARS or text.startswith(SKIP_PREFIXES):
            continue
        if a.since and date and date < a.since:
            continue
        key = text[:200]
        if key in seen:
            continue
        seen.add(key)
        rows.append({"t": date, "source": a.source, "text": text})

    rows.sort(key=lambda r: r["t"])
    hide_names(rows, find_names(rows))
    out = os.path.expanduser(a.out)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    mode = "a" if os.path.exists(out) else "w"
    with open(out, mode) as o:
        for r in rows:
            o.write(json.dumps(r) + "\n")
    words = sum(len(r["text"].split()) for r in rows)
    print(f"{len(rows)} messages, {words} words from {a.source} -> {out}")
    print(f"{dropped} messages dropped as sensitive." if dropped else "No messages dropped as sensitive.")


if __name__ == "__main__":
    main()
