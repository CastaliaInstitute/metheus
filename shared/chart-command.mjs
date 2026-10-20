/** Format a self-attested, one-request chart prompt for the Matrix bot. */
function validateGateList(gates, label = "gate") {
  if (
    !Array.isArray(gates)
    || gates.length < 1
    || gates.some((gate) => !Number.isInteger(gate) || gate < 1 || gate > 64)
    || new Set(gates).size !== gates.length
  ) throw new TypeError(`Provide distinct ${label} numbers from 1 to 64.`);
  return [...gates].sort((a, b) => a - b).join(", ");
}

export function formatChartAsk(gates, question, metheusGates) {
  const prefix = formatChartAskPrefix(gates, metheusGates);
  if (typeof question !== "string" || !question.trim()) throw new TypeError("Add a question after the | separator.");
  return `${prefix}${question.trim()}`;
}

/** Format the editable command prefix for a one-turn chart-aware question. */
export function formatChartAskPrefix(gates, metheusGates) {
  const userGateList = validateGateList(gates);
  const assistantMap = metheusGates === undefined
    ? ""
    : `metheus-gates: ${validateGateList(metheusGates, "Metheus profile gate")} | `;
  return `!metheus ask-chart my-gates: ${userGateList} | ${assistantMap}`;
}

/** Format an explicit in-memory chart-aware mode for one room and sender. */
export function formatChartSet(gates) {
  if (
    !Array.isArray(gates)
    || gates.length < 1
    || gates.some((gate) => !Number.isInteger(gate) || gate < 1 || gate > 64)
    || new Set(gates).size !== gates.length
  ) throw new TypeError("Provide distinct gate numbers from 1 to 64.");
  return `!metheus chart-set my-gates: ${[...gates].sort((a, b) => a - b).join(", ")}`;
}

/** Parse a gate list for explicitly enabling chart-aware follow-up turns. */
export function parseChartSet(argument) {
  const match = /^my-gates\s*:\s*([0-9,\s]+)$/i.exec(argument);
  if (!match) return { error: "Use your own gate list: !metheus chart-set my-gates: 11, 56" };
  const rawGates = match[1].split(",").map((value) => value.trim());
  const gates = rawGates.map(Number);
  if (
    !rawGates.length
    || rawGates.some((value) => !/^\d{1,2}$/.test(value))
    || gates.some((gate) => !Number.isInteger(gate) || gate < 1 || gate > 64)
    || new Set(gates).size !== gates.length
  ) {
    return { error: "List distinct gate numbers from 1 to 64, for example: !metheus chart-set my-gates: 11, 56" };
  }
  return { gates };
}

/** Parse the exact chart-aware command accepted by the bot. */
export function parseChartAsk(argument) {
  const match = /^my-gates\s*:\s*([0-9,\s]+)\s*\|\s*([\s\S]+)$/i.exec(argument);
  if (!match) return { error: "Use only your own gate list: !metheus ask-chart my-gates: 11, 56 | your question" };
  const rawGates = match[1].split(",").map((value) => value.trim());
  const gates = rawGates.map(Number);
  if (
    !rawGates.length
    || rawGates.some((value) => !/^\d{1,2}$/.test(value))
    || gates.some((gate) => !Number.isInteger(gate) || gate < 1 || gate > 64)
    || new Set(gates).size !== gates.length
  ) {
    return { error: "List distinct gate numbers from 1 to 64, for example: !metheus ask-chart my-gates: 11, 56 | your question" };
  }
  let metheusGates;
  let question = match[2].trim();
  const assistantMatch = /^metheus-gates\s*:\s*([0-9,\s]+)\s*\|\s*([\s\S]+)$/i.exec(question);
  if (assistantMatch) {
    const rawAssistantGates = assistantMatch[1].split(",").map((value) => value.trim());
    metheusGates = rawAssistantGates.map(Number);
    if (
      !rawAssistantGates.length
      || rawAssistantGates.some((value) => !/^\d{1,2}$/.test(value))
      || metheusGates.some((gate) => !Number.isInteger(gate) || gate < 1 || gate > 64)
      || new Set(metheusGates).size !== metheusGates.length
    ) return { error: "List distinct Metheus profile gates from 1 to 64." };
    question = assistantMatch[2].trim();
  }
  if (!question) return { error: "Add a question after the | separator." };
  return metheusGates ? { gates, metheusGates, question } : { gates, question };
}
