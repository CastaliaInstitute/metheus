# AI affordances across the 64 gates

**Draft concept atlas · 0.1**

This atlas asks: *if a person chooses to explore a Human Design gate theme, what could an AI tool offer as a useful environmental prompt or scaffold?* It gives one practical possibility for each gate. A person can use, adapt, or ignore any idea regardless of their chart.

The gate titles and center/channel placements below follow Metheus's [versioned BodyGraph topology catalog](../catalog/human-design-bodygraph-topology.json). Titles are symbolic source labels. The activity ideas and ready-to-use example prompts in the [machine-readable catalog](../catalog/gate-ai-affordances.json) are Metheus design proposals, not Human Design doctrine, psychological assessments, evidence-based treatment, or claims about hormones.

## How to use the atlas

The sequence is **person's goal → chosen activity → optional symbolic lens → person's report**. For example, someone who wants to explore an idea might ask an AI for a relevant question, a surprising connection, and an invitation to tell a story. If the person associates that activity with 11–56, Metheus may show that as their chosen symbolic lens. The AI offers a context for curiosity and expression; it does not activate Gate 11 or 56, complete the channel, change a chart, or prove that the gates explain the person's response.

### The gate-aware response in four steps

1. **Read the selected map.** On every explicitly chart-aware request, use the complete gate list supplied for that person. Never infer gates from their words, biometrics, relationships, or another room member's chart.
2. **Help with the stated goal.** Choose an activity associated with a relevant activated gate and let it shape the practical help itself—for example, offer questions, organize details, compare options, or rehearse language. Do not recite the chart or force a gate reference into an unrelated answer.
3. **Check for a useful pairing.** If both channel endpoints are in the selected map, combine their activities only when that pairing improves the requested help. If exactly one endpoint is selected, the other endpoint is only a possible environmental activity. Offer at most one such complement, and only when it adds a useful option.
4. **Leave interpretation with the person.** Describe the activity plainly; identify the gate or channel only as an optional symbolic lens. The person can accept, adapt, decline, correct the chart, or ask for chart-free help. An unselected gate is not a deficit, and an AI prompt does not activate it.

This is how “acutely aware” should work in the product: the AI receives a clearly scoped chart-awareness snapshot with the user's selected gates and topology-derived channels on each enabled request, while remaining responsive to the immediate question. It should know the complete selected set, which channels are defined within that set, and what activity ideas the catalog links to those gates. It is not live awareness of current transits, physiology, feelings, or gate changes. The current Matrix prototype reconstructs that awareness for each request and does not remember earlier chart-aware replies or the person's reaction to them. The snapshot tells the model how many gates were provided and makes its limits explicit.

In an explicitly enabled chart-aware request, Metheus uses the person's activated-gate list and channel topology to identify activities linked to those gates and possible partner-gate activities. The Matrix bot supports one-request `ask-chart` and an explicit per-sender `chart-set` room setting for future `ask` turns; the sender supplies their own gate list, which the bot does not calculate or verify. A `chart-set` list stays in bot memory only and clears on explicit removal, any opt-out, room membership change, or process restart. On each chart-aware request, the model receives the complete set, its defined channels, and possible complementary activities. A machine-readable `chartAwareness` snapshot also summarizes exactly which map was supplied and states whether the request has live-state access or memory of earlier chart-aware turns. This lets the AI use the chart context fully without implying awareness beyond the supplied map. It first responds to the person's goal, then may offer at most one complementary activity if that activity clearly helps. Candidate presence alone does not rank an activity or establish need, ability, fit, or benefit. The suggestion is optional; the person can accept, revise, decline, or browse the same catalog without a chart. AI is a tool, not a human relationship, caregiver, clinician, or authority over a person's identity.

