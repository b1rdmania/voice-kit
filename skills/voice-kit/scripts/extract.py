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
(messages over --max-chars) and duplicates. Redacts emails, phone numbers and
API keys. Writes one JSON object per line: {"t": date, "source": ..., "text": ...}.

The corpus is private. Keep it in ~/voice/ and never commit or share it.
"""

import argparse
import glob
import json
import os
import re
import sys

SKIP_PREFIXES = ("<", "Base directory for this skill", "[Request interrupted",
                 "Caveat:", "This session is being continued", "[SYSTEM")
REDACT = [
    (re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), "[email]"),
    (re.compile(r"\+?\d[\d ()-]{9,}\d"), "[phone]"),
    (re.compile(r"\b(sk|pk|rk|ghp|gho|xox[abp])[-_][A-Za-z0-9_-]{16,}"), "[key]"),
    (re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b"), "[id]"),
]


def clean(text):
    text = re.sub(r"<system-reminder>.*?</system-reminder>", "", text, flags=re.S)
    text = re.sub(r"<pasted_content[^>]*>.*?</pasted_content[^>]*>", "[paste]", text, flags=re.S)
    text = text.strip()
    for pattern, label in REDACT:
        text = pattern.sub(label, text)
    return text


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
    ap.add_argument("--max-chars", type=int, default=2500)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.source in ("chatgpt", "samples") and not a.path:
        sys.exit(f"--source {a.source} needs --path")

    seen, rows = set(), []
    for date, raw in SOURCES[a.source](a.path):
        text = clean(raw or "")
        if len(text) < 12 or len(text) > a.max_chars or text.startswith(SKIP_PREFIXES):
            continue
        if a.since and date and date < a.since:
            continue
        key = text[:200]
        if key in seen:
            continue
        seen.add(key)
        rows.append({"t": date, "source": a.source, "text": text})

    rows.sort(key=lambda r: r["t"])
    out = os.path.expanduser(a.out)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    mode = "a" if os.path.exists(out) else "w"
    with open(out, mode) as o:
        for r in rows:
            o.write(json.dumps(r) + "\n")
    words = sum(len(r["text"].split()) for r in rows)
    print(f"{len(rows)} messages, {words} words from {a.source} -> {out}")


if __name__ == "__main__":
    main()
