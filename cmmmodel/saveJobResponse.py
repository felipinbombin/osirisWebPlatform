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

from scene.models import MetroLine, OperationPeriod, MetroTrack, MetroLineMetric
from viz.models import ModelAnswer

import pickle


def process_answer(answer_dict, execution_obj):
    """ fill viz table with answer dictionary """
    if execution_obj.model_id == 1:
        line_objs = MetroLine.objects.filter(scene=execution_obj.scene).order_by("id")
        operation_periods = OperationPeriod.objects.filter(scene=execution_obj.scene).order_by("id")
        metrics = ["Powerfc"]

        ModelAnswer.objects.filter(execution__model_id=execution_obj.model_id).delete()
        for metric in metrics:
            for line_obj in line_objs:
                track_objs = MetroTrack.objects.filter(metroLine=line_obj).order_by("id")
                # metro line metrics direction = going (g) or reverse (r)
                for direction in [0, 1]:
                    system_direction = MetroLineMetric.GOING if direction == 0 else MetroLineMetric.REVERSE
                    for operation_period in operation_periods:
                        for track_obj in track_objs:
                            line_id = line_obj.id - line_objs[0].id
                            op_id = operation_period.id - operation_periods[0].id
                            track_id = track_obj.id - track_objs[0].id
                            values = answer_dict[metric][line_id][direction][op_id][track_id]
                            for index, value in enumerate(values):
                                ModelAnswer.objects.create(execution=execution_obj, metroLine=line_obj,
                                                           direction=system_direction, operationPeriod=operation_period,
                                                           metroTrack=track_obj, attributeName=metric, order=index,
                                                           value=value)

    """
    for key, value in answer_dict.items():
        if isinstance(value, dict):
            for key2, value2 in value.items():
                if isinstance(value2, dict):
                    for key3, value3 in value2.items():
                        f.write("{} {} {} {}".format(key, key2, key3, value))
    """


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
