# -*- coding: utf-8 -*-
import os
import sys
import pickle
import django
import gzip

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "osirisWebPlatform.settings")
django.setup()

from django.db import transaction
from django.utils import timezone
from django.conf import settings

from cmmmodel.models import ModelExecutionHistory, ModelExecutionQueue, CMMModel
from cmmmodel.clusterConnection import run_task
from cmmmodel.transform.processSpeedData import ProcessSpeedData
from cmmmodel.transform.processForceData import ProcessForceData
from cmmmodel.transform.processEnergyData import ProcessEnergyData
from cmmmodel.transform.processThermalData import ProcessThermalData


def process_answer(answer_dict, execution_obj):
    """ fill viz table with answer dictionary """
    processor = None

    if execution_obj.model_id == CMMModel.SPEED_MODEL_ID:
        processor = ProcessSpeedData(execution_obj)
        answer_dict = answer_dict["SM"]
    elif execution_obj.model_id == CMMModel.FORCE_MODEL_ID:
        processor = ProcessForceData(execution_obj)
        answer_dict = answer_dict["FM"]
    elif execution_obj.model_id == CMMModel.ENERGY_MODEL_ID:
        processor = ProcessEnergyData(execution_obj)
        answer_dict = answer_dict["EM"]
    elif execution_obj.model_id == CMMModel.THERMAL_MODEL_ID:
        processor = ProcessThermalData(execution_obj)
        # answer_dict = answer_dict["TM"]

    if processor is not None:
        processor.load(answer_dict)
        processor.create_excel_file(answer_dict)


def save_model_response(external_id, output_file_name, std_out, std_err):
    """ save model response  """

    with transaction.atomic():
        execution_obj = ModelExecutionHistory.objects.select_related("scene").get(externalId=external_id)
        execution_obj.end = timezone.now()
        execution_obj.status = ModelExecutionHistory.OK
        if std_err != "":
            execution_obj.status = ModelExecutionHistory.ERROR
        execution_obj.answer.name = os.path.join("modelOutput", output_file_name)
        execution_obj.std_out = std_out
        execution_obj.std_err += std_err
        execution_obj.save()

        # process output for viz
        file_path = os.path.join(settings.MODEL_OUTPUT_PATH, output_file_name)
        if os.path.isfile(file_path):
            with gzip.open(file_path, "rb") as answer_file:
                answer = pickle.load(answer_file)
                answer = answer["output"]
                process_answer(answer, execution_obj)

        # exec next model if exists
        next_models = ModelExecutionQueue.objects.filter(modelExecutionHistory=execution_obj).order_by('id').\
            values_list('model_id', flat=True)

        if len(next_models) >= 1:
            ModelExecutionQueue.objects.filter(modelExecutionHistory=execution_obj).delete()
            run_task(execution_obj.scene, next_models[0], next_models[1:])


if __name__ == "__main__":
    """ update execution record """
    save_model_response(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
