/** Return a room-local ordinal without disclosing a Matrix user ID to the model. */
export function roomParticipantLabel(members, sender) {
  if (!Array.isArray(members) || typeof sender !== "string") return "Room participant";
  const index = members.indexOf(sender);
  return index < 0 ? "Room participant" : `Room participant ${index + 1}`;
}

const allowedInteractionModes = new Set([
  "create", "organize", "compare", "communicate", "reflect", "adapt", "practice", "coordinate", "learn",
]);

/** Build minimal one-request context from version-matched local catalogs. */
export function buildChartContext(gates, topology, affordanceCatalog) {
  if (
    !Array.isArray(gates)
    || !topology
    || !affordanceCatalog
    || topology.catalogId !== "human-design-bodygraph-topology-v1"
    || affordanceCatalog.catalogId !== "metheus-gate-ai-affordances-v1"
    || affordanceCatalog.topologyCatalogId !== topology.catalogId
    || affordanceCatalog.topologyVersion !== topology.version
    || !Array.isArray(topology.channels)
    || !Array.isArray(topology.gates)
    || !Array.isArray(affordanceCatalog.entries)
  ) return { error: "Chart-aware prompts are unavailable because the version-matched gate catalogs could not be loaded." };

  if (
    gates.length < 1
    || gates.some((gate) => !Number.isInteger(gate) || gate < 1 || gate > 64)
    || new Set(gates).size !== gates.length
  ) return { error: "Provide distinct gate numbers from 1 to 64." };

  const entries = new Map(affordanceCatalog.entries.map((entry) => [entry?.gateNumber, entry]));
  const topologyGates = new Map(topology.gates.map((gate) => [gate?.number, gate]));
  const channelIds = new Set(topology.channels.map((channel) => channel?.id));
  const channelPairs = new Set();
  const channelsForGate = new Map(Array.from({ length: 64 }, (_, index) => [index + 1, new Set()]));
  const channelsAreConsistent = topology.channels.length === 36
    && channelIds.size === 36
    && topology.channels.every((channel) => {
      const { id, gateA, gateB, centerA, centerB } = channel || {};
      if (
        !Number.isInteger(gateA) || gateA < 1 || gateA > 64
        || !Number.isInteger(gateB) || gateB < 1 || gateB > 64
        || gateA === gateB
        || id !== `ch-${gateA}-${gateB}`
        || !topologyGates.has(gateA) || !topologyGates.has(gateB)
      ) return false;
      const pair = `${Math.min(gateA, gateB)}-${Math.max(gateA, gateB)}`;
      if (channelPairs.has(pair)) return false;
      channelPairs.add(pair);
      const gateARecord = topologyGates.get(gateA);
      const gateBRecord = topologyGates.get(gateB);
      if (centerA !== gateARecord.centerId || centerB !== gateBRecord.centerId) return false;
      channelsForGate.get(gateA).add(id);
      channelsForGate.get(gateB).add(id);
      return true;
    })
    && topology.gates.every((gate) => {
      const expected = [...(channelsForGate.get(gate?.number) || [])].sort();
      return Array.isArray(gate?.channelIds)
        && [...gate.channelIds].sort().join("|") === expected.join("|");
    });
  if (
    affordanceCatalog.entries.length !== 64
    || entries.size !== 64
    || topology.gates.length !== 64
    || topologyGates.size !== 64
    || !channelsAreConsistent
    || Array.from({ length: 64 }, (_, index) => index + 1).some((gate) => !entries.has(gate))
    || affordanceCatalog.entries.some((entry) => {
      const source = topologyGates.get(entry?.gateNumber);
      return !source
        || entry.title !== source.title
        || entry.centerId !== source.centerId
        || !Array.isArray(entry.channelIds)
        || !Array.isArray(source.channelIds)
        || [...entry.channelIds].sort().join("|") !== [...source.channelIds].sort().join("|");
    })
    || affordanceCatalog.entries.some((entry) =>
      !Array.isArray(entry?.interactionModes)
      || entry.interactionModes.length === 0
      || new Set(entry.interactionModes).size !== entry.interactionModes.length
      || entry.interactionModes.some((mode) => !allowedInteractionModes.has(mode))
    )
    || gates.some((gate) => !entries.has(gate))
  ) {
    return { error: "Chart-aware prompts are unavailable because the gate catalog is incomplete or malformed." };
  }

  const active = new Set(gates);
  const activatedGates = [...gates].sort((a, b) => a - b).map((gateNumber) => {
    const entry = entries.get(gateNumber);
    return {
      gateNumber,
      sourceTitle: entry.title,
      centerId: entry.centerId,
      channelIds: entry.channelIds,
      interactionModes: entry.interactionModes,
      optionalActivityIdea: entry.aiAffordance,
      examplePrompt: entry.examplePrompt,
    };
  });
  const activeChannels = [];
  const complementaryGateCandidates = [];
  for (const channel of topology.channels) {
    const gateA = channel?.gateA;
    const gateB = channel?.gateB;
    if (!Number.isInteger(gateA) || !Number.isInteger(gateB)) continue;
    const aActive = active.has(gateA);
    const bActive = active.has(gateB);
    if (aActive && bActive) {
      activeChannels.push({ channelId: channel.id, gateNumbers: [gateA, gateB].sort((a, b) => a - b) });
      continue;
    }
    if (aActive === bActive) continue;
    const activeGateNumber = aActive ? gateA : gateB;
    const complementaryGateNumber = aActive ? gateB : gateA;
    const entry = entries.get(complementaryGateNumber);
    if (!entry || typeof entry.aiAffordance !== "string") continue;
    complementaryGateCandidates.push({
      channelId: channel.id,
      activeGateNumber,
      complementaryGateNumber,
      complementaryGateTitle: entry.title,
      interactionModes: entry.interactionModes,
      optionalActivityIdea: entry.aiAffordance,
      examplePrompt: entry.examplePrompt,
      framing: "Optional symbolic exploration; not gate activation, a chart change, or evidence of a missing ability.",
    });
  }
  const definedCenterIds = [...new Set(activeChannels.flatMap((item) => {
    const channel = topology.channels.find((candidate) => candidate.id === item.channelId);
    return [channel?.centerA, channel?.centerB].filter((center) => typeof center === "string");
  }))].sort();
  const chartAwareness = {
    mode: "explicit_chart_context",
    mapScope: "user_supplied_non_time_bound_gate_list",
    providedActivatedGateCount: activatedGates.length,
    providedGateNumbers: [...gates].sort((a, b) => a - b),
    providedDefinedChannelCount: activeChannels.length,
    liveStateAccess: false,
    priorChartAwareTurnMemory: false,
    statement: "This request includes only the sender's selected, self-reported non-time-bound gate list and topology-derived channels. It does not include live transits, momentary state, or prior chart-aware exchanges.",
  };
  return {
    contextType: "optional_symbolic_chart_context",
    contextScope: "user_supplied_non_time_bound_gate_list",
    chartAwareness,
    sourceSystem: { name: "Human Design" },
    chartProvenance: {
      kind: "sender_supplied_unverified_gate_list",
      chartBinding: "sender_self_attested_unverified",
    },
    topologyCatalogId: topology.catalogId,
    topologyVersion: topology.version,
    affordanceCatalogId: affordanceCatalog.catalogId,
    affordanceCatalogVersion: affordanceCatalog.version,
    activatedGateNumbers: [...gates].sort((a, b) => a - b),
    activatedGates,
    definedChannelIds: [...new Set(activeChannels.map((item) => item.channelId))].sort(),
    activeChannels,
    definedCenterIds,
    complementaryGateCandidates,
    assistantGuidance: [
      "Read the complete activated-gate set for each chart-aware request, but do not try to use every gate. Select at most one active-gate activity that best serves the user's stated goal and use it to shape the help itself (for example, brainstorm, organize, compare, or rehearse); combine active activities only when the task specifically benefits from it. Otherwise answer normally.",
      "Treat chartAwareness as the complete scope of what you know about this person's selected map for this turn. Do not claim broader or more current awareness than the listed gates and derived channels.",
      "Use each activity's interaction-mode labels as practical format hints (create, organize, compare, communicate, reflect, adapt, practice, coordinate, learn); they describe the offered activity, never the user's traits or abilities.",
      "For a listed active channel, use its gateNumbers to find the two corresponding activities in activatedGates. Combine only those catalog activities when the combination fits the stated goal; do not invent a separate channel meaning. Frame the combination as an optional symbolic lens, never a fixed trait or biological function.",
      "Choose the most relevant activity from the user's activated gates rather than treating gate titles as personality traits. Do not let chart activity displace the direct answer or repeat a suggestion within this response; never recite the full gate list. Chart-aware turns are stateless and do not include prior chart-aware suggestions, so do not claim to remember or adapt to them.",
      "If naming a gate or channel, identify it as a symbolic source label and invite the person to correct or reject the lens.",
      "The sender self-attests this is their own gate list; ownership is not authenticated. Apply it only to the sender's reflection and never to another participant.",
      "This is a user-supplied, non-time-bound personal gate list. It is not a current transit reading, live activation, or observation of the user's present state.",
      "Answer the user's stated question or goal first; do not make a gate suggestion the default response.",
      "Consider supplied complementary-gate candidates as optional environmental activities that can offer a way to explore the partner end of a channel. Assess each candidate against the user's stated goal. When one clearly helps, proactively offer at most one even if the user did not ask for channel analysis; its concrete activity must add a useful option, and you must not force a complement when none fits. Always distinguish it from the already activated gates and never imply a missing capacity.",
      "Describe any activity in plain language before naming its gate or channel, and make it easy to skip or ask for a non-chart-based alternative.",
      "Never infer biology, hormones, health, personality, ability, need, deficit, or outcome from gates, centers, or channels.",
      "A complementary gate prompt is an invitation, not evidence of a missing capacity or a gate being activated by AI.",
      "Keep practical support useful without chart framing, grounded in the user's stated goal.",
    ],
  };
}

