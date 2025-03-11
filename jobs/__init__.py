"""Nautobot Jobs."""
from nautobot.apps.jobs import register_jobs
from .command_getter import RunCommand

jobs = [RunCommand]
register_jobs(*jobs)
