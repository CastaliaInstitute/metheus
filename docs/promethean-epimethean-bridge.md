# Bridging Promethean design and Epimethean life

**Status:** working model, version 0.1. This proposes how Metheus can let Human Design symbolism and lived physiology inform the same reflection without conflating them. It does not claim that Human Design structures measure, cause, or predict endocrine function.

## The bridge is a relation, not an identity

Metheus can place a person's Promethean map beside Epimethean records and ask whether a symbolic theme is useful in light of lived experience. The map supplies vocabulary and questions; the lived layer supplies dated observations, reports, and context. Neither layer translates automatically into the other.

This distinction matters because Human Design describes a BodyGraph of nine centers, 64 gates, and 36 channels as an internal symbolic architecture. A channel is defined by two gates connecting centers inside that framework. Some Human Design teaching also gives centers biological or glandular correspondences. Those are **claims within a symbolic lineage**, not a validated endocrine anatomy or clinical assessment. In physiology, glands release hormones into circulation, feedback loops regulate them, and many hormones act across multiple tissues; an endocrine organ is not equivalent to a symbolic center. [Jovian Archive's system description](https://jovianarchive.com/blogs/human-design-basics/centers-gates-and-channels), [IHDS center correspondences](https://ihumandesignschool.com/the-nine-centers/), [MedlinePlus on endocrine glands](https://medlineplus.gov/encyc/article/002351.htm), [NCBI Bookshelf: principles of endocrinology](https://www.ncbi.nlm.nih.gov/books/NBK20/).

## Three crosswalk relation types

Every symbolic-to-lived crosswalk should declare one relation type:

| Relation | What it means | Example | What it does not mean |
|---|---|---|---|
| **Symbolic doctrine** | A relationship taught by a named version or lineage of Human Design, chakra practice, or another symbolic system | “This lineage associates the Root center with adrenal themes.” | A medical fact or a measured adrenal state |
| **Reflective association** | A user- or author-chosen thematic pairing used to formulate a question | Placing a person's fatigue notes next to a Root-centered prompt | Evidence that the symbolic feature explains the fatigue |
| **Empirical association** | A testable statistical relation between prespecified symbolic features and specified, appropriately collected Epimethean variables | A preregistered study asks whether a chart feature is associated with a repeated, validated measure after relevant covariates | Causation, clinical validity, or individual prediction without further evidence |

The correspondence schema represents relations involving a symbolic feature. It is not a container for general biomedical mechanisms: an assay's validity or a hormone pathway is a general evidence claim, not a symbolic crosswalk. Metheus stores those claims separately using the [evidence-claim model](evidence-claim-model.md) and [scoped evidence-claim schema](../schema/evidence-claim.schema.json), which capture scope, citations, review, status, limitations, and permitted use. A mechanism described in biomedical sources does not validate a Human Design or chakra association.

Empirical-association records require at least one directly relevant citation, a dated review, and a named reviewer role. They cannot be used to explain a person's measurements or predict an individual's outcome. Never silently upgrade a lineage statement or reflective pairing to empirical association.

## A cautious center-level conversation map

The table below is a **prompting guide**, not a body map. The symbolic themes are summarized from Human Design teaching; candidate Epimethean domains are simply records a person might choose to discuss beside that theme. The legacy gland associations are included only so the source-specific doctrine can be recognized and provenance-tagged. The source explicitly presents them as a design teaching; Metheus does not adopt them as physiology.

| Promethean center | Human Design theme (source-attributed) | Some lineage's biological correspondence (tradition-attributed) | Epimethean material that might be placed beside it | Example of a question, without biological inference |
|---|---|---|---|---|
| Head | Inspiration, questions, mental pressure | Pineal | Light exposure, sleep timing, questions or mental load as self-report | “When did questions feel most present, and what else was happening?” |
| Ajna | Conceptualization and mental awareness | Anterior/posterior pituitary | Thinking or uncertainty as self-report; clinical pituitary results only if independently collected | “Does this way of organizing ideas feel useful in this situation?” |
| Throat | Manifestation, communication, expression | Thyroid and parathyroid | Communication events, voice experience, relevant thyroid/parathyroid lab records | “How did speaking or not speaking fit the circumstances?” |
| G / Identity | Identity, love, direction | Liver / blood | Identity and direction reflections; liver-related clinical records only if relevant and volunteered | “What felt like your direction here?” |
| Heart / Ego / Will | Will, value, material resources | Thymus / stomach in one IHDS teaching | Effort, promises, limits, rest; clinical measures remain separate | “What did you commit to, and what did it cost or enable?” |
| Spleen | Instinct, immediate awareness, wellbeing | Lymphatic system / immunity | Sensations and symptoms as self-report; immune tests or diagnoses only as sourced clinical records | “What did you notice in the moment?” |
| Solar Plexus | Emotion and changing emotional experience | Kidney / pancreas in one IHDS teaching | Mood and felt experience, sleep, reproductive-stage context, assay results if available | “What shifted over time, and which parts are directly observed?” |
| Sacral | Response and life-force energy | Ovaries / testes in one IHDS teaching | Activity, effort/rest, feeding or reproductive context, personal energy report | “When did you feel available for the activity you chose?” |
| Root | Pressure, stress, drive | “Adrenalin” (IHDS source wording); another HD teaching names adrenal glands | Workload, sleep, activity, stress as self-report, cortisol or catecholamine results only if tested | “Which pressures felt urgent, and what helped you recover?” |

The organ/biology pairings in the table come from one Human Design school's account of the nine centers. Other materials vary in wording and scope; a separate Human Design center page explicitly describes a Root/adrenal association, but neither source makes the chart a test of gland function. Keep each cited source attached if this vocabulary is used. [IHDS: The Nine Centers](https://ihumandesignschool.com/the-nine-centers/), [Human Design: Centers](https://human.design/the-human-design-system/centers).

## Why not map hormones directly to gates?

Begin with source-specific mappings only where a named Human Design source actually defines them. Do not invent a hormone for each gate, or assign one biochemical meaning to every gate in a channel. A hormone may be produced in one tissue, regulated by several axes, released in pulses or daily rhythms, and act at receptors throughout the body. A symbolic gate is a different kind of object. Even when a source describes a gate's “biology,” store that description as lineage doctrine unless independent evidence supports a specific empirical claim. The current [gate endocrine-correspondence catalog](../catalog/gate-endocrine-correspondences.json) now includes a 48-entry, source-attributed gate-to-organ table for endocrine-related organs from one 7 Jewels resource, alongside six earlier records from other lineages. Together they cover 48 distinct gates. These are symbolic/source-specific organ assignments, not biological mechanisms or Metheus-validated associations. Where the source names a hormone-producing gland, that remains gland context rather than a gate-specific hormone claim.

For a proposed mapping such as `Gate → hormone` or `Channel → endocrine pathway`, require all of the following before treating it as more than a symbolic prompt:

1. Named system, source, version, exact gate/channel, and wording of the traditional claim.
2. A clearly specified hormone, specimen, assay, timing protocol, population, and outcome.
3. A prespecified hypothesis and analysis plan; no searching across all gates and hormones and selecting an appealing match after seeing results.
4. Appropriate comparison groups, sample-size rationale, confounder plan, replication, and independent review.
5. Evidence that supports the particular claim being made. Statistical co-occurrence is not a mechanism and does not license diagnosis or individual prediction.

Until that evidence exists, the allowed language is “this tradition associates…,” “we are exploring this as a metaphor,” or “in these records, these things co-occurred.” Avoid “this gate controls,” “your chart means your hormone is…,” or “this channel causes…”.

## Channels and chakras

Treat a channel first as a **Promethean relation** between two gates and their centers. A reading may use that relation to connect two symbolic themes, then ask how the person experiences both themes in a particular context. The channel itself is not a neural tract, endocrine axis, or physiological flow.

If a chakra correspondence is used, record the chakra tradition, lineage, and version explicitly. “Chakra,” Human Design's nine-center BodyGraph, and the anatomical/endocrine systems are not interchangeable vocabularies. Do not force a one-to-one seven-chakra-to-nine-center conversion; a source may describe a transformation or adaptation, but Metheus must preserve that source's own claim rather than present it as universal history or anatomy.

### Designing an environment around an open theme

Metheus can extend the reflective use of an undefined gate/channel by asking what practice, access support, routine, space, person, group, or tool the subject wants available. Call this an **environmental affordance** or **functional analogue**, not a new chart definition. In Human Design terminology, definition remains a chart/calculation property; lineage descriptions of conditioning through another person or transit remain attributed symbolic doctrine. A Metheus-created support must be grounded in a non-symbolic goal, observed need, task demand, developmental context, or access constraint, and the person chooses whether to try it. The chart can suggest a question but cannot decide what needs filling. See the [environmental affordance layer](environmental-affordance-layer.md).

An AI conversation can offer a repeatable conversational scaffold—for example, rehearsal, reflection, or problem-solving practice—if that is what the person wants. A subject may describe their own experience of an AI interaction in relationship-like terms; Metheus should retain it as the subject's description while representing the AI's product role as a tool/scaffold. It must not say that an AI carries the complementary gate, forms a Human Design channel, has reciprocal feelings, or replaces a human relationship. Outcomes and any biological measurements remain separate from the interaction record.

## The reading sequence

1. **Name the Promethean feature.** Show chart source/version and the selected center, gate, channel, line, or other feature.
2. **Name its symbolic meaning.** Attribute the interpretation to the selected Human Design lineage; do not present it as measured.
3. **Select relevant Epimethean records.** Use only the person's chosen observations for the question and window. Display source class, time, method, and coverage.
4. **Keep any correspondence explicit.** If a gland or hormone link is mentioned, label it `tradition_attributed` and cite the lineage. If a matching assay exists, show that assay separately with its own provenance.
5. **Describe co-occurrence before interpretation.** State what repeated records show, missingness, alternatives, and what they cannot establish.
6. **Offer a reflective question.** The person decides whether the symbolic theme connects with their experience; disagreement is valid and should not be explained away.

### Example

Suppose a reading concerns an activated gate within the Solar Plexus center, and a person also has cycle notes, self-reported mood entries, and one progesterone result.

Metheus may say:

> In the Human Design source you selected, this Solar Plexus feature is described through an emotional-awareness theme. Your notes show that mood, cycle timing, and sleep varied across the dates you recorded; the progesterone value is a separate lab result from one collection time. These records do not show that the gate or progesterone caused the mood changes. Does the symbolic theme help you reflect on the changes you noticed, or would another framing fit better?

It may not conclude that the gate produces progesterone, that progesterone defines the person's emotional authority, or that one result describes an entire cycle.

## Data model for a crosswalk

A future relation record should be versioned and separate from observations and chart placements:

```json
{
  "id": "relation-example-01",
  "sourceSystem": { "name": "Human Design", "lineage": "named source", "version": "source version" },
  "sourceFeature": { "kind": "center", "id": "solar_plexus" },
  "targetConcept": { "kind": "hormone", "id": "progesterone" },
  "relationType": "tradition_attributed",
  "evidenceStatus": "not_evaluated",
  "permittedUse": "optional_reflective_prompt",
  "sourceCitations": [{ "title": "specific source", "url": "https://example.org/source" }],
  "claimText": "Source's own wording, paraphrased with provenance",
  "limitations": ["This attributed symbolic correspondence is not a measured or validated endocrine relation."],
  "reviewedAt": "2026-10-20"
}
```

This example remains illustrative and should not be loaded as a real Human Design correspondence. Actual source-attributed entries are held in the separate [gate endocrine-correspondence catalog](../catalog/gate-endocrine-correspondences.json). Its items use the machine-readable [`correspondence schema`](../schema/correspondence.schema.json), wrapped by the [`correspondence catalog schema`](../schema/correspondence-catalog.schema.json). A clinical assay record remains a separate observation. A user's consent to reflect on one link does not turn the link into a validated biological relation.

## Design decisions to carry forward

- Promethean chart features are calculated once from their source inputs and kept immutable except for correction/recalculation with an explicit version.
- Epimethean physiology is time-indexed, optional, provenance-preserving, and revisable; it does not alter the birth chart.
- The bridge is many-to-many and source-dependent. One center can be discussed beside several processes, and one hormone can interact with multiple organs and life contexts.
- A symbolic feature may prioritize a question, not select or impute a hormone measurement.
- Readings disclose whether a link is lineage doctrine, metaphor, empirical association, or mechanism.
- Medical interpretation remains separate from symbolic readings; no system feature diagnoses endocrine disease or recommends changing medication or hormones.

## References

- [Jovian Archive: Centers, Gates and Channels](https://jovianarchive.com/blogs/human-design-basics/centers-gates-and-channels) — Human Design's own description of its structural vocabulary.
- [Jovian Archive: Human Design Dictionary](https://jovianarchive.com/pages/human-design-dictionary) — official terms and center keynotes.
- [International Human Design School: The Nine Centers](https://ihumandesignschool.com/the-nine-centers/) — one source-specific center/organ correspondence list.
- [MedlinePlus: Endocrine glands](https://medlineplus.gov/encyc/article/002351.htm) — endocrine anatomy and hormone secretion.
- [NCBI Bookshelf: Principles of endocrinology](https://www.ncbi.nlm.nih.gov/books/NBK20/) — hormone receptors, systemic functions, feedback, and interacting axes.
