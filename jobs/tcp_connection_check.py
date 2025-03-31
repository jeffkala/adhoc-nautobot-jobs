from nautobot.apps.jobs import IntegerVar, Job, StringVar
from netutils.ping import tcp_ping
from celery import group
from celery import signature
from celery.utils.nodenames import gethostname
from nautobot.dcim.models import Device
from nornir import InitNornir

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
        self.logger.info(f"{dir(self.job_result)}")
        self.logger.info(f"{self.job_result.task_kwargs}")
        self.logger.info(f"{self.job_result.celery_kwargs}")
        # args: ['jobs.jobs.tcp_connection_check.ConnectivityCheckTask']
        tkwargs = {'ip_addresses': '10.1.1.9', 'port': 22}
        nr = InitNornir(
            runner=NORNIR_SETTINGS.get("runner"),
            logging={"enabled": False},
            inventory={
                "plugin": "nautobot-inventory",
                "options": {
                    "runner": {
                    "plugin": "threaded",
                    "options": {
                        "num_workers": 20,
                    },
                    "credentials_class": "nautobot_plugin_nornir.plugins.credentials.env_vars.CredentialsEnvVars",
                    "queryset": Device.objects.first(),
                    "defaults": {"now": datetime.now()},
                },
            },
        )
        result = nr.run(task=hello_world)
        print(result)
        # sig = signature('nautobot.extras.jobs.run_job', args=('jobs.jobs.tcp_connection_check.ConnectivityCheckTask',{'properties':{'exchange': '', 'routing_key': 'default'}}), routing_key="default", kwargs=tkwargs)
        # g = group(sig,)
        # res = g(routing_key="default", hostname=gethostname())
        # sig = signature('nautobot.extras.jobs.run_job', args=('jobs.jobs.tcp_connection_check.ConnectivityCheckTask',{}), celery_kwargs=self.job_result.celery_kwargs, routing_key="default", kwargs=tkwargs)
        sig = signature('nautobot_plugin_nornir.jobs.hello_world', kwargs={'tasks': 'hellow_world'}, routing_key="default", hostname=gethostname())
        g = group(sig,)
        res = g()
        self.logger.info("res: %s", res.results)
        ip_addresses = kwargs["ip_addresses"].replace(" ", "").split(",")
        for ipaddr in ip_addresses:
            reach_check = tcp_ping(ipaddr, kwargs["port"])
            self.logger.info("Reachability check to %s:%s boolean result: %s", ipaddr, kwargs["port"], reach_check)
