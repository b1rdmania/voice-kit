# Refresh

Update the guide with what the person has written since the last build. Run it every few months, or when drafts start to sound off.

1. Read the date in `~/voice/.build`.
2. Run `scripts/extract.py` for each source with `--since <that date>` into a new file, `~/voice/corpus-new.jsonl`.
3. Split and analyse it as in `build.md`, steps 2 and 3. Give the analysis the current guide so it reports what changed.
4. Update the guide. Add new corrections to "Hard bans". Move words the person stopped using to "Retired". Add new FINAL drafts to the examples.
5. Run the blind test from `build.md`, step 6.
6. Append `corpus-new.jsonl` to `corpus.jsonl` and update `.build`.
