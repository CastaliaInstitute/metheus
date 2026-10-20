# Metheus Matrix AI bot

This is the server-side companion for the static client in [`/chat/`](../docs/matrix-chat-pwa.md). It joins only explicitly allowlisted rooms, requires Matrix end-to-end encryption, and responds only to explicit `!metheus ask …` commands.

## Shared-room consent gate

Before any AI request, every currently joined person other than the bot must:

1. Send `!metheus ai-info` and receive the disclosure in the room.
2. Send `!metheus ai-opt-in`.
3. Use `!metheus ai-status` to see aggregate informed/opt-in counts and whether explicit AI questions are active; individual choices are not listed.

Ordinary room messages are never forwarded. The bot keeps a short conversation context in memory only. It clears that context when any room member joins or leaves, when any participant opts out, and after a process restart. If membership changes while a model request is running, the bot discards the response. Any request already sent to the provider cannot be recalled. Membership changes are detected against the current room state before commands and after each model call.

`!metheus ai-opt-out` pauses the room immediately and clears in-memory context. The room must complete the disclosure/opt-in flow again to resume. The bot host stores per-room informed/opted-in Matrix user IDs and a membership signature in `room-consent.json`; this file contains no messages. Matrix sync state and encryption keys are stored separately in the configured data directory. Restrict the host, volume, backups, and operator access accordingly.

The model request uses the OpenAI Responses API with `store: false`, no `previous_response_id`, and a bounded in-memory exchange. This disables Responses API application-state storage but does not guarantee zero retention: provider abuse-monitoring controls and retention vary by account and may retain content. The room disclosure directs members to review the provider's current terms before sharing sensitive, health, child, reproductive, or intimate information. The bot does not claim that Matrix encryption hides content from the bot or the configured AI provider.

For an explicit `!metheus ask` that mentions a gate number, the bot adds matching entries from `catalog/gate-endocrine-correspondences.json` to that request; the room disclosure tells participants this may happen. These entries preserve source lineage and limitations so the model can describe a teaching as source-attributed; they are not passed as biological facts or used to infer a room member's physiology. If the catalog is missing, the bot continues without correspondence context and is instructed not to invent gate/hormone links. Set `METHEUS_CORRESPONDENCE_CATALOG` if the deployment keeps this catalog outside the repository's default relative path. This public catalog context is included only in explicit questions and is not written to the bot's disk.

The current Matrix Bot SDK dependency tree includes legacy `request`-family packages with unresolved moderate advisories. A compatible maintained request implementation is pinned by npm override to remove the critical/high advisories in the older package, but that does not substitute for dependency review or a security audit. This service is an integration prototype; do not deploy it with sensitive user data until those upstream dependencies and the full deployment have been reviewed.

## Configuration and run

Copy `.env.example` to a private deployment secret store; do not commit real values. Create a dedicated Matrix account, add it only to approved private rooms, enable encryption before inviting the bot, and set `MATRIX_ALLOWED_ROOM_IDS` to the exact room IDs. The bot must have a persistent, private data volume so its Matrix device and crypto state remain stable. Do not use a shared human account or reuse an access token in the browser.

```sh
cd bot
npm ci
node src/index.mjs
```

Required settings are `MATRIX_HOMESERVER_URL`, `MATRIX_BOT_ACCESS_TOKEN`, `MATRIX_ALLOWED_ROOM_IDS`, `OPENAI_API_KEY`, and `OPENAI_MODEL`. Model access depends on the configured OpenAI project. The bot uses the Matrix Bot SDK's Rust-backed SQLite crypto store and requires a supported Node.js runtime and platform binary. The deployment operator must verify the bot device and confirm the actual homeserver, provider, account retention settings, and room history policy before inviting participants.

## Current boundaries

The bot does not create rooms, manage human accounts, ingest Metheus profiles or chart data, read ordinary room history, provide device-verification/recovery UX, store transcripts, export/delete Matrix room history, moderate a family, or provide therapy, clinical care, or emergency response. Its Matrix crypto setup is an implementation component; this prototype has not received a security audit or operational deployment review. It must not be used for children's personal data or sensitive health/intimacy discussions until those reviews and the required product controls are complete.
