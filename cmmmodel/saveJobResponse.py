# -*- coding: utf-8 -*-
from django.utils import timezone

from cmmmodel.models import ModelExecutionHistory, ModelExecutionQueue
from cmmmodel.views import Run
import sys


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
    """ load data with data given by args """
    saveModelResponse(sys.argv[1], sys.argv[2], sys.argv[3])
