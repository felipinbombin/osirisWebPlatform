# -*- coding: utf-8 -*-
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "osirisWebPlatform.settings")
import django
django.setup()
import sys

from django.utils import timezone
from cmmmodel.models import ModelExecutionHistory, ModelExecutionQueue
from cmmmodel.views import Run


def save_model_response(external_id, std_out, std_err):
    """ save model response  """

    execution_obj = ModelExecutionHistory.objects.get(externalId=external_id)
    execution_obj.end = timezone.now()
    execution_obj.status = ModelExecutionHistory.OK
    execution_obj.answer = std_out
    execution_obj.error += std_err
    execution_obj.save()

    # exec next model if exists
    next_models = ModelExecutionQueue.objects.filter(modelExecutionHistory=execution_obj).order_by('id').\
        values_list('id', flat=True)

    if len(next_models) >= 1:
        Run().runModel(None, execution_obj.scene_id, next_models[0], next_models[1:])
        ModelExecutionQueue.objects.filter(modelExecutionHistory=execution_obj).delete()

if __name__ == "__main__":
    """ update execution record """
    save_model_response(sys.argv[1], sys.argv[2], sys.argv[3])
