/** Room AI is enabled only for a non-empty room where every current member opted in. */
export function hasRoomWideOptIn(consent, members) {
  if (!Array.isArray(members) || members.length === 0 || !Array.isArray(consent?.optedIn)) return false;
  const optedIn = new Set(consent.optedIn);
  return members.every((member) => typeof member === "string" && optedIn.has(member));
}

/** A completed model response may be posted only if membership and consent still match. */
export function mayDeliverRoomResponse({
  startingSignature,
  currentSignature,
  startingRevision,
  currentRevision,
  consent,
  members,
}) {
  return typeof startingSignature === "string"
    && startingSignature === currentSignature
    && Number.isInteger(startingRevision)
    && startingRevision === currentRevision
    && hasRoomWideOptIn(consent, members);
}
