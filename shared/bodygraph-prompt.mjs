const CENTER_NAMES = {
  head: "Head",
  ajna: "Ajna",
  throat: "Throat",
  g_identity: "G / Identity",
  heart: "Heart / Ego",
  solar_plexus: "Solar Plexus",
  sacral: "Sacral",
  spleen: "Spleen",
  root: "Root",
};

function normalizeGateList(gates, label, { optional = false } = {}) {
  if (optional && gates === undefined) return [];
  if (
    !Array.isArray(gates)
    || (!optional && gates.length < 1)
    || gates.some((gate) => !Number.isInteger(gate) || gate < 1 || gate > 64)
    || new Set(gates).size !== gates.length
  ) throw new TypeError(`${label} must contain distinct gate numbers from 1 to 64.`);
  return [...gates].sort((a, b) => a - b);
}

/** Generate a readable AI input prompt from selected maps and versioned topology. */
export function generateBodygraphInputPrompt({ userGates, metheusGates, topology, affordanceCatalog }) {
  const selectedUserGates = normalizeGateList(userGates, "User map");
  const selectedMetheusGates = normalizeGateList(metheusGates, "Metheus prompt profile", { optional: true });
  if (
    !topology
    || topology.catalogId !== "human-design-bodygraph-topology-v1"
    || !Array.isArray(topology.gates)
    || !Array.isArray(topology.channels)
    || topology.channels.length !== 36
    || !affordanceCatalog
    || affordanceCatalog.catalogId !== "metheus-gate-ai-affordances-v1"
    || affordanceCatalog.topologyCatalogId !== topology.catalogId
    || affordanceCatalog.topologyVersion !== topology.version
    || !Array.isArray(affordanceCatalog.entries)
    || affordanceCatalog.entries.length !== 64
  ) throw new TypeError("A complete, version-matched BodyGraph topology and gate activity catalog are required.");

  const topologyGates = new Map(topology.gates.map((gate) => [gate.number, gate]));
  const activities = new Map(affordanceCatalog.entries.map((entry) => [entry.gateNumber, entry]));
  const knownGates = Array.from({ length: 64 }, (_, index) => index + 1);
  if (
    topologyGates.size !== 64
    || activities.size !== 64
    || knownGates.some((number) => !topologyGates.has(number) || !activities.has(number))
    || [...selectedUserGates, ...selectedMetheusGates].some((number) => !activities.has(number))
    || topology.channels.some((channel) => (
      !Number.isInteger(channel.gateA)
      || !Number.isInteger(channel.gateB)
      || channel.gateA === channel.gateB
      || channel.id !== `ch-${channel.gateA}-${channel.gateB}`
      || topologyGates.get(channel.gateA)?.centerId !== channel.centerA
      || topologyGates.get(channel.gateB)?.centerId !== channel.centerB
    ))
    || affordanceCatalog.entries.some((entry) => {
      const gate = topologyGates.get(entry.gateNumber);
      return !gate
        || entry.title !== gate.title
        || entry.centerId !== gate.centerId
        || !Array.isArray(entry.channelIds)
        || [...entry.channelIds].sort().join("|") !== [...(gate.channelIds || [])].sort().join("|");
    })
  ) throw new TypeError("The BodyGraph topology and gate activity catalog are incomplete or inconsistent.");

  const describeMap = (gateNumbers, heading, role) => {
    const selected = new Set(gateNumbers);
    const gateLines = gateNumbers.map((number) => {
      const gate = topologyGates.get(number);
      const activity = activities.get(number);
      return `- Gate ${number} · ${gate.title} · ${CENTER_NAMES[gate.centerId] || gate.centerId}: ${activity.aiAffordance}`;
    });
    const channels = topology.channels.filter((channel) => selected.has(channel.gateA) && selected.has(channel.gateB));
    const channelLines = channels.length
      ? channels.map((channel) => `- Channel ${channel.gateA}–${channel.gateB} (both selected endpoints): use the two gate activity ideas above only if combining them helps the request; do not infer a separate channel meaning.`)
      : ["- No complete channels are present in this selected gate set."];
    const centers = [...new Set(channels.flatMap((channel) => [channel.centerA, channel.centerB]))]
      .sort()
      .map((center) => CENTER_NAMES[center] || center);
    return [
      `## ${heading}`,
      role,
      `Selected gates: ${gateNumbers.join(", ")}.`,
      "Gate activity ideas (optional interaction formats):",
      ...gateLines,
      `Complete channels: ${channels.map((channel) => `${channel.gateA}–${channel.gateB}`).join(", ") || "none"}.`,
      `Centers connected by complete channels: ${centers.join(", ") || "none"}.`,
      "Channel references:",
      ...channelLines,
    ].join("\n");
  };

  const sections = [
    "Metheus BodyGraph input prompt",
    "Use the following selected Human Design map only as an optional, source-specific symbolic interaction lens. This is user-supplied and unverified; it is not a measurement, psychological assessment, or biological model.",
    describeMap(selectedUserGates, "User-supplied map", "The person selected these gates for their own map; chart ownership and calculation have not been verified."),
  ];
  if (selectedMetheusGates.length) {
    sections.push(describeMap(
      selectedMetheusGates,
      "Metheus prompt profile",
      "This is a user-configured AI interaction-style profile, not a chart or lived experience belonging to the AI. Keep it separate from the user's map.",
    ));
  }
  sections.push(
    "## Response guidance",
    "Answer the person's actual question first. Use at most one relevant activity idea to shape practical help; combine two endpoint activities only when the combination is useful. Keep map ownership and the two maps distinct. Describe activities in plain language before optional gate/channel labels. Make symbolic framing easy to decline and provide chart-free help equally well.",
    "Do not infer personality, ability, needs, deficits, compatibility, feelings, hormones, health, biology, or outcomes from gates, centers, channels, or map overlap. Do not claim that an AI activates, completes, or embodies a gate/channel. An unselected gate is not a missing capacity. If no activity fits, answer normally without chart framing.",
    "The BodyGraph topology defines gate and channel membership only. The activity text is a Metheus design proposal, not Human Design doctrine or validated evidence.",
  );
  const detailedPrompt = sections.join("\n\n");
  if (detailedPrompt.length <= 1_700) return detailedPrompt;

  const describeCompactMap = (gateNumbers, heading, role) => {
    const selected = new Set(gateNumbers);
    const byCenter = new Map();
    for (const number of gateNumbers) {
      const centerId = topologyGates.get(number).centerId;
      const center = CENTER_NAMES[centerId] || centerId;
      if (!byCenter.has(center)) byCenter.set(center, []);
      byCenter.get(center).push(number);
    }
    const centers = [...new Set(topology.channels
      .filter((channel) => selected.has(channel.gateA) && selected.has(channel.gateB))
      .flatMap((channel) => [channel.centerA, channel.centerB])
      .map((center) => CENTER_NAMES[center] || center))].sort();
    const channels = topology.channels
      .filter((channel) => selected.has(channel.gateA) && selected.has(channel.gateB))
      .map((channel) => `${channel.gateA}–${channel.gateB}`);
    return [
      `## ${heading}`,
      role,
      `Selected gates by center: ${[...byCenter].map(([center, numbers]) => `${center}: ${numbers.join(",")}`).join("; ")}.`,
      `Complete channels: ${channels.join(", ") || "none"}.`,
      `Centers connected by complete channels: ${centers.join(", ") || "none"}.`,
    ].join("\n");
  };
  const compactSections = [
    "Metheus BodyGraph input prompt · compact form",
    `Symbolic topology: ${topology.catalogId} ${topology.version}. This user-supplied map is unverified; use its gate/channel structure only as an optional symbolic lens, not as measurement or biology.`,
    describeCompactMap(selectedUserGates, "User-supplied map", "Self-reported map for the requesting person; not independently verified."),
  ];
  if (selectedMetheusGates.length) {
    compactSections.push(describeCompactMap(
      selectedMetheusGates,
      "Metheus prompt profile",
      "User-configured AI interaction-style lens, not an AI-owned chart, body, or lived experience. Keep separate from the user map.",
    ));
  }
  compactSections.push(
    "Answer the person's actual question first. Do not infer traits, needs, deficits, compatibility, feelings, hormones, health, biology, or outcomes from gates, channels, centers, or overlap. Do not invent gate meanings or claim AI gate activation. Keep symbolic framing optional; give chart-free help equally well.",
  );
  return compactSections.join("\n\n");
}
