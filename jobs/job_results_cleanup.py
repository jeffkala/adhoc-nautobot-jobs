"""Jobs to manage job results."""

import datetime

from django.utils.timezone import make_aware
from nautobot.extras.jobs import IntegerVar, Job
from nautobot.extras.models import JobResult

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
        
        jobs_to_delete = JobResult.objects.filter(
            completed__lte=str(make_aware(datetime.datetime.now()) - datetime.timedelta(days=end_time))
        )
        for job_result in jobs_to_delete:
            if not commit:
                self.log_info(obj=job_result, message=f"{job_result} would be removed if Commit changes was selected.")
        if commit:
            jobs_to_delete.delete()
            self.log_success(obj=None, message=f"Job results older than {end_time} days old have been deleted.")


jobs = [ClearJobResultsJob]
