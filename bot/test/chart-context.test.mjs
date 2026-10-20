import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { buildChartContext, buildMetheusGateProfile, roomParticipantLabel } from "../src/chart-context.mjs";
import { formatChartAsk, parseChartAsk } from "../../shared/chart-command.mjs";

const botDir = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const rootDir = path.resolve(botDir, "..");
const topology = JSON.parse(fs.readFileSync(path.join(rootDir, "catalog/human-design-bodygraph-topology.json"), "utf8"));
const affordances = JSON.parse(fs.readFileSync(path.join(rootDir, "catalog/gate-ai-affordances.json"), "utf8"));
const canonicalExample = JSON.parse(fs.readFileSync(path.join(rootDir, "examples/chart-aware-ai-context-unverified.example.json"), "utf8"));

test("parses explicit chart ask and normalizes gate list", () => {
  assert.deepEqual(parseChartAsk("my-gates: 56, 11 | help me explore curiosity"), {
    gates: [56, 11],
    question: "help me explore curiosity",
  });
});

test("a PWA-formatted chart prompt with separate user and Metheus maps round-trips", () => {
  const command = formatChartAsk([56, 11], "  help me explore curiosity  ");
  assert.equal(command, "!metheus ask-chart my-gates: 11, 56 | help me explore curiosity");
  assert.deepEqual(parseChartAsk(command.slice("!metheus ask-chart ".length)), {
    gates: [11, 56],
    question: "help me explore curiosity",
  });

  const withMetheusMap = formatChartAsk([56, 11], "help me explore curiosity", [62, 17]);
  assert.equal(withMetheusMap, "!metheus ask-chart my-gates: 11, 56 | metheus-gates: 17, 62 | help me explore curiosity");
  assert.deepEqual(parseChartAsk(withMetheusMap.slice("!metheus ask-chart ".length)), {
    gates: [11, 56],
    metheusGates: [17, 62],
    question: "help me explore curiosity",
  });
});

test("chart prompt formatter rejects empty, duplicate, and invalid selections", () => {
  for (const gates of [[], [11, 11], [0], [65]]) {
    assert.throws(() => formatChartAsk(gates, "question"), TypeError);
  }
  assert.throws(() => formatChartAsk([11], " "), TypeError);
});

test("requires the sender to self-attest the chart list in the command syntax", () => {
  assert.ok(parseChartAsk("gates: 11, 56 | question").error);
  assert.match(parseChartAsk("my-gates: 11 | question").question, /question/);
});

test("labels shared-room speakers without sending their Matrix IDs", () => {
  const members = ["@alpha:example.org", "@beta:example.org"];
  assert.equal(roomParticipantLabel(members, "@beta:example.org"), "Room participant 2");
  assert.equal(roomParticipantLabel(members, "@unknown:example.org"), "Room participant");
  assert.equal(roomParticipantLabel(null, "@beta:example.org"), "Room participant");
});

test("rejects malformed, out-of-range, and repeated gates", () => {
  for (const command of [
    "gates: 11, 56 | question",
    "gates: 0 | question",
    "gates: 65 | question",
    "gates: 11, 11 | question",
    "gates: 11 |",
  ]) {
    assert.ok(parseChartAsk(command).error, command);
  }
  assert.ok(parseChartAsk("my-gates: 11 | metheus-gates: 17, 17 | question").error);
  assert.ok(parseChartAsk("my-gates: 11 | metheus-gates: 65 | question").error);
});

test("builds a separate Metheus interaction profile without treating it as a user chart", () => {
  const profile = buildMetheusGateProfile([17, 62], topology, affordances);
  assert.equal(profile.contextType, "metheus_symbolic_prompt_profile");
  assert.deepEqual(profile.configuredGateNumbers, [17, 62]);
  assert.ok(profile.configuredGateActivities.some((gate) => gate.gateNumber === 17));
  assert.ok(profile.configuredChannels.some((channel) => channel.channelId === "ch-17-62"));
  assert.match(profile.statement, /not a user chart/);
  assert.ok(buildMetheusGateProfile([17, 17], topology, affordances).error);
});

test("adds activated gate titles and complementary activity ideas", () => {
  const context = buildChartContext([11], topology, affordances);
  assert.equal(context.contextType, "optional_symbolic_chart_context");
  assert.deepEqual(context.chartProvenance, {
    kind: "sender_supplied_unverified_gate_list",
    chartBinding: "sender_self_attested_unverified",
  });
  assert.equal(context.topologyCatalogId, "human-design-bodygraph-topology-v1");
  assert.equal(context.affordanceCatalogId, "metheus-gate-ai-affordances-v1");
  assert.deepEqual(context.activatedGateNumbers, [11]);
  assert.equal(context.activatedGates[0].sourceTitle, "Ideas");
  assert.match(context.activatedGates[0].examplePrompt, /questions or connections/i);
  assert.ok(context.complementaryGateCandidates.some((item) =>
    item.channelId === "ch-11-56" && item.activeGateNumber === 11 && item.complementaryGateNumber === 56,
  ));
  assert.ok(context.complementaryGateCandidates.find((item) => item.channelId === "ch-11-56").examplePrompt);
  assert.ok(context.assistantGuidance.some((guidance) => guidance.includes("Never infer biology")));
  assert.ok(context.assistantGuidance.some((guidance) => guidance.includes("self-attests this is their own gate list")));
  assert.ok(context.assistantGuidance.some((guidance) => guidance.includes("Answer the user's stated question or goal first")));
  assert.ok(context.assistantGuidance.some((guidance) => guidance.includes("complete activated-gate set for each chart-aware request")));
  assert.ok(context.assistantGuidance.some((guidance) => guidance.includes("use it to shape the help itself")));
  assert.ok(context.assistantGuidance.some((guidance) => guidance.includes("Choose the most relevant activity")));
  assert.ok(context.assistantGuidance.some((guidance) => guidance.includes("correct or reject the lens")));
  assert.ok(context.assistantGuidance.some((guidance) => guidance.includes("proactively offer at most one even if the user did not ask")));
  assert.ok(context.assistantGuidance.some((guidance) => guidance.includes("easy to skip")));
  assert.ok(context.assistantGuidance.some((guidance) => guidance.includes("distinguish it from the already activated gates")));
});

test("matches the shared canonical context example exactly", () => {
  assert.deepEqual(buildChartContext([11], topology, affordances), canonicalExample);
});

test("recognizes complete channels and does not suggest their complement", () => {
  const context = buildChartContext([11, 56], topology, affordances);
  assert.ok(context.activeChannels.some((item) => item.channelId === "ch-11-56"));
  assert.ok(!context.complementaryGateCandidates.some((item) => item.channelId === "ch-11-56"));
});

test("fails closed when catalog versions do not match", () => {
  const mismatched = { ...affordances, topologyVersion: "wrong-version" };
  assert.ok(buildChartContext([11], topology, mismatched).error);
});

test("builder rejects invalid gate arrays even when called without the parser", () => {
  assert.ok(buildChartContext([11, 11], topology, affordances).error);
  assert.ok(buildChartContext([0], topology, affordances).error);
});
