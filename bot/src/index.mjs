import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import OpenAI from "openai";
import {
  MatrixClient,
  RustSdkCryptoStorageProvider,
  SimpleFsStorageProvider,
} from "matrix-bot-sdk";
import { StoreType } from "@matrix-org/matrix-sdk-crypto-nodejs";

process.umask(0o077);

const required = [
  "MATRIX_HOMESERVER_URL",
  "MATRIX_BOT_ACCESS_TOKEN",
  "MATRIX_ALLOWED_ROOM_IDS",
  "OPENAI_API_KEY",
  "OPENAI_MODEL",
];
const missing = required.filter((name) => !process.env[name]?.trim());
if (missing.length) {
  throw new Error(`Missing required environment settings: ${missing.join(", ")}`);
}

const dataDir = path.resolve(process.env.METHEUS_BOT_DATA_DIR || "./data");
fs.mkdirSync(dataDir, { recursive: true, mode: 0o700 });
fs.chmodSync(dataDir, 0o700);
const allowedRooms = new Set(
  process.env.MATRIX_ALLOWED_ROOM_IDS.split(",").map((value) => value.trim()).filter(Boolean),
);
if (allowedRooms.size === 0) {
  throw new Error("MATRIX_ALLOWED_ROOM_IDS must contain at least one room ID.");
}
const model = process.env.OPENAI_MODEL.trim();
const botToken = process.env.MATRIX_BOT_ACCESS_TOKEN.trim();
const consentPath = path.join(dataDir, "room-consent.json");
const matrixStore = new SimpleFsStorageProvider(path.join(dataDir, "matrix-state.json"));
const cryptoStore = new RustSdkCryptoStorageProvider(
  path.join(dataDir, "matrix-crypto"),
  StoreType.Sqlite,
);
const matrix = new MatrixClient(
  process.env.MATRIX_HOMESERVER_URL.trim(),
  botToken,
  matrixStore,
  cryptoStore,
);
const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

const consentState = loadConsentState();
const roomSessions = new Map();
const maxContextMessages = 12;
const maxMessageChars = 2_000;
const maxOutputTokens = 700;
const inFlightRooms = new Set();
const lastRequestAt = new Map();

const systemInstructions = `You are Metheus, a transparent AI reflection companion in a shared Matrix room. You are a software tool, not a person, clinician, therapist, mediator, or relationship judge. Help participants notice perspectives, ask non-coercive questions, and distinguish symbolic Human Design language from reported experience and established science. Never claim Human Design predicts, measures, or causes a biological or psychological state. Do not diagnose, prescribe, or infer anyone's consent, feelings, hormones, or motives. Do not take sides or treat one participant's account as the whole relationship. For health questions, offer general information with uncertainty and encourage a qualified professional for personal decisions. If someone describes immediate danger or intent to harm, prioritize immediate local emergency support and trusted human help. Keep replies concise, respectful, and useful to the whole room.`;

const privacyDisclosure = `Metheus AI is optional. If every currently joined person in this room opts in, only messages sent with “!metheus ask …” and the recent in-memory Metheus exchange will be sent to the configured OpenAI API to produce a reply. Ordinary room chat is not forwarded. The bot does not save chat text to its own disk; its short context buffer is memory-only and is cleared when anyone joins/leaves or opts out. The bot host stores per-room opt-in status and the current room-member list, but not chat text. The Matrix room itself and its server follow their own history and retention settings. OpenAI API requests use store:false, which disables Responses API application-state storage; it does not by itself guarantee zero retention. OpenAI's API data controls describe default abuse-monitoring retention of up to 30 days, subject to account settings and exceptions. Review the provider's current data terms before sharing sensitive, medical, reproductive, child, or intimate information. Do not use this prototype for emergencies.`;

function loadConsentState() {
  try {
    const parsed = JSON.parse(fs.readFileSync(consentPath, "utf8"));
    return parsed && typeof parsed === "object" && !Array.isArray(parsed) ? parsed : {};
  } catch (error) {
    if (error?.code === "ENOENT") return {};
    throw new Error("Could not read the bot's consent state; refusing to start.");
  }
}

function saveConsentState() {
  const temp = `${consentPath}.tmp`;
  fs.writeFileSync(temp, `${JSON.stringify(consentState, null, 2)}\n`, { mode: 0o600 });
  fs.chmodSync(temp, 0o600);
  fs.renameSync(temp, consentPath);
  fs.chmodSync(consentPath, 0o600);
}

