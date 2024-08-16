"""Choicesets for IPAM Site Designs."""

from nautobot.core.choices import ChoiceSet


class SiteSizeChoice(ChoiceSet):
    """Choiceset used by IPAM Site Design."""

    SIZE_MICRO = "micro"
    SIZE_SMALL = "small"
    SIZE_MEDIUM = "medium"
    SIZE_LARGE = "large"

    CHOICES = (
        (SIZE_MICRO, "MICRO"),
        (SIZE_SMALL, "SMALL"),
        (SIZE_MEDIUM, "MEDIUM"),
        (SIZE_LARGE, "LARGE"),
    )
