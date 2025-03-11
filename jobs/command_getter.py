"""Example to reuse nornir elements to run commands."""

from nautobot.apps.jobs import BooleanVar, Job, MultiObjectVar
from nautobot.dcim.models import Device
from nautobot_plugin_nornir.constants import NORNIR_SETTINGS
from nautobot_plugin_nornir.plugins.inventory.nautobot_orm import NautobotORMInventory
from nornir import InitNornir
from nornir.core.plugins.inventory import InventoryPluginRegister
from nornir_nautobot.exceptions import NornirNautobotException
from nornir_nautobot.plugins.tasks.dispatcher import dispatcher

InventoryPluginRegister.register("nautobot-inventory", NautobotORMInventory)


class CommandExecution(Job):
    """Simple Job to Execute Show Command."""

    devices = MultiObjectVar(model=Device, required=False)
    debug = BooleanVar(description="Enable for more verbose debug logging")

    class Meta:
        """Meta object boilerplate for onboarding."""

        name = "Runs Commands on a Device."
        description = "Login to a device(s) and run commands."
        has_sensitive_variables = False
        hidden = True

    def run(self, *args, **kwargs):  # pragma: no cover
        """Process command runner job."""
        try:
            with InitNornir(
                runner=NORNIR_SETTINGS.get("runner"),
                logging={"enabled": False},
                inventory={
                    "plugin": "nautobot-inventory",
                    "options": {
                        "credentials_class": NORNIR_SETTINGS.get("credentials"),
                        "params": NORNIR_SETTINGS.get("inventory_params"),
                        "queryset": kwargs["devices"],
                    },
                },
            ) as nornir_obj:
                self.logger.debug("Initialized Nornir object.")
                for nr_host, nr_obj in nornir_obj.inventory.hosts.items():
                    result = nornir_obj.run(
                        task=dispatcher,
                        logger=self.logger,
                        method="get_command",
                        obj=nr_host,
                        framework="netmiko",
                        command="show version",
                        use_textfsm=True,
                    )
                    self.logger.info(result)
        except NornirNautobotException as err:
            self.logger.error(err)
  
jobs = [CommandExecution]

register_jobs(*jobs)
