# -*- coding: utf-8 -*-
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "osirisWebPlatform.settings")
django.setup()

from django.db import transaction
from django.utils import timezone
from django.conf import settings

from cmmmodel.models import ModelExecutionHistory, ModelExecutionQueue, Model
from cmmmodel.clusterConnection import run_task
from cmmmodel.transform.processSpeedData import ProcessSpeedData

import sys
import pickle


def process_answer(answer_dict, execution_obj):
    """ fill viz table with answer dictionary """
    processor = None
    if execution_obj.model_id == Model.SPEED_MODEL_ID:
        processor = ProcessSpeedData(execution_obj)
    elif execution_obj.model_id == Model.STRONG_MODEL_ID:
        pass
    elif execution_obj.model_id == Model.ENERGY_MODEL_ID:
        pass
    elif execution_obj.model_id == Model.TEMPERATURE_MODEL_ID:
        pass

    if processor is not None:
        processor.load(answer_dict)
        processor.createExcelFile(answer_dict)

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
            with open(file_path, "rb") as answer_file:
                answer = pickle.load(answer_file)
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
