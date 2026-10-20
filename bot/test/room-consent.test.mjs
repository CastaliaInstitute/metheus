import assert from "node:assert/strict";
import test from "node:test";
import { hasRoomWideOptIn, mayDeliverRoomResponse } from "../src/room-consent.mjs";

test("room-wide AI stays off for an empty room or one missing opt-in", () => {
  assert.equal(hasRoomWideOptIn({ optedIn: ["a"] }, []), false);
  assert.equal(hasRoomWideOptIn({ optedIn: ["a"] }, ["a", "b"]), false);
  assert.equal(hasRoomWideOptIn({ optedIn: ["a", "b"] }, ["a", "b"]), true);
});

test("response is suppressed when membership changes during model processing", () => {
  assert.equal(mayDeliverRoomResponse({
    startingSignature: "members-a-b",
    currentSignature: "members-a-b-c",
    startingRevision: 4,
    currentRevision: 5,
    consent: { optedIn: ["a", "b", "c"] },
    members: ["a", "b", "c"],
  }), false);
});

test("response is suppressed after any consent revision, even if everyone opts in again", () => {
  assert.equal(mayDeliverRoomResponse({
    startingSignature: "members-a-b",
    currentSignature: "members-a-b",
    startingRevision: 8,
    currentRevision: 10,
    consent: { optedIn: ["a", "b"] },
    members: ["a", "b"],
  }), false);
});

test("response is delivered only for unchanged membership, consent, and unanimous opt-in", () => {
  assert.equal(mayDeliverRoomResponse({
    startingSignature: "members-a-b",
    currentSignature: "members-a-b",
    startingRevision: 8,
    currentRevision: 8,
    consent: { optedIn: ["a", "b"] },
    members: ["a", "b"],
  }), true);
});
