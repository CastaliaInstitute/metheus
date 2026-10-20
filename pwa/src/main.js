import './style.css';

const $ = (selector) => document.querySelector(selector);
const connectForm = $('#connect-form');
const connectPanel = $('#connection-panel');
const conversation = $('#conversation');
const settingsPanel = $('#settings-panel');
const timeline = $('#timeline');
const statusLine = $('#connect-status');
const syncIndicator = $('#sync-indicator');
const messageForm = $('#message-form');
const messageInput = $('#message-input');
const session = { client: null, sdk: null, userId: null, roomId: null, encrypted: false, seen: new Set() };
let deferredInstall = null;

window.addEventListener('beforeinstallprompt', (event) => {
  event.preventDefault();
  deferredInstall = event;
  $('#install-button').hidden = false;
});
$('#install-button').addEventListener('click', async () => {
  if (!deferredInstall) return;
  deferredInstall.prompt();
  await deferredInstall.userChoice;
  deferredInstall = null;
  $('#install-button').hidden = true;
});

if ('serviceWorker' in navigator) navigator.serviceWorker.register('/chat/sw.js', { scope: '/chat/' }).catch(() => {});

$('#settings-toggle').addEventListener('click', () => {
  conversation.hidden = !conversation.hidden;
  settingsPanel.hidden = !settingsPanel.hidden;
});
$('#back-to-chat').addEventListener('click', () => {
  settingsPanel.hidden = true;
  conversation.hidden = false;
});

function setStatus(message, isError = false) {
  statusLine.textContent = message;
  statusLine.classList.toggle('error', isError);
}

function safeText(parent, tag, text, className) {
  const element = document.createElement(tag);
  element.textContent = text;
  if (className) element.className = className;
  parent.append(element);
  return element;
}

function displayEvent(event) {
  if (!event || event.getType() !== 'm.room.message') return;
  const content = event.getContent();
  if (content?.msgtype !== 'm.text' || typeof content.body !== 'string') return;
  const id = event.getId() || `${event.getSender()}-${event.getTs()}-${content.body}`;
  if (session.seen.has(id)) return;
  session.seen.add(id);
  $('#welcome-card').hidden = true;
  const mine = event.getSender() === session.userId;
  const article = document.createElement('article');
  article.className = `message ${mine ? 'message-mine' : ''}`;
  safeText(article, 'p', event.sender?.name || event.getSender(), 'message-sender');
  safeText(article, 'p', content.body, 'message-body');
  safeText(article, 'time', new Date(event.getTs()).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' }), 'message-time');
  timeline.append(article);
  timeline.scrollTop = timeline.scrollHeight;
}

function getPlainBody(error) {
  const message = error?.message || 'The Matrix server could not complete this request.';
  return message.replace(/https?:\/\/\S+/g, 'server endpoint').slice(0, 240);
}

function onceSyncReady(client) {
  return new Promise((resolve, reject) => {
    const timeout = window.setTimeout(() => reject(new Error('The homeserver did not finish syncing in time.')), 30000);
    const onSync = (state, _previous, data) => {
      if (state === 'PREPARED' || state === 'SYNCING') {
        clearTimeout(timeout);
        client.removeListener(sdk.ClientEvent.Sync, onSync);
        resolve(data);
      }
    };
    client.on(sdk.ClientEvent.Sync, onSync);
  });
}

connectForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const data = new FormData(connectForm);
  const baseUrl = String(data.get('homeserver')).trim().replace(/\/$/, '');
  const roomInput = String(data.get('room')).trim();
  const user = String(data.get('user')).trim();
  const password = String(data.get('password'));
  const submit = connectForm.querySelector('button[type="submit"]');
  submit.disabled = true;
  setStatus('Signing in and preparing Matrix encryption support in this browser…');
  try {
    const homeserver = new URL(baseUrl);
    if (homeserver.protocol !== 'https:' && !['localhost', '127.0.0.1'].includes(homeserver.hostname)) {
      throw new Error('Use an HTTPS Matrix homeserver. HTTP is allowed only for local development.');
    }
    const sdk = await import('matrix-js-sdk');
    session.sdk = sdk;
    const loginClient = sdk.createClient({ baseUrl });
    const login = await loginClient.login('m.login.password', { user, password, initial_device_display_name: 'Metheus Circle PWA' });
    // Drop the password input immediately after the login request resolves.
    connectForm.elements.password.value = '';
    const client = sdk.createClient({ baseUrl, accessToken: login.access_token, userId: login.user_id, deviceId: login.device_id, timelineSupport: true });
    await client.initRustCrypto();
    session.client = client;
    session.userId = login.user_id;
    session.roomId = roomInput;
    client.on(sdk.RoomEvent.Timeline, (matrixEvent, room) => {
      if (!room || room.roomId !== session.roomId) return;
      matrixEvent.once('Event.decrypted', () => displayEvent(matrixEvent));
      displayEvent(matrixEvent);
    });
    const ready = onceSyncReady(client);
    client.startClient({ initialSyncLimit: 30 });
    await ready;
    let room = client.getRoom(roomInput);
    if (!room) {
      const joined = await client.joinRoom(roomInput);
      room = joined;
      session.roomId = joined.roomId;
    }
    if (!room) throw new Error('The room is not available to this Matrix account. Check the room ID or ask its admin to invite you.');
    const cryptoApi = client.getCrypto();
    session.encrypted = cryptoApi ? await cryptoApi.isEncryptionEnabledInRoom(room.roomId) : false;
    const liveEvents = room.getLiveTimeline()?.getEvents?.() || [];
    liveEvents.forEach(displayEvent);
    $('#room-title').textContent = room.name || 'The Hearth';
    $('#room-subtitle').textContent = `${room.getJoinedMembers().length} people in this room · ${session.encrypted ? 'end-to-end encryption on' : 'encryption off — sending disabled'}`;
    messageInput.disabled = !session.encrypted;
    messageInput.placeholder = session.encrypted ? 'Write a message to your room…' : 'Sending is disabled until this room is end-to-end encrypted.';
    messageForm.querySelector('button').disabled = !session.encrypted;
    $('.composer-note').textContent = session.encrypted
      ? 'The Metheus bot must be joined to this room to reply. Messages are shared with the whole room.'
      : 'This room is not end-to-end encrypted. Sending is disabled in this prototype.';
    $('#session-details').replaceChildren();
    [['Account', login.user_id], ['Room', room.roomId], ['Homeserver', baseUrl], ['Encryption', session.encrypted ? 'Matrix reports end-to-end encryption is enabled for this room.' : 'Not enabled. Sending is disabled.']].forEach(([term, value]) => {
      safeText($('#session-details'), 'dt', term);
      safeText($('#session-details'), 'dd', value);
    });
    connectPanel.hidden = true;
    conversation.hidden = false;
    $('#settings-toggle').hidden = false;
    $('#logout-button').hidden = false;
    $('#install-button').hidden = false;
    syncIndicator.textContent = 'Connected to Matrix';
    client.on(sdk.ClientEvent.Sync, (state) => {
      if (state === 'SYNCING' || state === 'PREPARED') syncIndicator.textContent = 'Live · Matrix';
      else if (state === 'ERROR') syncIndicator.textContent = 'Reconnecting…';
    });
  } catch (error) {
    connectForm.elements.password.value = '';
    const client = session.client;
    session.client = null;
    if (client) client.stopClient();
    setStatus(getPlainBody(error), true);
  } finally {
    submit.disabled = false;
  }
});

messageForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const body = messageInput.value.trim();
  if (!body || !session.client || !session.roomId || !session.encrypted) return;
  const submit = messageForm.querySelector('button');
  submit.disabled = true;
  try {
    await session.client.sendTextMessage(session.roomId, body);
    messageInput.value = '';
    messageInput.style.height = 'auto';
  } catch (error) {
    syncIndicator.textContent = `Message not sent · ${getPlainBody(error)}`;
  } finally {
    submit.disabled = false;
    messageInput.focus();
  }
});

messageInput.addEventListener('input', () => {
  messageInput.style.height = 'auto';
  messageInput.style.height = `${Math.min(messageInput.scrollHeight, 160)}px`;
});
messageInput.addEventListener('keydown', (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    messageForm.requestSubmit();
  }
});

$('#logout-button').addEventListener('click', async () => {
  const client = session.client;
  if (client) {
    client.stopClient();
    try { await client.logout(); } catch { /* local disconnect still proceeds */ }
  }
  session.client = null;
  session.sdk = null;
  session.userId = null;
  session.roomId = null;
  session.encrypted = false;
  session.seen.clear();
  timeline.querySelectorAll('.message').forEach((message) => message.remove());
  $('#welcome-card').hidden = false;
  connectForm.reset();
  connectForm.elements.homeserver.value = 'https://matrix.org';
  conversation.hidden = true;
  settingsPanel.hidden = true;
  connectPanel.hidden = false;
  $('#logout-button').hidden = true;
  $('#settings-toggle').hidden = true;
  messageInput.disabled = false;
  messageForm.querySelector('button').disabled = false;
  messageInput.placeholder = 'Write a message to your room…';
  $('.composer-note').textContent = 'The Metheus bot must be joined to this room to reply. Messages are shared with the whole room.';
  syncIndicator.textContent = 'Disconnected';
  setStatus('Disconnected. Matrix SDK encryption keys may remain in this browser’s local SDK store.');
});
