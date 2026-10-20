import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { generateBodygraphInputPrompt } from "../../shared/bodygraph-prompt.mjs";

const rootDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const topology = JSON.parse(fs.readFileSync(path.join(rootDir, "catalog/human-design-bodygraph-topology.json"), "utf8"));
const affordances = JSON.parse(fs.readFileSync(path.join(rootDir, "catalog/gate-ai-affordances.json"), "utf8"));

test("generates readable gate activities and complete channels from a selected map", () => {
  const prompt = generateBodygraphInputPrompt({ userGates: [56, 11], topology, affordanceCatalog: affordances });
  assert.match(prompt, /User-supplied map/);
  assert.match(prompt, /Selected gates by center: Ajna: 11; Throat: 56\./);
  assert.match(prompt, /Complete channels: 11–56\./);
  assert.match(prompt, /Centers connected by complete channels: Ajna, Throat\./);
  assert.match(prompt, /Do not infer traits, needs, deficits, compatibility, feelings, hormones, health, biology, or outcomes/);
  assert.doesNotMatch(prompt, /Metheus prompt profile/);
});

test("keeps a configured Metheus profile separate from the user's map", () => {
  const prompt = generateBodygraphInputPrompt({
    userGates: [11],
    metheusGates: [62, 17],
    topology,
    affordanceCatalog: affordances,
  });
  assert.match(prompt, /## User-supplied map/);
  assert.match(prompt, /## Metheus prompt profile/);
  assert.match(prompt, /not an AI-owned chart, body, or lived experience/);
  assert.match(prompt, /Selected gates by center: Ajna: 17; Throat: 62\./);
  assert.match(prompt, /Complete channels: 17–62\./);
});

test("uses compact form for dense maps while retaining channel topology", () => {
  const everyGate = Array.from({ length: 64 }, (_, index) => index + 1);
  const prompt = generateBodygraphInputPrompt({
    userGates: everyGate,
    metheusGates: everyGate,
    topology,
    affordanceCatalog: affordances,
  });
  assert.match(prompt, /compact form/);
  assert.match(prompt, /Complete channels:/);
  assert.match(prompt, /Centers connected by complete channels:/);
  assert.match(prompt, /Complete channels: .*11–56/);
  assert.match(prompt, /Root:/);
});

test("rejects invalid selections and inconsistent catalog versions", () => {
  for (const userGates of [[], [11, 11], [0], [65]]) {
    assert.throws(() => generateBodygraphInputPrompt({ userGates, topology, affordanceCatalog: affordances }), TypeError);
  }
  assert.throws(() => generateBodygraphInputPrompt({
    userGates: [11],
    metheusGates: [17, 17],
    topology,
    affordanceCatalog: affordances,
  }), TypeError);
  assert.throws(() => generateBodygraphInputPrompt({
    userGates: [11],
    topology,
    affordanceCatalog: { ...affordances, topologyVersion: "mismatch" },
  }), TypeError);
});
