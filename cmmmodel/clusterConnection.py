# -*- coding: utf-8 -*-
from django.db import transaction
from django.conf import settings
from django.utils import timezone

from io import BytesIO

from cmmmodel.models import ModelExecutionHistory, Model, ModelExecutionQueue
from cmmmodel.firstInput import first_input
from scene.models import Scene

import paramiko
import os
import uuid
import pickle


class EnqueuedModelException(Exception):
    pass


class ModelIsRunningException(Exception):
    pass


class IncompleteSceneException(Exception):
    pass


def get_paramiko_client():
    """ create ssh connection to cmm cluster """
    key_path = os.path.join(settings.KEY_DIR, 'ssh_key')

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    k = paramiko.RSAKey.from_private_key_file(key_path)
    client.connect(hostname=settings.CLUSTER_URL, username=settings.CLUSTER_USER, pkey=k)

    return client


def run_task(scene_obj, model_id, next_model_ids):
    """ connect to cluster server and run model """

    with transaction.atomic():
        model_obj = Model.objects.get(id=model_id)

        if scene_obj.status == Scene.INCOMPLETE:
            raise IncompleteSceneException

        # if model you try to run is enqueued, don´t run and notify to user
        if ModelExecutionQueue.objects.filter(modelExecutionHistory__scene=scene_obj, model_id=model_id).exists():
            raise EnqueuedModelException
        elif ModelExecutionHistory.objects.filter(scene=scene_obj, model_id=model_id,
                                                  status=ModelExecutionHistory.RUNNING).exists():
            raise ModelIsRunningException

        client = get_paramiko_client()

        # run model
        response_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'saveJobResponse.py')
        external_id = uuid.uuid4()

        # create file with serialized input model data
        model_input_data = get_input_data(scene_obj.id, model_id)
        input_file_name = "{}.model_input".format(external_id)
        destination = "osiris/inputs/" + input_file_name

        sftp = client.open_sftp()
        sftp.putfo(BytesIO(model_input_data), destination)
        sftp.close()

        command = "sbatch ~/osiris/runModel.sh {} {} \"{}\" {} \"{}\" {} {}".format(settings.SERVER_IP,
                                                                                    response_script,
                                                                                    settings.PYTHON_COMMAND,
                                                                                    external_id,
                                                                                    input_file_name,
                                                                                    model_obj.clusterExecutionId,
                                                                                    settings.MODEL_OUTPUT_PATH)

        stdin, stdout, stderr = client.exec_command(command)

        job_number = None
        # save job number
        for line in stdout:
            job_number = int(line.strip('\n').split(" ")[3])

        if job_number is None:
            status = ModelExecutionHistory.ERROR_TO_START
        else:
            status = ModelExecutionHistory.RUNNING

        meh = ModelExecutionHistory.objects.create(scene=scene_obj, model=model_obj, start=timezone.now(),
                                                   status=status, jobNumber=job_number, externalId=external_id,
                                                   std_err=stderr.read().decode('utf-8'))

        for model_id in next_model_ids:
            ModelExecutionQueue.objects.create(modelExecutionHistory=meh, model_id=model_id)
        # close ssh connection
        client.close()


def cancel_task(scene_obj, model_id):
    """ cancel cluster task """
    model_execution = ModelExecutionHistory.objects.get(scene=scene_obj, model_id=model_id,
                                                        status=ModelExecutionHistory.RUNNING)

    command = "scancel {}".format(model_execution.jobNumber)
    client = get_paramiko_client()
    stdin, stdout, stderr = client.exec_command(command)

    model_execution.status = ModelExecutionHistory.CANCEL
    model_execution.end = timezone.now()
    model_execution.std_out += stdout.read().decode('utf-8')
    model_execution.std_err += stderr.read().decode('utf-8')
    model_execution.save()

    ModelExecutionQueue.objects.filter(modelExecutionHistory=model_execution).delete()


class ModelInputDoesNotExistException(Exception):
    pass


def get_input_data(scene_id, model_id):
    """ get input data to run model """

    if model_id == 999:
        # for testing purpose
        input_dict = {
            "seconds": 60
        }
        input_dict = pickle.dumps(input_dict, protocol=pickle.HIGHEST_PROTOCOL)
    elif model_id == Model.SPEED_MODEL_ID:
        input_dict = first_input(scene_id)
        input_dict = {
            "input": input_dict,
            "output": {}
        }
        input_dict = pickle.dumps(input_dict, protocol=pickle.HIGHEST_PROTOCOL)
    else:
        previous_model = model_id - 1
        model_obj = ModelExecutionHistory.objects.filter(status=ModelExecutionHistory.OK,
                                                         scene_id=scene_id,
                                                         model_id=previous_model).order_by("-end").first()
        if model_obj is None:
            raise ModelInputDoesNotExistException

        with open(model_obj.answer.path, mode="rb") as answer_file:
            input_dict = answer_file.read()

    return input_dict