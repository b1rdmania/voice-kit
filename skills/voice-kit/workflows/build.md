# Build

Build `<voice-dir>/guide.md` from what the person has already written to their AI tools.

## 1. Pick the sources

Use the source and storage route in `references/storage.md`. For file-based extraction, run `scripts/extract.py` once per source. Every run appends to the same corpus. Substitute `<voice-dir>` with the chosen absolute path and quote paths containing spaces; angle-bracket names below are placeholders. Start a new build with a fresh corpus file so retries do not duplicate earlier extraction.

| Source | Command |
| --- | --- |
| Claude Code | `python3 scripts/extract.py --source claude-code --out <voice-dir>/corpus.jsonl` |
| Codex | `python3 scripts/extract.py --source codex --out <voice-dir>/corpus.jsonl` |
| ChatGPT export | `python3 scripts/extract.py --source chatgpt --path <conversations.json> --out <voice-dir>/corpus.jsonl` |
| Posts or emails they paste or point to | `python3 scripts/extract.py --source samples --path <file> --out <voice-dir>/corpus.jsonl` |

Redaction is best effort. Offer inspection of the cleaned corpus before analysis without requiring a review step. In hosted sessions, use only the uploaded export or samples commands, with their actual paths.

If scripts are unavailable, analyse supplied readable samples directly and skip splitting. Do not ask again for samples already supplied.

Aim for 20,000 words or more. Under 5,000 words, label the guide provisional; offer more samples without blocking a useful first guide.

## 2. Split

Run `python3 scripts/split.py <voice-dir>/corpus.jsonl`. It writes chunks of about 60,000 words.

## 3. Analyse

For each chunk, run `prompts/analysis.md` against it. Use one subagent per chunk on a cheaper model when the host supports subagents. Otherwise analyse the chunks one at a time. Collect the findings as text.

## 4. Approved examples

Ask once whether they have posts or messages they were happy with. If they share any, save each to `<voice-dir>/drafts/` marked FINAL. If not, skip this step. Drafts they approve later fill the gap.

## 5. Write the guide

Copy `templates/voice-guide.md` to `<voice-dir>/guide.md`. Fill every section from the findings and the approved examples.

- Every hard ban must come from a standing correction: a general rule the person stated, or the same correction on two or more drafts. Scope it to the format and context supported by the evidence. Quote it. One-off edits go under "Tendencies".
- Every "keep anyway" item must show up in their own writing.
- Leave a section empty, with a note, rather than invent it.

## 6. Blind test

Pick two approved examples, or two of their own longer messages if there are none. Give a fresh subagent only the guide, `workflows/write.md` and a one-line summary of what each example says. Ask it to draft both. If subagents are unavailable, make a self-check draft and label it as such rather than calling it a blind test. Show the person the drafts next to the originals. Fix the guide where the drafts miss.

Write today's date and the sources to `<voice-dir>/.build`.

Deliver the guide using `references/storage.md`. Without filesystem tools, record the build date and sources in the guide itself.
