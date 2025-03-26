from nautobot.apps.jobs import IntegerVar, Job, StringVar
from netutils.ping import tcp_ping
from celery import group
from celery import signature

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
        self.logger.info(f"{dir(self.job_result)}")
        # args: ['jobs.jobs.tcp_connection_check.ConnectivityCheckTask']
        tkwargs = {'ip_addresses': '10.1.1.9', 'port': 22}
        #  'task_args', 'task_kwargs', 'task_name'
        self.logger.info(self.job_result.task_args)
        self.logger.info(self.job_result.task_kwargs)
        self.logger.info(self.job_result.celery_kwargs)
        self.logger.info(self.job_result.task_name)
        sig = signature('jobs.jobs.tcp_connection_check.ConnectivityCheckTask', args=self.job_result.celery_kwargs, **tkwargs)
        g = group([sig])
        res = g.apply_async()
        res.ready()
        self.logger.info("res: %s", res)
        ip_addresses = kwargs["ip_addresses"].replace(" ", "").split(",")
        for ipaddr in ip_addresses:
            reach_check = tcp_ping(ipaddr, kwargs["port"])
            self.logger.info("Reachability check to %s:%s boolean result: %s", ipaddr, kwargs["port"], reach_check)