The AI should read the person's complete activated-gate set on each chart-aware request and answer the stated question first. It should choose at most one active-gate activity that best serves the goal, rather than trying to use every gate. For a defined channel in the supplied map, it can use the channel's paired gate numbers to find both entries in the activated-gate activity list and combine those activities when the stated task benefits; it should not invent a separate channel meaning. Present the combination as an optional symbolic lens, not a fixed trait or biological function. An activity can shape the response itself: offer several varied questions to explore an idea, organize details into a checklist, compare viewpoints, or rehearse a conversation. Do not let chart activity displace the direct answer or repeat a suggestion within the same response. These are user-selectable interaction options, not claims about the person's traits, abilities, or needs. If no activity fits, answer normally. Invite the person to correct or reject the symbolic lens.

Chart-aware means the AI is given the supplied gate map for that request; it is not live sensing of moment-to-moment gate activation. The map can guide which interaction formats it considers, but it does not diagnose a deficit or prove that an activity completes a channel. For example, a gate-linked activity may be a practical scaffold: Gate 11 can shape a curiosity exchange by offering several questions, while Gate 56 may shape a user-chosen storytelling or exploration format. The AI can offer the latter as a complement when it serves the user's goal, and should name it as an optional symbolic association. It must not claim the interaction has activated either gate, changed a hormone, or reproduced a human relationship. These limits also apply to sensory suggestions: active gates do not justify recommending aromas, flavors, supplements, or other exposures as endocrine interventions. Any sensory activity must be optional, user-directed, and supported by evidence specific to the substance, route, and outcome before Metheus makes a physiological claim.

The Matrix prototype's chart-aware turns are stateless: each turn receives the current question and chart context, not earlier chart-aware exchanges. The bot therefore cannot reliably avoid repeating an activity suggested in an earlier chart-aware turn or claim to remember the person's response to it. This is an explicit limitation; the isolated turn does not inherit shared room chat history.

An unactivated partner gate is a distinct, optional complement. The AI considers available partner-gate activities connected to the person's activated gates on each chart-aware request. When one complementary activity clearly advances the person's goal, it may proactively offer one even if the person did not ask for channel analysis. It chooses based on fit to the stated goal, not chart-only ranking. Describe the activity in plain language first, name the symbolic pairing only as optional context, and make it easy to skip or request a chart-free alternative. AI can offer an activity associated with a gate; it does not activate the gate, complete the channel, or establish that a capacity was missing. A chart-aware request is not permission to steer every reply toward the bodygraph or repeat the full gate list.

### Example: active Gate 11, optional Gate 56 complement

Suppose a person self-reports Gate 11 and asks, “I’m curious about this topic, but I don’t know where to start.” The catalog suggests using Gate 11's activity by offering a few varied questions or connections and letting the person choose one. The AI might say: “Here are three different questions you could explore. Which one interests you most?” That is the practical help; the AI need not mention the chart.

If the person asks to explore the 11–56 pairing, or a short story clearly fits the chosen topic, the AI could add: “I can also turn your chosen question into a short story and let you decide whether to continue. That is an optional activity associated with Gate 56 in this symbolic map; would you like to try it, or stay with the questions?” The person can decline or ask for a different activity. This is a designed interaction choice, not proof of a missing capacity, a biological effect, or literal channel activation. The supplied map identifies 11–56 as a channel by its gate endpoints; “curiosity” is the person's framing here, not a physiological property.

## Interaction-style labels

For a separate exploration of optional two-part AI activities when both endpoints of a channel are active, see the [36-channel AI interaction-pattern atlas](channel-ai-affordance-atlas.md). Those pairings are design proposals composed from gate-level activities, not channel interpretations or mechanisms.

The catalog uses a small set of labels to tell the AI what form an activity can take. They describe the offered support, not the person.

| Label | Plain-language meaning |
|---|---|
| `create` | Generate ideas, stories, or a first draft. |
| `organize` | Arrange details into steps, lists, or a clear structure. |
| `compare` | Lay out options or viewpoints and examine differences. |
| `communicate` | Draft or rehearse words for a message or conversation. |
| `reflect` | Offer a prompt for journaling or considering a self-reported experience. |
| `adapt` | Adjust a plan or routine to the person's stated constraints. |
| `practice` | Rehearse a conversation or build a repeatable skill activity. |
| `coordinate` | Help arrange shared tasks, resources, or responsibilities. |
| `learn` | Explain a topic or sequence material for study. |

