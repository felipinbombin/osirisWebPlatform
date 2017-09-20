# -*- coding: utf-8 -*-
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "osirisWebPlatform.settings")
import django
django.setup()
import sys

from django.db import transaction
from django.utils import timezone
from django.conf import settings
from cmmmodel.models import ModelExecutionHistory, ModelExecutionQueue
from cmmmodel.views import Run

import pickle


def process_answer(answer_dict, execution_obj):
    """ fill viz table with answer dictionary """
    for key, value in answer_dict.items():
        if isinstance(value, dict):
            print(key)
            process_answer(value, execution_obj)
        else:
            print(key, " : ", value)


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
            Run().runModel(execution_obj.scene, next_models[0], next_models[1:])


if __name__ == "__main__":
    """ update execution record """
    save_model_response(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
