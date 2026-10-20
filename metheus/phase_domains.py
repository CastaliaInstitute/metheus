"""Consent domains for the canonical Metheus phase systems."""

PHASE_SYSTEM_DOMAINS = {
    "human_design_transit": "symbolic",
    "astrological_transit": "symbolic",
    "menstrual_cycle": "reproductive",
    "pregnancy": "reproductive",
    "postpartum": "reproductive",
    "menopause": "reproductive",
    "development": "development",
    "sleep_wake": "sleep",
    "circadian_rhythm": "circadian",
    "eating_rhythm": "nutrition",
    "other": "other",
}

ULTRADIAN_PHASE_DOMAINS = {
    "feeding_bout_reported": "feeding",
    "within_day_activity_rest_cycle": "activity",
}


def phase_authorization_domain(phase_system: object, canonical_phase: object = None) -> str | None:
    """Return the consent domain for a supported phase system/phase pair."""
    if phase_system == "ultradian_rhythm":
        return ULTRADIAN_PHASE_DOMAINS.get(canonical_phase) if isinstance(canonical_phase, str) else None
    if not isinstance(phase_system, str):
        return None
    return PHASE_SYSTEM_DOMAINS.get(phase_system)
