from nautobot.apps.jobs import register_jobs
from .tcp_connection_check import ConnectivityCheckTask

jobs = [ConnectivityCheckTask]
register_jobs(*jobs)
