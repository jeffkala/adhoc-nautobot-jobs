"""Register all the jobs."""

from nautobot.apps.jobs import register_jobs
from .tcp_connection_check import ConnectivityCheckTask
from .nbc_secret_rotation import CloudSecretRotationv1, CloudSecretRotationv2

jobs = [ConnectivityCheckTask, CloudSecretRotationv1, CloudSecretRotationv2]
register_jobs(*jobs)
