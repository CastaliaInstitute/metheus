# Environmental affordances and designed “channels”

**Status:** proposed Metheus extension, version 0.1. This describes optional ways to shape a person's environment around a chosen need or activity. It does not change a Promethean chart, validate Human Design, or prescribe a health, developmental, or relationship intervention.

## Three meanings to keep apart

1. **Chart definition** is a calculated Promethean property under a named Human Design source and calculation. A Metheus reading must not recalculate it from a conversation, a wearable, a life event, or an AI interaction.
2. **Conditioning or temporary completion** is language used within Human Design lineages for what may happen when another person or a transit supplies a complementary gate. It remains a statement within that symbolic system. For example, the [Jovian Archive glossary](https://jovianarchive.com/pages/human-design-dictionary) describes a channel as formed by the joining of two activated gates and says a dormant gate in an undefined center may be affected by another or a transit.
3. **A Metheus environmental affordance** is a real, revisable support someone may choose to make available around a goal or need: a routine, space, object, prompt, practice, peer, group, professional, or digital tool. It can offer a *functional analogue* to a theme the person wants to explore. It does not literally define a gate, complete a channel, or turn an undefined center into a deficit.

Metheus can use an undefined gate or channel as an optional **question prompt**—for example, “Is there a kind of practice or support you wish were easier to access?”—but the chart alone cannot establish a need or choose what should be built. Any proposed support must rest on the person's stated goal, observed friction, access need, developmental context, or other selected non-symbolic input. The person may decline, revise, or ignore it.

## From prompt to optional environment design

1. **Keep the chart statement attributed.** Name the source and lineage; show its undefined/hanging-gate vocabulary as a chart description, not a clinical or psychological finding.
2. **Translate the theme into a function, not an identity.** Ask whether the person wants more opportunity for communication practice, reflection, learning, structure, connection, problem solving, or another self-chosen function.
3. **Ground design in lived context.** Use only selected evidence such as the person's stated goal, repeated report, task demands, access constraints, caregiver-supported developmental context, or feedback from previous attempts. Do not infer a missing capacity from an undefined chart feature.
4. **Offer alternatives.** A person might prefer a human peer, group, physical cue, routine, professional support, AI conversation, or no additional support. Present costs, privacy, availability, and limits in plain language when relevant.
5. **Let the person decide whether to try it.** A reflection option is an invitation, not a recommendation. Record proposed, chosen, declined, revised, and actually used separately.
6. **Ask what happened.** Record the person's later experience or task-specific observation separately from the affordance. A trial can feel useful, neutral, uncomfortable, inaccessible, or mixed. One response does not validate the symbolic pairing or establish a general effect.

The draft [reading schema](../schema/reading.schema.json) permits an `environmental_affordance` reflection option. It requires a non-symbolic basis and source record, and it records the delivery mode, intended function, and role frame. The [observation schema](../schema/observation.schema.json) can separately record an affordance lifecycle event (`offered`, `chosen`, `declined`, `unavailable`, `used`, `stopped`, or revised) and later observations can link to its stable `affordanceId`. The [synthetic AI-use example](../examples/environmental-affordance-ai-use.example.json) and its distinct [uncertain response](../examples/environmental-affordance-response.example.json) show this split; the [linked case bundle](../examples/environmental-affordance-linked-case.example.json) combines them with the originating reading and selected record IDs. The in-memory [`validate_environmental_affordance_links`](../metheus/affordances.py) resolver checks that selected lifecycle events point to an existing same-subject reading option, preserve its delivery/function/role metadata, and that selected response records point to a selected same-subject affordance trial. Reading preflight runs this check before consented analysis. `assemble_reading` now carries reflection options into the output package with selected sources and subject status, and the HTML presenter renders them as optional ideas rather than recommendations; the [synthetic assembled option](../examples/assembled-reading-ai-affordance.example.json) demonstrates the presentation contract, and the [rendered HTML example](../examples/assembled-reading-ai-affordance.html) shows the actual presentation. Regenerate it with `python tools/render_reading_example.py examples/assembled-reading-ai-affordance.example.json examples/assembled-reading-ai-affordance.html`. It does not validate event ordering, require every lifecycle step, interpret AI disclosure quality, assess effectiveness or safety, or infer causality; those remain separate decisions and evidence questions.

Consent remains tied to the actual record's domain and purpose. For example, an AI dialogue used for a learning goal is a learning record; if the subject separately reports experiencing it as relationship-like, that account belongs under the relationship domain and sensitive privacy scope. Analysis involving a remote AI service requires the separate remote-processing permission already defined in the [privacy model](privacy-consent-model.md). Do not store prompts or transcripts as part of the affordance event; an explicit, separate purpose and data-retention decision would be required for any such content.

This is representation only: Metheus does not currently generate, deploy, rank, or evaluate supports or run an AI service.

## AI-mediated scaffold

An AI conversation could be one designed affordance. It might offer a repeatable place to rehearse a conversation, organize thoughts, explore alternatives, or practice a skill when a person chooses that function. A user may personally describe the interaction as relationship-like; Metheus can preserve that as the user's account. The system should still describe the service's role as a **tool or scaffold**, not claim that the AI has feelings, reciprocal attachment, human judgment, or a Human Design gate/channel.

An AI scaffold should:

- disclose that the partner is AI, what it is intended to do, and what it cannot do;
- keep the subject in control of the topic, memory, privacy choices, and ability to stop or delete the interaction;
- avoid exclusivity, emotional-dependency cues, pressure to return, claims of love or need, and framing itself as a replacement for friends, caregivers, clinicians, or community;
- keep private or intimate details optional and minimize storage and third-party information;
- connect practice to the person's chosen real-world activity when desired, without demanding transfer to human relationships;
- offer alternatives such as journaling, independent rehearsal, a trusted person, an accessibility tool, or no interaction;
- keep the response and its perceived after-effect as separate records; do not label an AI output as evidence, therapy, diagnosis, or a biological signal.

For babies and young children, an AI scaffold must not be represented as an attachment figure, caregiver, or substitute for responsive human care. Any age-appropriate use should support caregiver-child interaction or a concrete learning/access need, with appropriate stewardship and review; Metheus currently has no child-facing AI service.

## Example

A person has an undefined channel in a chart and asks whether it explains why they find language practice easier with a conversation partner. Metheus may state the chart's source-attributed description, then keep it separate from the person's own account that short, low-pressure French practice helps them prepare. It could ask whether they want to try a human peer, an AI tool that role-plays a dialogue, solo rehearsal, or nothing. If they choose the AI practice, the option is grounded in their stated learning goal and prior feedback, not in the chart. Later feedback might say it felt useful or uncomfortable; neither result changes their chart definition or proves that the symbolic theme caused the experience.

## Model boundary

The Promethean map may help someone notice a question. It must not determine the affordance, the user's capacity, or whether the experiment succeeded. An environmental affordance belongs to context; a person's decision to use it belongs to behavior; their response belongs to a separately sourced observation. If Metheus later compares repeated trials, it must describe within-person timing and uncertainty and avoid causal language unless a suitable reviewed design supports it.

Related: [Promethean–Epimethean bridge](promethean-epimethean-bridge.md), [reading grammar](reading-grammar.md), [developmental learning layer](developmental-learning-layer.md), [privacy and consent model](privacy-consent-model.md), and [systems model](systems-model.md).
