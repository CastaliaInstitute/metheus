# Metheus Circle: Matrix chat PWA

**Status:** static client prototype. It connects individual Matrix accounts to an existing room. The PWA does not host rooms, collect profiles, or provide the Metheus AI service.

## What it does

The installable client at `/chat/` signs a person into a Matrix homeserver, joins or opens a room ID/alias, displays room text messages, and sends a new text message. It uses `matrix-js-sdk` and initializes its Rust-backed crypto support. Each participant signs in with their own Matrix account; shared-room messages are visible to the room's members. Session tokens stay in client memory. Matrix SDK encryption state uses browser IndexedDB. The service worker caches only the application shell and static assets; it does not cache Matrix API responses or room messages. The app does not retain transcripts in its own storage. The client queries the SDK for the room's encryption setting and disables sending if Matrix reports encryption is off; it does not independently verify users' devices or the bot's key handling.

The PWA is a presentation and transport client. An independently operated Metheus Matrix bot must join the room and respond to messages for users to chat with Metheus AI. A prototype bot is now included in [`bot/`](../bot/README.md), but it is not deployed or connected to the Pages client. It requires a separately operated Node service, an allowlisted Matrix bot account, persistent private crypto storage, and a server-side OpenAI API key. The PWA has no model/API key or direct model connection.

The chat's optional **Metheus AI** panel sends the bot's `!metheus ai-info`, `!metheus ai-status`, `!metheus ai-opt-in`, and `!metheus ai-opt-out` commands as visible room messages. Participants must read the returned disclosure and opt in individually; the bot refuses to process `!metheus ask …` until every currently joined person is opted in. `!metheus ai-status` reports only aggregate counts of currently joined people who have read the disclosure or opted in, and whether explicit AI questions are active; it does not list individuals' choices. The panel can insert the explicit ask prefix into the composer. Ordinary messages are not forwarded to the AI by the bot. An opt-out clears the bot's in-memory context, but cannot recall a request already sent to the model provider.

## Three.js bodygraph reference

The chat places a Three.js/WebGL-rendered bodygraph beside the room timeline. It uses vector geometry from the shared Astrolabe Human Design bodygraph template, with its embedded scripts removed and all natal/transit activation values, personal status, and source-specific labels stripped. The reference has no participant chart data. Drag to orbit, scroll/pinch to zoom, click a gate/channel to highlight it, or enter a reference such as `Gate 34` or `Channel 34-20`. Gate/channel mentions in room messages are also highlighted when the diagram is open. The **Gate links** view overlays source-attributed gate correspondences from a separate catalog; selecting a marked gate shows the source and limits. These are attributed Human Design teachings, not proven biological relationships or an individual's physiology. The **Endocrine network** view displays a separate interactive candidate physiology graph, with domain filtering and node details; endocrine node positions are diagram layout, not anatomy, and the graph remains under review and internal only. Neither map calculates a chart or makes personal health inferences. Update the two JSON files in `pwa/public/` when their source catalogs change.

## Room setup required

1. Operate a Matrix homeserver or choose one that permits the intended use and provides HTTPS, account registration/sign-in, and browser access (CORS) for the deployed Metheus origin.
2. Create a private room for the intended participants. Decide who may invite members, whether room history is shared with new members, how long messages are retained, and how the room will be closed or deleted.
3. Enable Matrix end-to-end encryption for the room and verify that the bot account is designed to participate in encrypted rooms. Encryption at the Matrix transport layer alone is not end-to-end encryption.
4. Invite each adult participant and the Metheus bot. Give each person their own account; do not share passwords or access tokens.
5. Make the bot's role, AI provider, model processing, retention, and escalation limitations clear to all participants before they disclose personal information. The bot should not represent itself as a therapist, clinician, mediator, or relationship judge.
6. Open `/chat/`, enter homeserver, room ID/alias, and the user's own login. The PWA prompts Matrix to join the room if the account is not already a member.

The current client does not provide room creation/invites, participant-specific charts, device verification/recovery UX, user management, an independent consent-state dashboard, moderation, transcript export/deletion, or message pagination and file/media support. Its command buttons send visible Matrix messages; they do not verify participant devices or certify consent. The encryption check reports the room setting but does not verify participant devices, verify bot key handling, or certify the service. Treat it as an early client, not a secure health-data product. Before using it for reproductive, health, or intimate information, complete a security/privacy review, add trusted device verification and recovery flows, and establish an appropriate retention plan. Do not use it for children's personal data in this prototype.

## Build and deploy

The Pages workflow runs `npm ci --prefix pwa` and `npm run build --prefix pwa`, then publishes the repository root. The Vite build writes the static PWA to the ignored `chat/` directory. Local build: `npm ci --prefix pwa && npm run build --prefix pwa`.

The client is configured for the custom domain path `/chat/`. Its installable shell works offline after first load, but Matrix sign-in, room sync, encryption key fetches, and message exchange require network access. Do not treat the offline shell as offline chat.
