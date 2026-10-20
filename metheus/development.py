"""Descriptive, date-anchored developmental age calculations."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any


INFANT_AGE_METHOD_VERSION = "metheus-infant-age-context/0.1.0"


def calculate_infant_age_context(
    birth_date: date,
    observation_date: date,
    *,
    gestational_age_at_birth_days: int,
    term_reference_days: int,
    age_precision: str = "exact",
    life_stage: str = "infancy",
) -> dict[str, Any]:
    """Return calendar-age context for a subject-reported preterm birth.

    The caller supplies the chosen term reference explicitly; this function
    classifies no milestones, developmental stage transitions, screening
    results, or clinical needs. Corrected age is omitted before the selected
    term-reference date rather than represented as a negative age.
    """
    if isinstance(birth_date, datetime) or not isinstance(birth_date, date):
        raise ValueError("birth_date must be a calendar date")
    if isinstance(observation_date, datetime) or not isinstance(observation_date, date):
        raise ValueError("observation_date must be a calendar date")
    if observation_date < birth_date:
        raise ValueError("observation_date cannot precede birth_date")
    if isinstance(gestational_age_at_birth_days, bool) or not isinstance(gestational_age_at_birth_days, int):
        raise ValueError("gestational_age_at_birth_days must be an integer")
    if isinstance(term_reference_days, bool) or not isinstance(term_reference_days, int):
        raise ValueError("term_reference_days must be an integer")
    if term_reference_days <= gestational_age_at_birth_days or gestational_age_at_birth_days < 0:
        raise ValueError("a preterm gestational age must be nonnegative and below the explicit term reference")
    if age_precision not in {"exact", "approximate"}:
        raise ValueError("age_precision must be exact or approximate")
    if life_stage not in {"newborn", "infancy"}:
        raise ValueError("life_stage must be newborn or infancy")

    chronological_age_days = (observation_date - birth_date).days
    postmenstrual_age_days = gestational_age_at_birth_days + chronological_age_days
    prematurity_interval_days = term_reference_days - gestational_age_at_birth_days
    estimated_term_date = birth_date + timedelta(days=prematurity_interval_days)

    context: dict[str, Any] = {
        "lifeStage": life_stage,
        "ageDays": chronological_age_days,
        "gestationalAgeAtBirthDays": gestational_age_at_birth_days,
        "postmenstrualAgeDays": postmenstrual_age_days,
        "termReferenceDays": term_reference_days,
        "ageAnchor": "record_time_start",
        "agePrecision": age_precision,
        "basis": "calculated",
        "ageMethod": (
            f"{INFANT_AGE_METHOD_VERSION}; elapsed calendar-date difference; "
            f"explicit term reference {term_reference_days} days"
        ),
        "ageLimitations": [
            "Calendar-age arithmetic is not a developmental assessment, milestone expectation, or screening result.",
            "The term reference is caller-selected; correction conventions and clinical use can vary.",
        ],
    }
    if observation_date >= estimated_term_date:
        context["correctedAgeDays"] = (observation_date - estimated_term_date).days
        context["correctedAgeMethod"] = (
            f"{INFANT_AGE_METHOD_VERSION}; chronological age minus the prematurity interval "
            f"({term_reference_days} - {gestational_age_at_birth_days} days); "
            f"term reference {term_reference_days} days"
        )
    return context
