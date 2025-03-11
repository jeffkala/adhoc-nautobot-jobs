"""Nautobot Jobs."""
from nautobot.apps.jobs import register_jobs
from .command_getter import CommandExecution

jobs = (CommandExecution,)
register_jobs(*jobs)
