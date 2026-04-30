"""Utility helpers for the Device Lifecycle Management app."""

import logging

from nautobot_device_lifecycle_mgmt.choices import CVESeverityChoices

logger = logging.getLogger("nautobot_device_lifecycle_mgmt")

_VALID_SEVERITIES = {choice[0] for choice in CVESeverityChoices.CHOICES}


def standardize_cvss_severity(raw: str | None) -> str:
    """Standardize a raw CVSS severity string to a ``CVESeverityChoices`` value.

    Maps NIST API values (``"CRITICAL"``, ``"HIGH"``, ...) to the title-cased
    values stored in ``CVELCM.severity``. Unrecognized input falls back to
    ``CVESeverityChoices.NONE`` with a warning log.

    Args:
        raw: A severity string from an external source (e.g. NIST CVE API), or
            ``None``/empty if no severity is available.

    Returns:
        A valid ``CVESeverityChoices`` value.
    """
    if not raw:
        return CVESeverityChoices.NONE
    candidate = raw.strip().title()
    if candidate in _VALID_SEVERITIES:
        return candidate
    logger.warning("Unrecognized CVSS severity %r; defaulting to %s", raw, CVESeverityChoices.NONE)
    return CVESeverityChoices.NONE
