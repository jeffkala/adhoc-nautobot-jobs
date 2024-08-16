"""Context file for New Device Registration Design."""

from nautobot_design_builder.context import Context, context_file
from nautobot_design_builder.errors import DesignValidationError


@context_file("context.yml")
class NewDeviceRegistrationDesignContext(Context):
    """Render context for New Device Registration Design."""

    site_name: str
    device_hostname: str

    def validate_hostname(self):
        """Simple validations for hostnames."""
        if not self.device_hostname:
            raise DesignValidationError("Hostname cannot be empty.")
