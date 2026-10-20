# Metheus

Metheus is a developing framework for readings that bring symbolic design into conversation with lived, changing experience.

## The two layers

- **Promethean — the design map.** A symbolic starting point such as Human Design: a birth-based lens for noticing patterns and asking questions.
- **Epimethean — the lived story.** What unfolds over time: personal rhythms, changing bodies, relationships, life transitions, and voluntarily shared observations.

The distinction matters. Symbolic interpretation, measured signals, and a person's own report are different kinds of information. A reading can place them in conversation while keeping their sources visible and leaving meaning with the person.

Possible Epimethean context includes hormonal rhythms across menstrual cycles, pregnancy, postpartum life, and menopause; sleep, temperature, heart-rate variability (HRV); conception and birth; relationship milestones, intimacy, developmental stages, and personal reflections. A person may reflect on how their own intimacy experiences relate to their own cycle notes over time. Such a perceived pattern does not establish hormonal causation, predict desire or behavior, or speak for a partner. Any clinical or laboratory results are distinct from calendar estimates and wearable proxies. Neurochemical activity should not be claimed as measured when it has not been measured. Relationship or intimacy notes are optional, private, and subjective; they cannot establish another person's consent, feelings, or compatibility. No context or tracking is assumed or required.

For babies and young children, developmental context may include changing sleep and feeding rhythms, growth, sensory and motor exploration, communication, co-regulation, and caregiver connection. These observations should support curiosity and responsive care, never score a child or substitute for developmental screening or pediatric guidance.

## Principles

- Describe patterns relative to the person's own history; do not turn correlation into cause or a fixed trait.
- Make intimate data optional, minimized, protected, and under the person's control.
- Treat cycle timing and wearable signals as estimates and reflective context, not diagnosis or medical advice; do not infer hormone or neurochemical levels from mood or proxy signals.
- Include diverse bodies and life paths: cycles may be absent, irregular, changing, or not relevant.
- Let people decide what fits and what, if anything, they want to do with a reading.

## Project status

This site is an early concept. Wearable integrations and personal data collection are not implemented.

## Research reference

See [Hormone and endocrine-signal reference](docs/hormone-reference.md) for a broad, categorized inventory, regulation notes, and developmental-stage guidance. It distinguishes classical hormones from neurotransmitters, cytokines, growth factors, local mediators, and molecules whose endocrine classification is debated.

The [candidate endocrine-relations catalog](catalog/endocrine-relations.json) (version 0.2.3) contains 38 typed, source-attributed candidate edges across HPT, HPA, HPG, circadian–melatonin, glucose-regulation, and gut-incretin physiology. It now includes a more detailed reproductive-cycle network; every edge remains under review, internal only, and unavailable to readings or individual inference. See the [reproductive neuroendocrine network](docs/reproductive-neuroendocrine-network.md) and the [Human Design × Neuroendocrine Atlas](docs/human-design-neuroendocrine-atlas.md) for the boundary between this biological graph and the symbolic bodygraph.

See [Metheus as a systems model](docs/systems-model.md) for the intended architecture: a stable symbolic map in conversation with physiology, development, circadian and feeding rhythms, relationships, circumstances, and observations that change over time.

The installable [Metheus Circle PWA](/chat/) is an early static Matrix client for a shared room conversation. It includes a Three.js bodygraph reference that highlights gate/channel references in chat; it is generic geometry, not a participant's chart. The client supports Matrix SDK end-to-end encryption and disables sending when the room is not reported encrypted. A [prototype Matrix AI bot](bot/README.md) is included as source, but is not deployed; it requires a separate server and API credentials. See the [PWA setup and capability boundary](docs/matrix-chat-pwa.md).

See [Perception, stress, emotion, and suffering](docs/perception-stress-pathway.md) for a provisional, branching map that separates subjective appraisal and feeling from physiology, behavior, and later meaning. Its synthetic graph distinguishes rumination, co-rumination, journaling, friend conversations, and chatbot use, and keeps candidate population-level cortisol/HRV associations separate from mechanisms and individual records.

The [synthetic experience-pathway example](examples/experience-pathway-synthetic.example.json) demonstrates the draft graph contract at [experience-pathway.schema.json](schema/experience-pathway.schema.json); nodes refer to separately sourced observations, and relation types distinguish personal reports from timing overlap.

The [synthetic pathway local-preflight case](examples/experience-pathway-local-preflight.example.json) bundles a small graph, source observations, subject index, explicit source selection, and scoped consent for the pathway preflight. Its [bundle schema](schema/experience-pathway-case.schema.json) checks each component's shape; cross-record ID matching and authorization remain runtime checks.

See the [Methean model core specification](docs/model-core-spec.md) for the computational boundary between symbolic prompts, source observations, descriptive features, latent-state estimates, and readings, including typed relation classes and maturity gates for future inference.

See the [critical review](docs/critical-review.md) for the current implementation limits, unresolved architecture and validation gaps, and a prioritized path toward an end-to-end Metheus prototype.

