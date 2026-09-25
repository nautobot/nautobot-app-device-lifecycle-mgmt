"""Helpers for decoding CVSS vector strings into human-readable metrics."""

import re
from urllib.parse import quote

# A single metric in a CVSS vector string, as used by the CVSS calculators (for example ``AV:N``).
_METRIC_PATTERN = re.compile(r"^(?P<key>[A-Za-z]+):(?P<value>[A-Za-z]+)$")

_IMPACT_HLN = {"H": "High", "L": "Low", "N": "None"}

_CVSS_V2_METRICS = {
    "AV": (
        "Access Vector",
        "How the vulnerability is exploited.",
        {"L": "Local", "A": "Adjacent Network", "N": "Network"},
    ),
    "AC": (
        "Access Complexity",
        "The complexity of the attack required to exploit the vulnerability.",
        {"H": "High", "M": "Medium", "L": "Low"},
    ),
    "Au": (
        "Authentication",
        "The number of times an attacker must authenticate to exploit the vulnerability.",
        {"M": "Multiple", "S": "Single", "N": "None"},
    ),
    "C": (
        "Confidentiality Impact",
        "The impact on the confidentiality of information on the system.",
        {"N": "None", "P": "Partial", "C": "Complete"},
    ),
    "I": (
        "Integrity Impact",
        "The impact on the integrity of the system.",
        {"N": "None", "P": "Partial", "C": "Complete"},
    ),
    "A": (
        "Availability Impact",
        "The impact on the availability of the system.",
        {"N": "None", "P": "Partial", "C": "Complete"},
    ),
}

_CVSS_V3_METRICS = {
    "AV": (
        "Attack Vector",
        "The context by which the vulnerability can be exploited.",
        {"N": "Network", "A": "Adjacent", "L": "Local", "P": "Physical"},
    ),
    "AC": (
        "Attack Complexity",
        "Conditions beyond the attacker's control that must exist to exploit the vulnerability.",
        {"L": "Low", "H": "High"},
    ),
    "PR": (
        "Privileges Required",
        "The level of privileges an attacker must have before exploiting the vulnerability.",
        {"N": "None", "L": "Low", "H": "High"},
    ),
    "UI": (
        "User Interaction",
        "Whether a user other than the attacker must participate in the attack.",
        {"N": "None", "R": "Required"},
    ),
    "S": (
        "Scope",
        "Whether the vulnerability can affect resources beyond the vulnerable component.",
        {"U": "Unchanged", "C": "Changed"},
    ),
    "C": ("Confidentiality", "The impact on the confidentiality of information.", _IMPACT_HLN),
    "I": ("Integrity", "The impact on the integrity of information.", _IMPACT_HLN),
    "A": ("Availability", "The impact on the availability of the affected component.", _IMPACT_HLN),
}

_CVSS_V4_METRICS = {
    "AV": (
        "Attack Vector",
        "The context by which the vulnerability can be exploited.",
        {"N": "Network", "A": "Adjacent", "L": "Local", "P": "Physical"},
    ),
    "AC": (
        "Attack Complexity",
        "Measurable actions the attacker must take to evade or circumvent existing security controls.",
        {"L": "Low", "H": "High"},
    ),
    "AT": (
        "Attack Requirements",
        "Deployment and execution conditions of the vulnerable system that enable the attack.",
        {"N": "None", "P": "Present"},
    ),
    "PR": (
        "Privileges Required",
        "The level of privileges an attacker must have before exploiting the vulnerability.",
        {"N": "None", "L": "Low", "H": "High"},
    ),
    "UI": (
        "User Interaction",
        "Whether a human user other than the attacker must participate in the attack.",
        {"N": "None", "P": "Passive", "A": "Active"},
    ),
    "VC": (
        "Vulnerable System Confidentiality",
        "The impact on the confidentiality of the vulnerable system.",
        _IMPACT_HLN,
    ),
    "VI": ("Vulnerable System Integrity", "The impact on the integrity of the vulnerable system.", _IMPACT_HLN),
    "VA": ("Vulnerable System Availability", "The impact on the availability of the vulnerable system.", _IMPACT_HLN),
    "SC": (
        "Subsequent System Confidentiality",
        "The impact on the confidentiality of subsequent systems.",
        _IMPACT_HLN,
    ),
    "SI": ("Subsequent System Integrity", "The impact on the integrity of subsequent systems.", _IMPACT_HLN),
    "SA": ("Subsequent System Availability", "The impact on the availability of subsequent systems.", _IMPACT_HLN),
    "E": (
        "Exploit Maturity",
        "The likelihood of the vulnerability being attacked, based on current exploit techniques.",
        {"X": "Not Defined", "A": "Attacked", "P": "POC", "U": "Unreported"},
    ),
}

_CVSS_METRICS_BY_VERSION = {
    "2.0": _CVSS_V2_METRICS,
    "3.0": _CVSS_V3_METRICS,
    "3.1": _CVSS_V3_METRICS,
    "4.0": _CVSS_V4_METRICS,
}


def _calculator_url(version: str, vector: str) -> str:
    """Return the URL of the official calculator for a CVSS vector."""
    if version == "2.0":
        return f"https://nvd.nist.gov/vuln-metrics/cvss/v2-calculator?vector={quote(f'({vector})', safe='')}"
    return f"https://www.first.org/cvss/calculator/{version}#{vector}"


def parse_cvss_vector(vector: str | None) -> dict | None:
    """Decode a CVSS vector string into its version and human-readable metrics.

    CVSS v3.0, v3.1 and v4.0 vectors start with a ``CVSS:<version>/`` prefix. Vectors
    without a prefix are treated as CVSS v2.0. Each ``/``-separated segment must match the
    CVSS calculator's ``METRIC:VALUE`` form (for example ``AV:N``); blank or malformed
    segments are skipped, and the returned ``vector`` is rebuilt from the valid segments.

    Args:
        vector: A CVSS vector string, for example ``CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H``.

    Returns:
        A dictionary with the ``version``, the ``vector``, the ``calculator_url`` and a list
        of ``metrics``, each with its ``key``, ``name``, ``description``, ``value`` and
        ``value_name``. Metrics or values that are not recognized keep their raw text and
        have an empty description. Returns ``None`` if the vector is empty, uses an
        unsupported CVSS version, or has no valid metrics.
    """
    vector = (vector or "").strip().strip("()")
    if not vector:
        return None

    parts = [part.strip() for part in vector.split("/") if part.strip()]
    if parts and parts[0].startswith("CVSS:"):
        prefix = parts.pop(0)
        version = prefix.removeprefix("CVSS:")
    else:
        prefix = ""
        version = "2.0"

    definitions = _CVSS_METRICS_BY_VERSION.get(version)
    if definitions is None:
        return None

    metrics = []
    for part in parts:
        match = _METRIC_PATTERN.match(part)
        if not match:
            continue
        key, value = match.group("key"), match.group("value")
        name, description, values = definitions.get(key, (key, "", {}))
        metrics.append(
            {
                "key": key,
                "name": name,
                "description": description,
                "value": value,
                "value_name": values.get(value, value),
            }
        )

    if not metrics:
        return None

    segments = [f"{metric['key']}:{metric['value']}" for metric in metrics]
    if prefix:
        segments.insert(0, prefix)
    vector = "/".join(segments)
    return {
        "version": version,
        "vector": vector,
        "calculator_url": _calculator_url(version, vector),
        "metrics": metrics,
    }