function roomConsent(roomId) {
  if (!consentState[roomId]) consentState[roomId] = { informed: [], optedIn: [], memberSignature: null };
  const entry = consentState[roomId];
  if (!Array.isArray(entry.informed)) entry.informed = [];
  if (!Array.isArray(entry.optedIn)) entry.optedIn = [];
  return entry;
}

async function currentJoinedMembers(roomId) {
  const state = await matrix.getRoomState(roomId);
  const ownId = await matrix.getUserId();
  const current = state
    .filter((event) => event?.type === "m.room.member" && event?.content?.membership === "join")
    .filter((event) => typeof event.state_key === "string" && event.state_key !== ownId)
    .map((event) => ({ userId: event.state_key, membershipEventId: event.event_id || "unknown-event" }))
    .sort((left, right) => left.userId.localeCompare(right.userId));
  return { members: [...new Set(current.map((event) => event.userId))], signature: JSON.stringify(current) };
}

async function refreshRoomConsent(roomId) {
  const { members, signature } = await currentJoinedMembers(roomId);
  const consent = roomConsent(roomId);
  if (consent.memberSignature !== signature) {
    consent.memberSignature = signature;
    consent.informed = [];
    consent.optedIn = [];
    roomSessions.delete(roomId);
    saveConsentState();
    return { members, changed: true };
  }
  return { members, changed: false };
}

function hasOptedIn(consent, members) {
  const optedIn = new Set(consent.optedIn);
  return members.length > 0 && members.every((member) => optedIn.has(member));
}

function parseCommand(text) {
  const match = /^!metheus(?:\s+([a-z-]+))?(?:\s+([\s\S]*))?$/i.exec(text.trim());
  if (!match) return null;
  return { name: (match[1] || "help").toLowerCase(), argument: (match[2] || "").trim() };
}

async function sendNotice(roomId, text) {
  await matrix.sendMessage(roomId, { msgtype: "m.notice", body: text });
}

async function processCommand(roomId, sender, command, members, consent) {
  switch (command.name) {
    case "help":
      await sendNotice(roomId, "Metheus commands: !metheus ai-info, !metheus ai-status, !metheus ai-opt-in, !metheus ai-opt-out, and (after every joined member opts in) !metheus ask <your question>. Ordinary room messages are never sent to the AI.");
      return;
    case "ai-status": {
      if (!members.includes(sender)) return;
      const memberSet = new Set(members);
      const informedCount = new Set(consent.informed.filter((userId) => memberSet.has(userId))).size;
      const optedInCount = new Set(consent.optedIn.filter((userId) => memberSet.has(userId))).size;
      const active = hasOptedIn(consent, members);
      await sendNotice(roomId, members.length === 0
        ? "Metheus AI is inactive. No other participants are currently joined."
        : `Metheus AI is ${active ? "active for explicit !metheus ask messages" : "inactive"}. ${informedCount} of ${members.length} currently joined participants have read the disclosure; ${optedInCount} of ${members.length} have opted in. Individual consent choices are not listed.`);
      return;
    }
    case "ai-info":
      if (!members.includes(sender)) return;
      consent.informed = [...new Set([...consent.informed, sender])].sort();
      saveConsentState();
      await sendNotice(roomId, privacyDisclosure);
      await sendNotice(roomId, "If you understand and agree to this room's optional AI processing, send !metheus ai-opt-in. Each currently joined person must opt in separately. Send !metheus ai-opt-out at any time to stop processing and clear the bot's context.");
      return;
    case "ai-opt-in":
      if (!members.includes(sender)) return;
      if (!consent.informed.includes(sender)) {
        await sendNotice(roomId, "Please read the disclosure first by sending !metheus ai-info. No room text has been sent to the AI.");
        return;
      }
      consent.optedIn = [...new Set([...consent.optedIn, sender])].sort();
      saveConsentState();
      roomSessions.delete(roomId);
      if (hasOptedIn(consent, members)) {
        await sendNotice(roomId, "Every currently joined person has opted in. Metheus AI is active for explicit !metheus ask messages. Its conversation context starts empty and is held only in memory.");
      } else {
        await sendNotice(roomId, "Your opt-in is recorded. Metheus will not process any room content until every currently joined person has independently opted in.");
      }
      return;
    case "ai-opt-out":
      consent.optedIn = consent.optedIn.filter((userId) => userId !== sender);
      consent.informed = consent.informed.filter((userId) => userId !== sender);
      saveConsentState();
      roomSessions.delete(roomId);
      await sendNotice(roomId, "AI processing is paused for this room, and Metheus's in-memory context has been cleared. A request already sent to the provider cannot be recalled. To resume, every currently joined person must read the disclosure and opt in again.");
      return;
    case "ask":
      if (!command.argument) {
        await sendNotice(roomId, "Add a question after the command: !metheus ask <your question>");
        return;
      }
      if (!hasOptedIn(consent, members)) {
        await sendNotice(roomId, "Metheus AI is inactive. Every currently joined person must read !metheus ai-info and opt in before any message is sent to the AI.");
        return;
      }
      await answerQuestion(roomId, command.argument, members, consent);
      return;
    default:
      await sendNotice(roomId, "I don't recognize that command. Send !metheus help for the available commands.");
  }
}

