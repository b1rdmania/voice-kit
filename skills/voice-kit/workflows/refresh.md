# Refresh

Update the guide with what the person has written since the last build. Run it every few months, or when drafts start to sound off.

For hosted sessions, follow `references/storage.md`: use the uploaded guide and new samples; skip extraction, splitting and corpus merging when scripts or the previous corpus are unavailable. Deliver the updated guide for download or copying.

1. Read the date in `<voice-dir>/.build`, or the build date recorded in the supplied guide.
2. Run `scripts/extract.py` for each source with `--since <that date>` into a fresh file, `<voice-dir>/corpus-new.jsonl`; do not reuse a previous refresh file.
3. Split and analyse it as in `build.md`, steps 2 and 3. Give the analysis the current guide so it reports what changed.
4. Update the guide. Add only standing corrections to "Hard bans", scoped to their supported format; put one-off edits in "Tendencies". Move words to "Retired" only with evidence of a changed preference, not merely absence from a small sample. Add new FINAL drafts to the examples.
5. Run the blind test from `build.md`, step 6.
6. Append `corpus-new.jsonl` to `corpus.jsonl` and update `.build`.
