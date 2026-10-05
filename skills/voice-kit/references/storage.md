# Storage and source access

Choose from capabilities actually available, not the product name.

## Local execution

When tools can access the person's machine, default to `~/voice/` (or their chosen directory). Ask which sources to use if they have not specified them. Read only those sources. Keep the guide, corpus, drafts and `.build` there, outside the plugin checkout.

## Hosted execution or web chat

A hosted filesystem is not the person's computer. Do not search `~/.claude` or `~/.codex` there for their history. Use an export or writing samples they supply, or a guide they upload. Do not imply that installation grants access to their ChatGPT history.

When Python and uploaded files are available, choose a writable session directory as `<voice-dir>` and run the bundled extractor against the supplied file. Files uploaded here are already shared with this AI provider before redaction. Describe redaction as best effort, not as a way to undo that upload.

Without execution tools, work directly from pasted or readable samples. Suggest 30–50 representative samples but accept fewer and label the guide provisional. Do not claim the extractor ran. Use the guide template and show the complete guide as copyable Markdown if downloadable files are unavailable.

## Save and reuse

Local sessions save to `<voice-dir>`. Hosted sessions should provide `guide.md` as a download, plus any approved drafts the person wants to reuse. Include the build date and source labels in the guide, without private source paths. Explain once that session files may not persist: save the guide and upload it in a later chat, along with relevant approved examples. Never promise memory across chats.

If a supplied guide references unavailable drafts, use the guide and available examples; ask for those drafts only if needed. For refresh, reuse the supplied guide and request only new samples or an export when no source is accessible. Return an updated guide. No download should bundle the corpus by default.
