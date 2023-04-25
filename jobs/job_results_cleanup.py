"""Jobs to manage the reservation portal."""

import datetime
import logging

from django.utils.timezone import make_aware
from nautobot.extras.jobs import IntegerVar, Job
from nautobot.extras.models import JobResult

LOGGER = logging.getLogger(__name__)

name = "Database Object Cleanups"  # pylint: disable=invalid-name


class ClearJobResultsJob(Job):
    """Class definition to clean up old Job Results."""

    days_to_keep = IntegerVar(required=True, default=30)

    class Meta:  # pylint: disable=too-few-public-methods
        """Meta object boilerplate for reservations."""

        name = "Clean up old job results."
        description = "Remove and clean up old job results."
        commit_default = True
        has_sensitive_variables = False

    def run(self, data, commit):
        """Run a job to remove legacy reservations."""
        end_time = data.get("days_to_keep")

        for job_result in JobResult.objects.filter(
            end_time__lte=str(make_aware(datetime.datetime.now()) - datetime.timedelta(days=end_time))
        ):
            self.log_info(obj=job_result, message=f"{job_result} to be removed")
            if commit:
                job_result.delete()


jobs = [ClearJobResultsJob]