## Head

| Gate and channel | Symbolic source title | An AI interaction someone might choose |
|---|---|---|
| 61 · 61–24 | Mystery | Explore a big question from several traditions or disciplines; separate known facts, interpretations, and open questions. |
| 63 · 63–4 | Doubt | Stress-test a claim by listing evidence, counterexamples, and what would change one's mind, without turning uncertainty into endless checking. |
| 64 · 64–47 | Confusion | Help sort a pile of notes into themes, identify missing context, and leave unresolved items visibly unresolved. |

## Ajna

| Gate and channel | Symbolic source title | An AI interaction someone might choose |
|---|---|---|
| 4 · 63–4 | Formulization | Generate candidate explanations for a question, label assumptions, and compare them without presenting a guess as certainty. |
| 11 · 11–56 | Ideas | Offer a few diverse, relevant questions or idea connections, then invite the person to choose one and tell or develop it. |
| 17 · 17–62 | Opinions | Compare viewpoints on a topic and distinguish observable evidence from interpretation and preference. |
| 24 · 61–24 | Rationalizing | Use a short “what do I know / what am I replaying / what is the next useful step?” reflection, with a clear option to stop. |
| 43 · 43–23 | Insight | Help the person express an unusual idea in their own words, consider alternatives, and identify a small way to examine it. |
| 47 · 64–47 | Realizing | Revisit selected notes or events and offer possible patterns as tentative interpretations for the person to accept or reject. |

## Throat

| Gate and channel | Symbolic source title | An AI interaction someone might choose |
|---|---|---|
| 8 · 1–8 | Contribution | Help shape a contribution for a chosen audience while preserving the person's voice and credit. |
| 12 · 12–22 | Caution | Draft a message in several tones and let the person choose whether, when, or whether not to send it. |
| 16 · 48–16 | Skills | Build a small, repeatable practice plan and a self-chosen feedback checklist for a skill. |
| 20 · 10–20, 20–34, 20–57 | Now | Turn the person's current priority into one manageable next action; do not frame speed or spontaneity as inherently better. |
| 23 · 43–23 | Assimilation | Translate a complex idea into plain language, an analogy, or a short explanation at the person's chosen level of detail. |
| 31 · 7–31 | Leading | Prepare a meeting agenda, invitation, or facilitation plan that makes room for others' input and consent. |
| 33 · 13–33 | Privacy | Offer a private reflection structure or a user-controlled summary, with clear control over what is saved or shared. |
| 35 · 35–36 | Change | Compare possible next steps during a transition, including what to keep, what to try, and what remains uncertain. |
| 45 · 21–45 | Gatherer | Help organize shared household or team resources, responsibilities, and requests transparently rather than assigning authority. |
| 56 · 11–56 | Stimulation | Create a short, user-paced story or exploration from a chosen topic, then offer “go deeper,” “tell your version,” and “stop.” |
| 62 · 17–62 | Detail | Turn a chosen plan into a checklist, glossary, or clearly labeled set of steps; let the user set the desired detail level. |

## G / Identity

| Gate and channel | Symbolic source title | An AI interaction someone might choose |
|---|---|---|
| 1 · 1–8 | Self-Expression | Offer a blank-canvas creative prompt or help revise a draft without deciding what is authentic to the person. |
| 2 · 2–14 | Higher Knowing | Map options, constraints, and resources around a direction the person has already named; do not make life decisions for them. |
| 7 · 7–31 | Role of the Self | Explore possible roles in a specific project and the responsibilities each would involve, without assigning a fixed role or destiny. |
| 10 · 10–20, 10–34, 10–57 | Behavior of the Self | Help compare an intended action with the person's stated values and context, without labeling their personality or judging their worth. |
| 13 · 13–33 | Listener | Provide a user-controlled listening or journaling prompt and reflect back only what the person chose to share. Avoid inviting unnecessary third-party secrets. |
| 15 · 5–15 | Extremes | Help design a flexible routine with acceptable variation and recovery options rather than forcing uniformity. |
| 25 · 25–51 | Spirit of the Self | Offer a compassion or values reflection in the person's own terms; do not impose spiritual beliefs or moral judgments. |
| 46 · 29–46 | Determination of the Self | Help the person keep a brief record of how an activity felt in their own body and context, without inferring physiology or telling them what their body means. |

