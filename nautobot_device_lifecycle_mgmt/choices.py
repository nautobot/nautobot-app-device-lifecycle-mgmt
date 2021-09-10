"""Static choices uses for the Device LifeCycle plugin."""
from pycountry import countries

from nautobot.utilities.choices import ChoiceSet


class ContractTypeChoices(ChoiceSet):
    """Choices for the types of supported contracts."""

    HARDWARE = "Hardware"
    SOFTWARE = "Software"

    CHOICES = (
        (HARDWARE, "Hardware"),
        (SOFTWARE, "Software"),
    )


class PoCTypeChoices(ChoiceSet):
    """Choices for the types of point-of-contacts."""

    PRIMARY = "Primary"
    TIER1 = "Tier 1"
    TIER2 = "Tier 2"
    TIER3 = "Tier 3"
    OWNER = "Owner"
    UNASSIGNED = "Unassigned"

    CHOICES = (
        (UNASSIGNED, UNASSIGNED),
        (PRIMARY, PRIMARY),
        (TIER1, TIER1),
        (TIER2, TIER2),
        (TIER3, TIER3),
        (OWNER, OWNER),
    )


class CurrencyChoices(ChoiceSet):
    """List of currencies for representing contract amounts."""

    USD = "USD"
    EUR = "EUR"
    DKK = "DKK"
    GBP = "GBP"
    CAD = "CAD"
    JPY = "JPY"
    CHF = "CHF"
    ZAR = "ZAR"
    AUD = "AUD"
    NZD = "NZD"

    CHOICES = (
        (AUD, f"{AUD} $"),
        (CAD, f"{CAD} $"),
        (CHF, f"{CHF} Fr."),
        (DKK, f"{DKK} kr"),
        (EUR, f"{EUR} €"),
        (GBP, f"{GBP} £"),
        (JPY, f"{JPY} ¥"),
        (NZD, f"{NZD} $"),
        (USD, f"{USD} $"),
        (ZAR, f"{ZAR} R"),
    )


class CountryCodes(ChoiceSet):
    """List of support country codes."""

    CHOICES = tuple((c.alpha_3, f"{c.name} ({c.alpha_3})") for c in countries)
