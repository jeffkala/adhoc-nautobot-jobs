"""Context file for IPAM Site Design."""

from nautobot_design_builder.context import Context, context_file
from nautobot_design_builder.errors import DesignValidationError


@context_file("ipam_context.yml")
class IpamSiteDesignContext(Context):
    """Render context for ipam site design."""

    site_name: str
    site_size: str
    lan_segments: int

    def validate_lan_segments_to_size(self):
        """Simple lan validations for lan segement counts."""
        if self.site_size in ["micro", "small"] and self.lan_segments != 0:
            self.log_failure(
                "Micro and small sites don't allow for selecting lan_segments, please leave the value at 0."
            )
            raise DesignValidationError(
                "Micro and small sites don't allow for selecting lan_segments, please leave the value at 0."
            )