## Heart / Ego

| Gate and channel | Symbolic source title | An AI interaction someone might choose |
|---|---|---|
| 21 · 21–45 | Hunter/Huntress | Make a transparent plan for a resource or task the person is responsible for, including shared ownership and limits. |
| 26 · 26–44 | Egoist | Practice a clear, truthful negotiation or request; help identify persuasive language that would become misleading or coercive. |
| 40 · 37–40 | Aloneness | Plan chosen solo time and recovery, while optionally making a low-pressure plan to reconnect with a trusted person. |
| 51 · 25–51 | Shock | Prepare for a new or challenging event by reviewing consent, likely surprises, a pause signal, and a safe exit option. |

## Solar Plexus

| Gate and channel | Symbolic source title | An AI interaction someone might choose |
|---|---|---|
| 6 · 59–6 | Friction | Rehearse respectful boundary-setting or a difficult conversation; do not infer reproductive state, compatibility, or emotional authority. |
| 22 · 12–22 | Openness | Explore how the person wants to communicate in a particular setting, with options to speak, wait, write, or decline. |
| 30 · 41–30 | Recognition of Feelings | Find words for a self-reported feeling and its context; never infer a feeling or hormone level from the chart or chat. |
| 36 · 35–36 | Crisis | Break a stressful situation into immediate needs and next steps; if someone reports imminent danger, direct them to appropriate human emergency support. |
| 37 · 37–40 | Friendship | Create conversation cards or a household check-in around mutual needs, agreements, and appreciation. |
| 49 · 19–49 | Principles | Help articulate a boundary, value, or group agreement and consider how it affects everyone involved. |
| 55 · 39–55 | Spirit | Offer an optional mood or meaning journal that treats entries as the person's account, not a diagnosis or stable trait. |

## Sacral

| Gate and channel | Symbolic source title | An AI interaction someone might choose |
|---|---|---|
| 3 · 3–60 | Ordering | Turn a messy transition into a few small, reversible experiments and a place to note what changed. |
| 5 · 5–15 | Fixed Rhythms | Help design a routine around the person's real schedule, with flexible timing and permission to revise it. |
| 9 · 9–52 | Focus | Break a chosen task into a short sequence, identify likely distractions, and let the person choose a stopping point. |
| 14 · 2–14 | Power Skills | Inventory skills and resources the person wants to use toward a chosen goal; avoid claims of innate power or guaranteed success. |
| 27 · 27–50 | Caring | Coordinate a user-selected care task or family checklist while keeping human responsibility and consent clear. |
| 29 · 29–46 | Saying Yes | Review a proposed commitment: why it matters, what it costs, what can change, and how the person can say no or renegotiate. |
| 34 · 20–34, 34–57 | Power | Offer a menu of ways to approach a self-chosen activity, scaled by the person's stated time, access, and energy constraints. |
| 42 · 42–53 | Growth | Break a longer project into milestones, review points, and a deliberate ending or handoff. |
| 59 · 59–6 | Sexuality | Offer consent-centered language for discussing intimacy, boundaries, and privacy; never sexualize a child, pressure a partner, or treat chat as consent. |

## Spleen