See the [capability matrix](docs/capability-matrix.md) for a domain-by-domain distinction between documented concepts, data contracts, executable summaries, validated models, and product services.

See [Metheus ontology](docs/ontology.md) for core entities and epistemic classes, with a draft [observation schema](schema/observation.schema.json) for time-bounded records.

See [record lifecycle](docs/record-lifecycle.md) for how corrections supersede prior records, how summaries avoid double-counting visible revisions, and why deletion remains a separate storage-service responsibility.

The draft [subject index](schema/subject-index.schema.json) links separately versioned resources without embedding a full profile. Sensitive birth inputs and their derived symbolic map have distinct contracts in the [birth-chart input schema](schema/birth-chart-input.schema.json) and [symbolic map schema](schema/symbolic-map.schema.json), with synthetic examples for the [index](examples/subject-index.example.json), [birth input](examples/birth-chart-input.example.json), and [map](examples/symbolic-map.example.json).

See [Metheus reading grammar](docs/reading-grammar.md) for synthesis rules and worked examples, with a draft [reading schema](schema/reading.schema.json) for sourced claims, limitations, and subject-controlled reflection options.

See [First executable rhythm summaries](docs/rhythm-analysis.md) for deterministic descriptions of logged sleep, meal/feeding timing, meal timing relative to wake, and gaps between reported bleeding-onset dates. These now have a dedicated [derived rhythm-summary schema](schema/rhythm-summary.schema.json), subject-index references, source-record dependencies, and a fully synthetic [consented sleep-summary reading example](examples/rhythm-summary-reading.example.json).

See [Measurement landscape](docs/measurement-landscape.md) for a modality-by-modality account of what Metheus could record, what is only an estimate, and the limits of wearables, urine tests, laboratory results, self-reports, and developmental records. The [synthetic serum TSH example](examples/serum-tsh-laboratory.example.json) shows the direct-assay record shape; its fictional value has no reference interval or interpretation.

See [Rhythm system model](docs/rhythm-system.md) for how circadian, sleep/wake, eating/feeding, activity, reproductive, developmental, and social rhythms may be represented and compared over time.

See [Promethean and Epimethean phase names](docs/phase-naming-framework.md) for optional evocative labels paired with canonical phase terms, timing, evidence basis, and uncertainty. The machine-readable [phase vocabulary catalog](catalog/phase-vocabulary.json) provides suggested names, descriptions, and per-phase guardrails; its [catalog schema](schema/phase-vocabulary.schema.json) keeps symbolic transit labels separate from lived-cycle and life-stage context.

See [Promethean–Epimethean bridge](docs/promethean-epimethean-bridge.md) for a source-attributed way to place gates, channels, centers, chakra traditions, and lived physiology in conversation without conflating symbolism with endocrine mechanisms. The draft [correspondence schema](schema/correspondence.schema.json) keeps these crosswalks distinct from measured observations.

The [Human Design × Neuroendocrine Atlas](docs/human-design-neuroendocrine-atlas.md) develops that bridge as a comparative graph model: it inventories the nine symbolic centers and 36 channel edges, identifies where biological analogies need qualification, and sketches a preregistered validation approach. The [source-attributed BodyGraph topology catalog](catalog/human-design-bodygraph-topology.json) includes all 64 source-specific gate titles and a 36-channel graph checked against the PWA reference graphic; it assigns no biological functions to gates and is not a chart-calculation source until the channel endpoints receive canonical review.

See the [evidence-claim model](docs/evidence-claim-model.md), [evidence review protocol](docs/evidence-review-protocol.md), [scoped evidence-claim schema](schema/evidence-claim.schema.json), and [candidate-only evidence catalog](catalog/evidence-claims.json) for separately sourced biomedical, measurement-validity, intervention, and developmental claims. Catalog entries remain under review and internal only; general scientific evidence does not turn a symbolic correspondence into a biological finding.

See [Epimethean behavior layer](docs/behavior-layer.md) for representing chosen or constrained eating patterns, fasting, exercise, supplements, sleep/light routines, and other practices alongside physiology without treating the model as a prescriber.

See [Environmental affordances and designed “channels”](docs/environmental-affordance-layer.md) for the proposed way to turn a Promethean theme into an optional, goal-grounded environmental support—including a transparent AI-mediated scaffold—without changing chart definition or treating openness as a deficit. A [synthetic linked case](examples/environmental-affordance-linked-case.example.json) combines an originating reading, AI-use event, separate response, and explicit record selection under a bundle schema. Reading assembly preserves optional support ideas with selected source IDs and status; the HTML presenter displays them as invitations, as shown in a [synthetic assembled AI-option package](examples/assembled-reading-ai-affordance.example.json) and its [rendered HTML](examples/assembled-reading-ai-affordance.html). Regenerate with `python tools/render_reading_example.py examples/assembled-reading-ai-affordance.example.json examples/assembled-reading-ai-affordance.html`.

