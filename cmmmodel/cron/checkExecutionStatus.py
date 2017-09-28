import os
import django
import logging

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "osirisWebPlatform.settings")
django.setup()

from django.utils import timezone
from django.db import transaction

from cmmmodel.models import ModelExecutionHistory, ModelExecutionQueue
from cmmmodel.views import getParamikoClient

CHECK_NUMBER = 2
# number of checks before change state

logger = logging.getLogger(__name__)


@transaction.atomic
def check_execution_is_running(client=None):
    """ check all process in status "running" if they finished in cmm cluster, executed by crontab app """

    if not ModelExecutionHistory.objects.filter(status=ModelExecutionHistory.RUNNING).exists():
        # nothing to do 
        return

    # retrieve active job number
    command = "squeue"
    if client is None:
        client = getParamikoClient()
    stdin, stdout, stderr = client.exec_command(command)

    # add log if there is an error with squeue
    if stderr.read().decode('utf-8') != "":
        logger.error(stderr.read().decode('utf-8'))
        return

    # skip first line
    stdout.readline()

    active_job_numbers = []
    # save job number
    for line in stdout:
        job_number = int(line.strip('\n').split(" ")[0])
        active_job_numbers.append(job_number)

    active_executions = ModelExecutionHistory.objects.filter(status=ModelExecutionHistory.RUNNING)

    for active_execution in active_executions:
        if active_execution.jobNumber in active_job_numbers:
            # nothing to do
            continue

        active_execution.check_answer += 1

        if active_execution.check_answer == CHECK_NUMBER:
            # change state

            # retrieve stdout and stderr from cluster
            command = "cat osiris/logs/archivo_{}.{}"

            _, stdout_out, stderr_out = client.exec_command(command.format(active_execution.jobNumber, "out"))
            _, stdout_err, stderr_err = client.exec_command(command.format(active_execution.jobNumber, "err"))

            # add log if there is an error with command
            if stderr_out.read().decode('utf-8') != "":
                logger.error(stderr_out.read().decode('utf-8'))
                continue
            if stderr_err.read().decode('utf-8') != "":
                logger.error(stderr_err.read().decode('utf-8'))
                continue

            active_execution.status = ModelExecutionHistory.ERROR_TO_COMMUNICATE_ANSWER
            active_execution.end = timezone.now()
            active_execution.std_out += stdout_out.read().decode('utf-8')
            active_execution.std_err += stdout_err.read().decode('utf-8')

            # deleted enqueued execution by this execution
            ModelExecutionQueue.objects.filter(modelExecutionHistory=active_execution).delete()

        active_execution.save()

