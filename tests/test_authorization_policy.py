"""Adversarial tests for the in-memory, fail-closed consent policy."""

from __future__ import annotations

import copy
import json
import unittest
from datetime import datetime, timezone
from pathlib import Path

from metheus.authorization import evaluate_authorization


ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 10, 20, 18, 0, tzinfo=timezone.utc)
SUBJECT = "rhythm-example-subject"
SOURCE = json.loads((ROOT / "examples/rhythm-sleep-2026-10-20.example.json").read_text(encoding="utf-8"))
GRANT = json.loads((ROOT / "examples/rhythm-summary-consent.example.json").read_text(encoding="utf-8"))


def grant(**updates: object) -> dict:
    value = copy.deepcopy(GRANT)
    value.update(updates)
    return value


class AuthorizationPolicyTests(unittest.TestCase):
    def evaluate(self, record: dict | None = None, grants: list[dict] | None = None, *, action: str = "analyze", purpose: str = "rhythm_summary", recipient: dict | None = None) -> dict:
        return evaluate_authorization(
            [copy.deepcopy(record or SOURCE)],
            copy.deepcopy(grants if grants is not None else [GRANT]),
            subject_id=SUBJECT,
            purpose=purpose,
            action=action,
            now=NOW,
            recipient=recipient,
        )

    def test_exact_subject_record_and_domain_scope_authorizes(self) -> None:
        result = self.evaluate()
        self.assertTrue(result["authorized"])
        self.assertEqual(result["decisions"][0]["reason"], "covered_by_active_scoped_grant")

    def test_subject_domain_and_record_scope_mismatches_deny(self) -> None:
        foreign = copy.deepcopy(SOURCE)
        foreign["subjectId"] = "someone-else"
        self.assertEqual(self.evaluate(foreign)["decisions"][0]["reason"], "subject_mismatch")

        wrong_domain = grant(domains=["nutrition"])
        self.assertFalse(self.evaluate(grants=[wrong_domain])["authorized"])

        wrong_record = grant(recordIds=["different-record"])
        self.assertFalse(self.evaluate(grants=[wrong_record])["authorized"])

    def test_expired_future_and_withdrawn_grants_do_not_authorize(self) -> None:
        for inactive in (
            grant(expiresAt="2026-10-20T18:00:00Z"),
            grant(createdAt="2026-10-21T00:00:00Z"),
            grant(status="withdrawn"),
        ):
            with self.subTest(grant=inactive):
                self.assertFalse(self.evaluate(grants=[inactive])["authorized"])

    def test_withdrawal_and_supersession_invalidate_old_same_subject_grant(self) -> None:
        old = grant(id="old-grant")
        revoked = grant(id="withdrawal", status="withdrawn", revokesGrantIds=["old-grant"])
        self.assertFalse(self.evaluate(grants=[old, revoked])["authorized"])

        replacement = grant(id="replacement", supersedes="old-grant")
        replaced = self.evaluate(grants=[old, replacement])
        self.assertTrue(replaced["authorized"])
        self.assertEqual(replaced["decisions"][0]["grantId"], "replacement")
        self.assertTrue(self.evaluate(grants=[replacement])["authorized"])

    def test_remote_processing_needs_record_scope_and_disclosure(self) -> None:
        remote = grant(permittedActions=["analyze", "remote_processing"], remoteProcessingDisclosureVersion="remote/1")
        self.assertTrue(self.evaluate(grants=[remote], action="remote_processing")["authorized"])
        self.assertFalse(self.evaluate(grants=[grant(permittedActions=["analyze", "remote_processing"])], action="remote_processing")["authorized"])
        broad = grant(recordIds=None, timeScope=None, permittedActions=["analyze", "remote_processing"], remoteProcessingDisclosureVersion="remote/1")
        self.assertFalse(self.evaluate(grants=[broad], action="remote_processing")["authorized"])

    def test_share_requires_exact_recipient_and_scope_note(self) -> None:
        share = grant(permittedActions=["share"], recipient={"reference": "clinician-1", "role": "clinician"}, scopeNote="Requested sleep-summary review.")
        self.assertTrue(self.evaluate(grants=[share], action="share", recipient={"reference": "clinician-1", "role": "clinician"})["authorized"])
        self.assertFalse(self.evaluate(grants=[share], action="share", recipient={"reference": "clinician-2", "role": "clinician"})["authorized"])
        self.assertFalse(self.evaluate(grants=[{**share, "scopeNote": ""}], action="share", recipient={"reference": "clinician-1", "role": "clinician"})["authorized"])

    def test_caregiver_reported_record_requires_child_steward_and_respects_declined_assent(self) -> None:
        child_record = copy.deepcopy(SOURCE)
        child_record["subjectId"] = "child-1"
        child_record["epistemicClass"] = "caregiver_reported"
        child_record["domain"] = "development"
        caregiver_grant = grant(
            subjectId="child-1", grantor={"reference": "caregiver-1", "role": "parent_guardian"},
            domains=["development"], purposes=["caregiver_coordination"],
            childParticipation={"assentState": "asked_agreed"},
        )
        result = evaluate_authorization([child_record], [caregiver_grant], subject_id="child-1", purpose="caregiver_coordination", action="analyze", now=NOW)
        self.assertTrue(result["authorized"])
        declined = {**caregiver_grant, "childParticipation": {"assentState": "asked_declined"}}
        result = evaluate_authorization([child_record], [declined], subject_id="child-1", purpose="caregiver_coordination", action="analyze", now=NOW)
        self.assertFalse(result["authorized"])
        self.assertEqual(result["decisions"][0]["reason"], "child_declined_in_applicable_grant")

    def test_derived_phase_requires_selected_source_and_each_item_authorized(self) -> None:
        source = copy.deepcopy(SOURCE)
        source["id"] = "bleeding-source"
        source["eventType"] = "bleeding_start"
        source["domain"] = "reproductive"
        phase = json.loads((ROOT / "examples/phase-epimethean.example.json").read_text(encoding="utf-8"))
        phase["subjectId"] = SUBJECT
        phase["basisRecordIds"] = [source["id"]]
        source_grant = grant(id="reproductive-source", domains=["reproductive"], purposes=["personal_reflection"], recordIds=[source["id"]])
        phase_grant = grant(id="reproductive-phase", domains=["reproductive"], purposes=["personal_reflection"], recordIds=[phase["id"]])
        result = evaluate_authorization([source, phase], [source_grant, phase_grant], subject_id=SUBJECT, purpose="personal_reflection", action="analyze", now=NOW)
        self.assertTrue(result["authorized"], result)

        missing_source = evaluate_authorization([phase], [phase_grant], subject_id=SUBJECT, purpose="personal_reflection", action="analyze", now=NOW)
        self.assertEqual(missing_source["decisions"][0]["reason"], "phase_basis_record_not_selected")

        source_without_consent = evaluate_authorization([source, phase], [phase_grant], subject_id=SUBJECT, purpose="personal_reflection", action="analyze", now=NOW)
        self.assertFalse(source_without_consent["authorized"])

    def test_duplicate_record_or_grant_ids_fail_closed(self) -> None:
        selected = [copy.deepcopy(SOURCE), copy.deepcopy(SOURCE)]
        result = evaluate_authorization(selected, [GRANT], subject_id=SUBJECT, purpose="rhythm_summary", action="analyze", now=NOW)
        self.assertFalse(result["authorized"])
        self.assertEqual(result["decisions"][0]["reason"], "duplicate_record_id")
        ambiguous = self.evaluate(grants=[GRANT, copy.deepcopy(GRANT)])
        self.assertFalse(ambiguous["authorized"])


if __name__ == "__main__":
    unittest.main()
