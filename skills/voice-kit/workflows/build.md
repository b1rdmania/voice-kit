# Build

Build `~/voice/guide.md` from what the person has already written to their AI tools.

## 1. Pick the sources

Ask which they use, then run `scripts/extract.py` once per source. Every run appends to the same corpus.

| Source | Command |
| --- | --- |
| Claude Code | `python3 scripts/extract.py --source claude-code --out ~/voice/corpus.jsonl` |
| Codex | `python3 scripts/extract.py --source codex --out ~/voice/corpus.jsonl` |
| ChatGPT export | `python3 scripts/extract.py --source chatgpt --path <conversations.json> --out ~/voice/corpus.jsonl` |
| Posts or emails they paste or point to | `python3 scripts/extract.py --source samples --path <file> --out ~/voice/corpus.jsonl` |

If the host cannot run scripts, ask the person to paste 30 to 50 of their own messages or posts, and work from those.

Aim for 20,000 words or more. Under 5,000 words, say the guide will be thin and ask for more samples.

## 2. Split

Run `python3 scripts/split.py ~/voice/corpus.jsonl`. It writes chunks of about 60,000 words.

## 3. Analyse

For each chunk, run `prompts/analysis.md` against it. Use one subagent per chunk on a cheaper model when the host supports subagents. Otherwise analyse the chunks one at a time. Collect the findings as text.

## 4. Ask for approved examples

Ask the person for three to eight things they wrote and were happy with: posts, emails, messages. Save each to `~/voice/drafts/` marked FINAL.

## 5. Write the guide

Copy `templates/voice-guide.md` to `~/voice/guide.md`. Fill every section from the findings and the approved examples.

- Every hard ban must come from a correction the person actually gave. Quote it.
- Every "keep anyway" item must show up in their own writing.
- Leave a section empty, with a note, rather than invent it.

## 6. Blind test

Pick two approved examples. Give a fresh subagent only the guide, `workflows/write.md` and a one-line summary of what each example says. Ask it to draft both. Show the person its drafts next to the originals. Fix the guide where the drafts miss.

Write today's date and the sources to `~/voice/.build`.
