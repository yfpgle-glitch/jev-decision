# Jev confirmation protocol

Use this protocol before an interactive Jev call.

1. Draft the smallest set of focused questions. Usually one question is enough.
2. Check that every question has one judgment target, a supported type, and only the context needed for that judgment.
3. Show the exact question and option labels in the host's native confirmation UI. Offer **Yes** and **No** only; use the free-text field for edits. Do not show the full `state`, source document, contact details, tool traces, or evidence ledger.
4. On **Yes**, call Jev with the displayed questions and compressed `state`. On **No**, stop without calling it.
5. If the host has no interactive UI, show the proposed questions and explain how the user can confirm in that host. A model-generated “yes” is not confirmation.

The UI may differ across Codex, Claude Code, and Command Code; these user-visible rules remain the same.
