# Relationship and interaction model

**Status:** draft data contract, version 0.1. This proposal describes how Metheus could represent interactions while keeping each person's account and permissions separate. It is not an intimacy, consent, compatibility, or relationship assessment tool.

## Core rule: an interaction is not shared evidence by default

One person can record their own account of an interaction. That record cannot stand in for another participant's account or disclose another person's private records. The [`interaction-event schema`](../schema/interaction-event.schema.json) is a subject-owned resource with its own record type and a record domain (`relationship` or `intimacy`). Authorization maps `relationship` records to the narrow `relationships` consent scope and keeps `intimacy` separate. It stores pseudonymous participant references, the recorder's perspective, a coarse event category, time precision, and explicit limitations. It supports conversation, caregiving, conflict, repair, affection, intimacy, and shared activity without requiring relationship status or explicit sexual detail.

A reference to a participant is not an account for that participant. This first contract does not link another participant's records. Each participant remains the owner of their own observations and would need separate, current, purpose-specific access before those records could be combined. The current consent contract evaluates each subject's records separately; it does not implement multi-party authorization, identity verification, persistence, or revocation propagation.

## Intimacy events and consent context

Metheus may allow a person to record that they chose to note an intimate interaction, with a date-only or approximate time if that is all they want to retain. The schema intentionally does not ask for sexual acts, partner identity, or a binary claim that consent was established. An optional `consentContext` records only the recorder's report of whether they noted communication, uncertainty/concern, or nothing; it is not a finding about what another participant consented to.

Consent is specific, voluntary, ongoing, and can change. A past interaction record, relationship label, prior agreement, hormone estimate, or a partner's silence cannot establish consent in a later interaction. A concern or uncertainty should not be converted into a score or automated determination; the record is a prompt for the person to seek the support they choose. Metheus must not ask an AI to adjudicate whether a sexual interaction was consensual.

## Keep physiology separate

An intimacy event can be compared descriptively with a person's separately recorded cycle or measurement events only when that person explicitly selects and authorizes those records for that purpose. The result can describe dates or co-occurrence, with coverage and missingness stated. It cannot infer desire, consent, relationship quality, fertility, a hormone level, or that hormones caused the event. Another participant's physiology must never be inferred from the recorder's data.

The same boundary applies to family interactions: a caregiver can report an event they observed, but must not assign hidden emotions, intention, attachment, or neurochemistry to a child. Child records need the relevant stewardship, minimal collection, and increasing child voice described in the [privacy model](privacy-consent-model.md).

## Example and implementation boundary

The synthetic [`interaction-intimacy` example](../examples/interaction-intimacy.example.json) shows a date-only record with no third-party identifying details or physiological claim. Its [subject-index example](../examples/interaction-subject-index.example.json) makes the record discoverable, while the [consent example](../examples/interaction-intimacy-consent.example.json) grants only this subject's own record for personal reflection. A later [corrected record](../examples/interaction-intimacy-correction.example.json) supersedes the earlier account but receives no inherited authorization; a [revised index](../examples/interaction-corrected-subject-index.example.json) points to the current record. Resource resolution and authorization recognize this record type for caller-supplied records. The repository does not store interaction events, enforce access at a storage boundary, provide partner-account linkage, or calculate relationship patterns. Until those controls exist, this remains an in-memory contract and policy path.

Related: [ontology](ontology.md), [privacy and consent](privacy-consent-model.md), [temporal comparison](rhythm-system.md), and [Methean model core](model-core-spec.md).
