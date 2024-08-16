"""Initial data required for New Device Registration builds."""

import time

from django.contrib.auth import get_user_model
from django.urls import reverse
from nautobot.dcim.models import Device, DeviceType, Location, Platform
from nautobot.extras.jobs import IPAddressWithMaskVar, ObjectVar, StringVar
from nautobot.extras.models import Job, JobResult, Role, Status
from nautobot_design_builder.contrib.ext import (
    ChildPrefixExtension,
    NextPrefixExtension,
)
from nautobot_design_builder.design_job import DesignJob
from nautobot_golden_config.models import GoldenConfig

from .context import NewDeviceRegistrationDesignContext


class NewDeviceRegistrationDesign(DesignJob):
    """New Device Registration."""

    class Meta:
        """Metadata needed to create a new device and generate bootstrap config design."""

        name = "New Device Registration"
        commit_default = True
        design_files = [
            "designs/0001_new_device_design.yaml.j2",
            "designs/0002_new_device_design.yaml.j2",
        ]
        context_class = NewDeviceRegistrationDesignContext
        nautobot_version = ">=2"
        extensions = [NextPrefixExtension, ChildPrefixExtension]

    site_name = ObjectVar(
        model=Location,
        label="Location",
        description="Location to reserve prefixes for. If location doesn't display make sure the proper site registration process was completed.",
        required=True,
    )
    device_hostname = StringVar(
        required=True,
        label="Device Hostname (must start with site code. See CDAS for details).",
        regex=r"(\w{2}-){2,}\w*",
    )
    device_mgmt_ip = IPAddressWithMaskVar(
        required=True,
        label="Device Mgmt IP with CIDR Mask",
        description="Mgmt IP and subnet. E.g 192.0.2.0/24 or fe80::dead:beef/64",
    )
    device_mgmt_interface = StringVar(
        label="Device Mgmt Interface",
        description="Mgmt Interface E.g. Vlan1234 or GigabitEthernet1",
        required=True,
    )
    device_platform = ObjectVar(
        label="Device Platform",
        model=Platform,
        required=True,
        description="The platform of the device to onboard. Use cisco_xe for most Cisco devices",
    )
    device_role = ObjectVar(
        label="Device Role",
        model=Role,
        query_params={"content_types": "dcim.device"},
        required=True,
    )

    def post_implementation(self, context, environment):
        """Generate bootstrap config."""
        User = get_user_model()  # pylint: disable=invalid-name
        executing_user = User.objects.get(id=self.celery_kwargs["nautobot_job_user_id"])

        current_device = Device.objects.get(name=context["device_hostname"])
        gc_intended = Job.objects.get(name="Generate Intended Configurations")
        bootstrap_config_job = JobResult.enqueue_job(
            job_model=gc_intended,
            user=executing_user,
            device=[current_device.id],
        )
        bootstrap_config_job.save()
        self.log_info(
            bootstrap_config_job,
            "Golden Config Job to Generate Intended Config has started...",
        )
