from nautobot.apps.jobs import IntegerVar, Job, StringVar
from netutils.ping import tcp_ping

class ConnectivityCheckTask(Job):  # pylint: disable=too-many-instance-attributes
    """Nautobot Job for checking a tcp port is 'opened'."""

    ip_addresses = StringVar(
        description="IP Address, specify in a comma separated list for multiple ip addresses.",
        label="IP Address",
    )
    port = IntegerVar(default=22)

    class Meta:  # pylint: disable=too-few-public-methods
        """Simple TCP Ping"""

        name = "TCP Connectivity Check"
        description = "Run Netutils TCP_PING function and report status."

    def run(self, *args, **kwargs):
        """Process tcp_ping task from job."""
        self.logger.info(f"{dir(self)}")
        ip_addresses = kwargs["ip_addresses"].replace(" ", "").split(",")
        for ipaddr in ip_addresses:
            reach_check = tcp_ping(ipaddr, kwargs["port"])
            self.logger.info("Reachability check to %s:%s boolean result: %s", ipaddr, kwargs["port"], reach_check)
