# -*- coding: utf-8 -*-
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "osirisWebPlatform.settings")
import django
django.setup()
import sys

from django.utils import timezone
from cmmmodel.models import ModelExecutionHistory, ModelExecutionQueue
from cmmmodel.views import Run

def saveModelResponse(job_number, std_out, std_err):
    """ save model response  """
    #TODO: verify if it had problem

    execution_obj = ModelExecutionHistory.objects.get(jobNumber=job_number)
    execution_obj.end=timezone.now()
    execution_obj.answer=std_out
    execution_obj.error += std_err
    execution_obj.save()

    # exec next model if exists
    next_models = ModelExecutionQueue.objects.filter(modelExecutionHistory=execution_obj).order_by('id').\
        values_list('id', flat=True)

    Run().runModel(None, execution_obj.scene_id, next_models[0], next_models[1:])
    ModelExecutionQueue.objects.filter(modelExecutionHistory=execution_obj).delete()

if __name__ == "__main__":
    """ update execution record """
    saveModelResponse(sys.argv[1], sys.argv[2], sys.argv[3])