See [Sensory, aroma, and flavor layer](docs/sensory-aroma-flavor-layer.md) for recording scent, taste, flavor, and route separately from measured or reported outcomes, with evidence limits on hormone-response claims.

See [Developmental psychology and learning layer](docs/developmental-learning-layer.md) for using developmental and learning sciences to shape revisable learning options while keeping symbolic design reflective rather than deterministic.

The [synthetic learning example](examples/learning-reading.example.json) shows a Promethean prompt, learning activity, separate learner feedback, and a goal-grounded optional AI dialogue scaffold whose role and privacy boundaries are explicit.

The [phase-aware reading example](examples/phase-aware-reading.example.json) places an optional Promethean transit, a reported bleeding event, and a qualitative urinary LH home-test record side by side while retaining their distinct evidence classes and limits. The test does not determine the phase annotation or validate the symbolic transit.

See the [privacy, consent, and data stewardship model](docs/privacy-consent-model.md), [relationship and interaction model](docs/relationship-interaction-model.md), and draft [consent-grant schema](schema/consent.schema.json) for scoped permissions, child participation, relationship-data boundaries, and required data lifecycle controls.

The Python package includes an in-memory [`evaluate_authorization`](metheus/authorization.py) policy prototype, [`validate_reading_references`](metheus/readings.py) and [`validate_experience_pathway_references`](metheus/pathways.py) integrity checks, [`validate_environmental_affordance_links`](metheus/affordances.py) support-option/trial/response reference checks, [`preflight_subject_reading`](metheus/readings.py) consent/index gate, [`preflight_experience_pathway_sources`](metheus/pathways.py) explicit source-selection and consent preflight for local analysis, [`resolve_current_records`](metheus/lifecycle.py) revision-chain resolver, [`assemble_reading`](metheus/readings.py) deterministic claim assembler, and [`render_assembled_reading_html`](metheus/rendering.py) escaped HTML presenter. Its descriptive time operations include `summarize_numeric_measurements`, which reports numeric-series distributions and coverage while separating source/method signatures, and [`calculate_infant_age_context`](metheus/development.py), which calculates date-anchored chronological/postmenstrual age and corrected-age arithmetic from explicit inputs without milestone inference, and `describe_temporal_order`, `describe_selected_temporal_relations`, and `describe_phase_observation_relations`, which compare explicitly selected record windows without inferring a mechanism or cause. Policy version `metheus-consent-policy/0.5.0` rejects unknown purposes, action/domain enumerations, and record-type/domain pairings, maps supported phase annotations to narrow consent domains, and requires a bleeding-summary boundary onset to remain among its explicitly selected and authorized source IDs. The reading preflight validates the reading, subject index, indexed resources, selected consent grants, and selected knowledge references against their JSON Schemas before assembly; it also resolves selected environmental-affordance source/options and response/trial links in memory before consented analysis. The pathway source preflight requires the selected IDs to match exactly the pathway's source references. It authorizes only those records; it does not authorize pathway storage, sharing, or remote processing. Assembly preserves authored claim text while attaching resolved source IDs, phase metadata, reference citations, support, and limitations; it validates the assembled package against a separate output schema but does not generate prose or verify that text is entailed by sources. The HTML presenter displays the package's claims and provenance without rewriting or evaluating them. These functions evaluate caller-supplied objects but do not authenticate users or enforce access to storage. Install the runtime schema dependency with `python -m pip install -r requirements.txt`.

The [contract validation script](tools/validate_contracts.py) checks every JSON Schema, explicitly mapped example, and mapped machine-readable catalog with the Draft 2020-12 validator. Run it with `python -m pip install -r requirements-validation.txt && python tools/validate_contracts.py`. GitHub Actions runs this gate for pull requests to `main` and before a Pages deployment; this is contract validation, not behavioral coverage of the Python policy functions.

[`resolve_subject_index`](metheus/resources.py) checks resource pointers, kinds, schema versions, ownership, symbolic-map dependencies, and rhythm-summary source events. [`authorize_subject_index_resources`](metheus/resources.py) validates indexed schemas and same-subject grants, then checks consent only for an explicit selection; index membership alone never authorizes access. Selecting a summary also requires selecting and separately authorizing each of its source records. See the [resource resolution contract](docs/resource-resolution.md) for the supported kinds and remaining limitations.

[`preflight_subject_reading`](metheus/readings.py) combines index resolution, reading citations, exact domain exclusions, and consent for a subject-selected reading. The [synthetic symbolic-map reading](examples/symbolic-map-reading.example.json) illustrates a reading that cites the derived map and feature while excluding raw birth inputs; it is not an automatically generated interpretation.

## Site

- GitHub Pages: https://castaliainstitute.github.io/metheus/
- Intended custom domain: https://metheus.castalia.institute/

## Local preview

Run `python3 -m http.server 8765` from this directory and open http://localhost:8765/.
