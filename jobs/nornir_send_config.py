"""Example Nornir Job."""

from typing import Optional
import logging
from nautobot.apps.jobs import Job, ObjectVar, register_jobs
from nautobot.dcim.models import Device
from nautobot_plugin_nornir.constants import NORNIR_SETTINGS
from nautobot_plugin_nornir.plugins.inventory.nautobot_orm import NautobotORMInventory
from nornir import InitNornir
from nornir.core.plugins.inventory import InventoryPluginRegister
from nornir_nautobot.plugins.tasks.dispatcher import dispatcher

InventoryPluginRegister.register("nautobot-inventory", NautobotORMInventory)

LOGGER = logging.getLogger("NORNIR_LOGGER")

class ExampleNornirJob(Job):
    """Nornir on a Device."""

    device = ObjectVar(model=Device, required=False)

    class Meta:
        """Meta for Example Nornir Job."""

        name = "Example Nornir Job"
        description = "example job to login on a device"


    def run(self, device: Optional[Device]):
        """Job execution method."""
        try:
            with InitNornir(
                runner=NORNIR_SETTINGS.get("runner"),
                logging={"enabled": False},
                inventory={
                    "plugin": "nautobot-inventory",
                    "options": {
                        "credentials_class": NORNIR_SETTINGS.get("credentials"),
                        "params": NORNIR_SETTINGS.get("inventory_params"),
                        "queryset": Device.objects.filter(name=device.name),
                    },
                },
            ) as nornir_obj:
                config_to_send = [f"ntp server 1.1.1.1"]
                for nr_host, nr_obj in nornir_obj.inventory.hosts.items():
                   send_config = nornir_obj.run(
                        task=dispatcher,
                        name="CONFIGURATION MERGE",
                        obj=nr_host,
                        logger=LOGGER,
                        config=config_to_send,
                        can_diff=False,
                    )
                   self.logger.info(send_config[nr_host][0].result[0].result)
        except Exception as error:
            self.logger.error(error)

jobs = [ExampleNornirJob]

register_jobs(*jobs)
