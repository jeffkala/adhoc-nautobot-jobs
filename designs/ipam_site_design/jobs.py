"""Initial data required for IPAM site builds."""

import nautobot.core.forms as utilities_forms
from nautobot.dcim.models import Location
from nautobot.extras.jobs import ChoiceVar, IntegerVar, ObjectVar, StringVar
from nautobot.ipam.models import Prefix
from nautobot_design_builder.contrib.ext import (
    ChildPrefixExtension,
    NextPrefixExtension,
)
from nautobot_design_builder.design_job import DesignJob

from .choices import SiteSizeChoice
from .context import IpamSiteDesignContext


class IpamSiteDesign(DesignJob):
    """New Site Deployment with IPAM Reservations."""

    class Meta:
        """Metadata needed to implement the ipam site design."""

        name = "New Site Deployment with IPAM Reservations"
        commit_default = False
        design_files = [
            "designs/0001_ipam_design.yaml.j2",
            "designs/0002_ipam_design.yaml.j2",
            "designs/0003_ipam_design.yaml.j2",
        ]
        context_class = IpamSiteDesignContext
        nautobot_version = ">=2"
        extensions = [NextPrefixExtension, ChildPrefixExtension]
        description = "IPAM"

    site_name = ObjectVar(
        model=Location,
        label="Site",
        query_params={
            "location_type": "Site",
        },
        description="Location to reserve prefixes for. If location doesn't display make sure the proper site registration process was completed.",
        required=True,
    )
    site_size = ChoiceVar(
        choices=SiteSizeChoice,
        required=True,
        widget=utilities_forms.StaticSelect2(),
    )
    lan_segments = IntegerVar(
        min_value=0,
        max_value=30,
        description="Number of LAN segments for the site. Leave 0 selected for Micro and Small Sites.",
        default=0,
    )