| Gate and channel | Symbolic source title | An AI interaction someone might choose |
|---|---|---|
| 18 · 18–58 | Correction | Give feedback on a user-selected draft or process using specific observations, an invitation to revise, and strengths as well as issues. |
| 28 · 28–38 | Game Player | Explore what feels meaningful in a decision and compare risks, safeguards, and alternatives without glamorizing danger. |
| 32 · 32–54 | Continuity | Compare ways to make a project sustainable, including when to continue, adapt, pause, or stop. |
| 44 · 26–44 | Alertness | Help review a user-selected pattern or past experience while labeling uncertainty and avoiding threat profiling or suspicion of others. |
| 48 · 48–16 | Depth | Build a learning path from introductory to advanced material, paced by the user's interest and available time. |
| 50 · 27–50 | Values | Draft a fair, inclusive set of shared expectations and care responsibilities for a family or team to review together. |
| 57 · 10–57, 20–57, 34–57 | Intuitive Insight | Offer a pause to notice immediate impressions, then separate “what I noticed” from “what I think it means” and check relevant evidence. |

## Root

| Gate and channel | Symbolic source title | An AI interaction someone might choose |
|---|---|---|
| 19 · 19–49 | Wanting | Help identify a stated need and draft a clear request or boundary, without claiming to read unspoken needs. |
| 38 · 28–38 | Fighter | Map a disagreement into the issue, each person's stated concern, and a non-harmful next step; prioritize de-escalation over winning. |
| 39 · 39–55 | Provocateur | Offer a playful, opt-in perspective shift or creative question, with an easy pass and no deliberate distressing or baiting. |
| 41 · 41–30 | Contraction | Plan a small, bounded start to an experience, including resource limits and what the person wants to leave open. |
| 52 · 9–52 | Inaction | Help create a focus-friendly setting with a chosen timer, break, or distraction boundary; avoid turning rest into failure. |
| 53 · 42–53 | Beginnings | Start a project with a one-step launch plan, a modest first milestone, and a review point. |
| 54 · 32–54 | Ambition | Compare goals with their tradeoffs, resources, relationships, and rest needs; let the person define what success means. |
| 58 · 18–58 | Aliveness | Brainstorm enjoyable, accessible activities and ways to make room for them, without prescribing an exercise or health regimen. |
| 60 · 3–60 | Acceptance | Identify actual constraints, distinguish fixed from negotiable parts, and generate options within the person's chosen limits. |

## Design rules for an AI implementation

- Use chart features for complementary prompting only in explicitly enabled chart-aware mode, with provenance clearly labeled as either a source-versioned calculated map or a sender-supplied, unverified gate list. The complete candidate pool is not ranked by chart alone; offer at most one activity when it clearly fits the person's stated goal. Never infer a deficit, need, ability, or likely outcome.
- Make the person's goal and the practical activity clear; the gate match explains why this idea appeared and can be hidden or ignored.
- Describe the offered function in everyday language. Put gate and channel labels in optional context, with the source/lineage available.
- Use user-controlled pacing, depth, and stop/skip controls. Do not use endless novelty, pressure, streaks, or emotional dependency to hold attention.
- Keep symbolic meaning, AI activity, the user's response, and any separately measured biometrics in distinct records. Chat content is not a hormone assay, diagnosis, or clinical assessment.
- For family use, let each person choose whether to participate and what to share. For babies and young children, AI supports a caregiver's activity; it is not an attachment figure, caregiver, or substitute for responsive human interaction.
- For intimacy, conflict, distress, and care activities, use consent-centered prompts and maintain clear human responsibility. AI-generated language never substitutes for consent or professional support.

## Data and review status

The gate-by-gate suggestions, plain-language “try asking” examples, and controlled interaction-mode labels for each of the 64 gates are available in the draft machine-readable [AI affordance catalog](../catalog/gate-ai-affordances.json), constrained by the [catalog schema](../schema/gate-ai-affordance-catalog.schema.json). Modes such as `compare`, `reflect`, or `coordinate` describe the kind of activity offered, not a user trait. The chart-aware context carries the labels with the activity ideas and example prompts, giving the AI explicit, goal-oriented ways to adapt its response. The catalog keys each suggestion to the existing versioned topology for gate title, center, and channel membership; its validator checks that those links stay aligned. The prose here is the human-readable companion. Update both together when proposals change.

Before using these suggestions in a live AI flow, review them with people who use Human Design and people who do not. Ask whether the plain-language activity is understandable and useful without seeing the gate label. Do not use engagement rates as evidence that a symbolic correspondence is valid.
