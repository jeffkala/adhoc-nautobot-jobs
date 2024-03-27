"""Register all the jobs."""

from nautobot.apps.jobs import register_jobs
from .tcp_connection_check import ConnectivityCheckTask
from .nbc_secret_rotation import CloudSecretRotation

jobs = [ConnectivityCheckTask, CloudSecretRotation]
register_jobs(*jobs)
