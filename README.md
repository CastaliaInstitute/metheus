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

See [Metheus as a systems model](docs/systems-model.md) for the intended architecture: a stable symbolic map in conversation with physiology, development, circadian and feeding rhythms, relationships, circumstances, and observations that change over time.

See [Metheus ontology](docs/ontology.md) for core entities and epistemic classes, with a draft [observation schema](schema/observation.schema.json) for time-bounded records.

See [Metheus reading grammar](docs/reading-grammar.md) for synthesis rules and worked examples, with a draft [reading schema](schema/reading.schema.json) for sourced claims, limitations, and subject-controlled reflection options.

See [First executable rhythm summaries](docs/rhythm-analysis.md) for deterministic descriptions of logged sleep, meal/feeding timing, meal timing relative to wake, and gaps between reported bleeding-onset dates.

See [Measurement landscape](docs/measurement-landscape.md) for a modality-by-modality account of what Metheus could record, what is only an estimate, and the limits of wearables, urine tests, laboratory results, self-reports, and developmental records.

See [Rhythm system model](docs/rhythm-system.md) for how circadian, sleep/wake, eating/feeding, activity, reproductive, developmental, and social rhythms may be represented and compared over time.

See [Promethean–Epimethean bridge](docs/promethean-epimethean-bridge.md) for a source-attributed way to place gates, channels, centers, chakra traditions, and lived physiology in conversation without conflating symbolism with endocrine mechanisms. The draft [correspondence schema](schema/correspondence.schema.json) keeps these crosswalks distinct from measured observations.

See the [evidence-claim model](docs/evidence-claim-model.md) and [scoped evidence-claim schema](schema/evidence-claim.schema.json) for separately sourced biomedical, measurement-validity, intervention, and developmental claims. General scientific evidence does not turn a symbolic correspondence into a biological finding.

See [Epimethean behavior layer](docs/behavior-layer.md) for representing chosen or constrained eating patterns, fasting, exercise, supplements, sleep/light routines, and other practices alongside physiology without treating the model as a prescriber.

See [Sensory, aroma, and flavor layer](docs/sensory-aroma-flavor-layer.md) for recording scent, taste, flavor, and route separately from measured or reported outcomes, with evidence limits on hormone-response claims.

See [Developmental psychology and learning layer](docs/developmental-learning-layer.md) for using developmental and learning sciences to shape revisable learning options while keeping symbolic design reflective rather than deterministic.

The [synthetic learning example set](examples/learning-reading.example.json) shows a Promethean prompt, learning activity, separate learner feedback, and a structured reading with subject-controlled reflection options.

See the [privacy, consent, and data stewardship model](docs/privacy-consent-model.md) and draft [consent-grant schema](schema/consent.schema.json) for scoped permissions, child participation, relationship-data boundaries, and required data lifecycle controls.

## Site

- GitHub Pages: https://castaliainstitute.github.io/metheus/
- Intended custom domain: https://metheus.castalia.institute/

## Local preview

Run `python3 -m http.server 8765` from this directory and open http://localhost:8765/.
