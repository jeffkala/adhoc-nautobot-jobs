"""Jobs for nautobot-plugin-nornir debugging."""

from datetime import datetime

import yaml
from nautobot.apps.jobs import Job, MultiObjectVar, register_jobs
from nautobot.dcim.models import Device
from nornir import InitNornir
from nornir.core.plugins.inventory import InventoryPluginRegister

from nautobot_plugin_nornir.constants import NORNIR_SETTINGS
from nautobot_plugin_nornir.plugins.inventory.nautobot_orm import NautobotORMInventory

InventoryPluginRegister.register("nautobot-inventory", NautobotORMInventory)


class DebugInventoryJob(Job):
    """Job to debug Nornir Inventory."""

    device = MultiObjectVar(model=Device, required=False)

    class Meta:  # pylint: disable=too-few-public-methods
        """Meta object boilerplate for compliance."""

        name = "Debug Nornir Inventory"
        description = "Prints inventory details per host, group, defaults."
        has_sensitive_variables = True

    def run(self, *args, **data):  # pylint: disable=too-many-branches
        """Run config compliance report script."""
        now = datetime.now()
        qs = Device.objects.filter(id__in=[dev.id for dev in data["device"]])
        after_qs = datetime.now()
        self.logger.info("Queryset Took\n%s", after_qs - now)
        self.logger.info("Queryset Count\n%s", qs.count())
        try:
            now = datetime.now()
            with InitNornir(
                runner=NORNIR_SETTINGS.get("runner"),
                logging={"enabled": False},
                inventory={
                    "plugin": "nautobot-inventory",
                    "options": {
                        "credentials_class": NORNIR_SETTINGS.get("credentials"),
                        "params": NORNIR_SETTINGS.get("inventory_params"),
                        "queryset": qs,
                        "defaults": {"now": datetime.now()},
                    },
                },
            ) as nornir_obj:
                after_qs = datetime.now()
                self.logger.info("Nonir Init Took\n%s", after_qs - now)
                for host, data in nornir_obj.inventory.hosts.items():
                    self.logger.info(
                        "#### %s\n```yaml\n%s```",
                        host,
                        yaml.dump(nornir_obj.inventory.hosts[host], default_flow_style=False),
                        extra={"object": Device.objects.get(id=data.data["id"])},
                    )
                    self.logger.info(
                        "#### %s Data\n```yaml\n%s```",
                        host,
                        yaml.dump(data.dict(), default_flow_style=False),
                        extra={"object": Device.objects.get(id=data.data["id"])},
                    )
                self.logger.info(
                    "#### Default Data\n```yaml\n%s```",
                    yaml.dump(nornir_obj.inventory.defaults.data, default_flow_style=False),
                )
        except Exception as err:
            self.logger.info("%s", err)
            raise


jobs = [DebugInventoryJob]

register_jobs(*jobs)