async function answerQuestion(roomId, question, members, consent) {
  if (question.length > maxMessageChars) {
    await sendNotice(roomId, `Please keep each Metheus question under ${maxMessageChars} characters.`);
    return;
  }
  if (inFlightRooms.has(roomId)) {
    await sendNotice(roomId, "Metheus is already working on a question for this room. Please wait for that reply.");
    return;
  }
  const now = Date.now();
  if (now - (lastRequestAt.get(roomId) || 0) < 8_000) {
    await sendNotice(roomId, "Please wait a few seconds before sending another Metheus question.");
    return;
  }
  inFlightRooms.add(roomId);
  const session = roomSessions.get(roomId) || [];
  const nextInput = [
    ...session,
    { role: "user", content: `A room participant asks: ${question}` },
  ];
  try {
    const response = await openai.responses.create({
      model,
      instructions: systemInstructions,
      input: nextInput,
      store: false,
      max_output_tokens: maxOutputTokens,
    });
    const answer = response.output_text?.trim();
    if (!answer) throw new Error("The model returned no text.");
    const latestMembership = await currentJoinedMembers(roomId);
    if (
      latestMembership.signature !== consent.memberSignature
      || !hasOptedIn(consent, latestMembership.members)
    ) {
      await refreshRoomConsent(roomId);
      roomSessions.delete(roomId);
      return;
    }
    const visibleAnswer = answer.slice(0, maxMessageChars);
    await sendNotice(roomId, visibleAnswer);
    roomSessions.set(roomId, [
      ...nextInput,
      { role: "assistant", content: visibleAnswer },
    ].slice(-maxContextMessages));
  } catch {
    // Do not log the prompt, response, or provider error payload.
    await sendNotice(roomId, "Metheus could not get an AI response just now. Your question was not saved by the bot; please try again later.");
  } finally {
    inFlightRooms.delete(roomId);
    lastRequestAt.set(roomId, Date.now());
  }
}

matrix.on("room.message", async (roomId, event) => {
  try {
    if (!allowedRooms.has(roomId)) return;
    const sender = event?.sender;
    const content = event?.content;
    if (typeof sender !== "string" || !content || content.msgtype !== "m.text" || typeof content.body !== "string") return;
    if (sender === await matrix.getUserId()) return;

    if (!await matrix.crypto.isRoomEncrypted(roomId)) {
      await sendNotice(roomId, "Metheus AI is disabled here because this room is not encrypted. No message was sent to the AI.");
      return;
    }

    const { members } = await refreshRoomConsent(roomId);
    const consent = roomConsent(roomId);
    const command = parseCommand(content.body);
    if (!command) return;
    await processCommand(roomId, sender, command, members, consent);
  } catch {
    // Intentionally omit event bodies, user IDs, and provider payloads from logs.
  }
});

matrix.on("room.failed_decryption", async () => {
  // No plaintext is available; keep the bot silent and fail closed.
});

matrix.on("room.invite", async (roomId) => {
  if (!allowedRooms.has(roomId)) return;
  try {
    await matrix.joinRoom(roomId);
    await matrix.crypto.prepare([roomId]);
  } catch {
    // No room content is read or forwarded if joining or crypto initialization fails.
  }
});

async function start() {
  const ownUserId = await matrix.getUserId();
  if (!ownUserId) throw new Error("The configured Matrix access token is not associated with a bot user.");
  for (const roomId of allowedRooms) {
    try {
      await matrix.joinRoom(roomId);
    } catch {
      // It may already be joined. The first sync will confirm room access.
    }
  }
  const joinedRooms = await matrix.getJoinedRooms();
  await matrix.crypto.prepare(joinedRooms.filter((roomId) => allowedRooms.has(roomId)));
  await matrix.start();
}

start().catch((error) => {
  // Keep operational diagnostics free of credentials and message content.
  process.stderr.write(`Metheus Matrix bot failed to start: ${error?.message || "unknown startup error"}\n`);
  process.exitCode = 1;
});
