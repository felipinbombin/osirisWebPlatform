# -*- coding: utf-8 -*-
from django.db import transaction
from django.conf import settings
from django.utils import timezone

from io import BytesIO

from cmmmodel.models import ModelExecutionHistory, CMMModel, ModelExecutionQueue
from cmmmodel.firstInput import first_input
from scene.models import Scene
from energycentermodel.read_data import datos_ac, datos_dc
from energycentermodel.models import Bitacora_trenes

import paramiko
import os
import uuid
import pickle
import gzip
import pytz


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
        model_obj = CMMModel.objects.get(id=model_id)

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
        input_file_name = "{0}.model_input".format(external_id)
        destination = "osiris/inputs/{0}".format(input_file_name)

        # gzipped file before sending to cluster
        file_obj = BytesIO()
        gzip_file = gzip.GzipFile(fileobj=file_obj, mode='wb')
        gzip_file.write(model_input_data)
        gzip_file.close()
        # move to beginning of file
        file_obj.seek(0)

        sftp = client.open_sftp()
        sftp.putfo(file_obj, destination)
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


class PreviousModelDidNotFinishWellException(Exception):
    pass


def get_input_data(scene_id, model_id):
    """ get input data to run model """

    if model_id == 999:
        # for testing purpose
        input_dict = {
            "seconds": 60
        }
        input_dict = pickle.dumps(input_dict, protocol=pickle.HIGHEST_PROTOCOL)
    elif model_id == CMMModel.SPEED_MODEL_ID:
        input_dict = first_input(scene_id)
        input_dict = {
            "input": input_dict,
            "output": {}
        }
        input_dict = pickle.dumps(input_dict, protocol=pickle.HIGHEST_PROTOCOL)
    else:
        previous_model = CMMModel.objects.get(id=model_id).modelRequired
        model_obj = ModelExecutionHistory.objects.filter(scene_id=scene_id,
                                                         model_id=previous_model).order_by("-start").first()
        if model_obj is None:
            raise ModelInputDoesNotExistException
        elif model_obj.status != ModelExecutionHistory.OK:
            raise PreviousModelDidNotFinishWellException

        with gzip.open(model_obj.answer.path, mode="rb") as answer_file:
            input_dict = answer_file.read()

            if model_id == CMMModel.ENERGY_CENTER_MODEL_ID:
                # add additional data
                input_dict = pickle.loads(input_dict)

                # save trains in bitacora_trenes table
                train_schedule = input_dict['output']['EM']['bitacora']

                for line_name in train_schedule:
                    for via in train_schedule[line_name]:
                        for train_name in train_schedule[line_name][via]:
                            print(len(train_schedule[line_name][via][train_name]))
                            """
                            for row in train_schedule[line_name][via][train_name]:
                                date = pytz.timezone(settings.TIME_ZONE).localize(row[0])
                                query_set = Bitacora_trenes.objects.filter(Tren_ID=train_name, Linea_ID=line_name,
                                                                           Fecha=date, Via=via)
                                with transaction.atomic():
                                    if not query_set.exists():
                                        Bitacora_trenes.objects.create(Tren_ID=train_name, Linea_ID=line_name, Fecha=date,
                                                                       Via=via, Posicion=row[1], Velocidad=row[2],
                                                                       Aceleracion=row[3], Potencia=row[4])
                                    else:
                                        query_set.update(Posicion=row[1], Velocidad=row[2], Aceleracion=row[3],
                                                         Potencia=row[4])
                            """

                input_dict['input']['ECM'] = {
                    'ac_data': datos_ac('Cochrane', '2017-01-01 00:00:00', '2017-01-01 23:59:00'),
                    'dc_data': datos_dc('Linea1', '2017-01-01 00:00:00', '2017-01-01 23:59:00')
                }
                input_dict = pickle.dumps(input_dict, protocol=pickle.HIGHEST_PROTOCOL)

    return input_dict