/** Build a distinct, user-configured symbolic prompt profile for Metheus itself. */
export function buildMetheusGateProfile(gates, topology, affordanceCatalog) {
  const context = buildChartContext(gates, topology, affordanceCatalog);
  if (context.error) return context;
  return {
    contextType: "metheus_symbolic_prompt_profile",
    contextScope: "user_configured_non_time_bound_ai_prompt_style",
    statement: "This is a gate set configured by the user as an optional symbolic prompt style for the Metheus AI. The AI has no human body, lived chart, feelings, or biological gate activations. This profile is not a user chart and must not be merged with or used to explain the user's map.",
    topologyCatalogId: context.topologyCatalogId,
    topologyVersion: context.topologyVersion,
    affordanceCatalogId: context.affordanceCatalogId,
    affordanceCatalogVersion: context.affordanceCatalogVersion,
    configuredGateNumbers: context.activatedGateNumbers,
    configuredGateActivities: context.activatedGates,
    configuredChannelIds: context.definedChannelIds,
    configuredChannels: context.activeChannels,
    assistantGuidance: [
      "Treat this as an optional user-configured interaction-style lens for the AI, not as a Human Design chart belonging to the AI.",
      "Never claim that the AI has a body, lived experience, feelings, hormones, a personal chart, or biologically activated gates.",
      "Keep the user's supplied map and the Metheus prompt profile distinct. Compare shared and different gate/channel references only as symbolic map structure.",
      "Use the profile only when it improves the user's stated request; answer directly and allow chart-free interaction.",
      "Do not infer the user's traits, needs, capacity, compatibility, health, biology, or relationship from either map or from their overlap.",
      "Describe any activity in plain language and make it optional. The profile does not activate or complete a gate or channel.",
    ],
  };
}
