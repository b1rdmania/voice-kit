# Voice Kit privacy policy

Effective date: 5 October 2026.

Voice Kit is a writing and editing plugin published by b1rdmania. It builds an editable voice guide from writing you choose to supply, then helps draft posts, emails and messages in your style.

## Information used and why

The workflow processes your selected writing samples, messages, corrections, approved drafts and existing voice guide to learn your writing preferences and draft or edit text. When you choose history extraction, it also processes message dates, source labels and up to 300 characters of the preceding AI reply for context. These materials can contain personal information about you or other people.

Choose only material you are comfortable sharing with your AI provider. Do not supply passwords, access keys, payment card details, government identifiers, private health information or other sensitive material. You can use a small set of selected writing samples instead of a conversation export.

## Where processing happens and who receives information

Voice Kit has no publisher-operated backend, analytics, advertising, telemetry or user accounts. Its bundled scripts do not send data over the network. The publisher does not receive your writing, corpus, guides or drafts through normal plugin use and does not sell them or use them for advertising.

With local execution, the scripts read the sources you select and write files to a directory on your machine, normally `~/voice/`. The AI host you use reads material for analysis and drafting under that provider's privacy policy and your account settings. Local extraction does not mean offline AI analysis.

In hosted or web use, uploads, pasted text and generated files are processed and stored by your AI provider. Uploading a file shares it with that provider before Voice Kit can redact it. Installing Voice Kit does not automatically grant it access to your past ChatGPT conversations or your computer's files.

## Redaction

The extraction script uses patterns to drop some sensitive messages and redact some identifiers. This is best effort, not a guarantee of anonymity. Names, confidential work details and sensitive subjects can remain. You may inspect and edit the extracted corpus before analysis. When scripts cannot run, no automated extraction or redaction is performed.

## Retention and deletion

The publisher holds no copy of your writing from normal plugin use. Local corpora, chunks, guides, build records and drafts remain until you delete them; Voice Kit does not automatically expire those files. Deleting the plugin does not delete files saved separately. Your backups may retain additional copies.

Hosted chats, uploads and generated files follow your AI provider's retention policies and account controls. Voice Kit sets no separate retention period for those systems. Session files may be temporary, so save a guide you want to reuse. Delete downloads and use the host's chat and file deletion controls when you no longer need them.

## Your choices

You choose the sources and samples, can omit or remove passages, and can edit or delete the resulting guide and drafts. To reuse a guide in another chat, supply it yourself unless the host already provides access. Voice Kit does not publish your writing or share your corpus as part of its distribution package.

## Policy hosting and questions

GitHub hosts this public policy and processes visits and comments under its own privacy policy. For policy questions, leave a comment on this policy's GitHub Gist. Comments are public: do not include private writing, exports, credentials or other sensitive information. The publisher can see information you voluntarily put in a public comment.

This policy will be updated if the plugin's handling of information changes.
