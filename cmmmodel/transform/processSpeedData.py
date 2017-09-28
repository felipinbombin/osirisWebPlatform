from abc import ABCMeta, abstractmethod

from scene.models import MetroLine, MetroTrack, MetroLineMetric, OperationPeriod
from viz.models import ModelAnswer

import numpy


class ProcessData:
    __metaclass__ = ABCMeta

    MODEL_ID = None

    def __init__(self):
        pass

    def delete_previous_data(self, scene_obj):
        # delete data before insert a new one
        ModelAnswer.objects.filter(execution__model_id=self.MODEL_ID,
                                   execution__scene=scene_obj).delete()

    @abstractmethod
    def load(self, data, execution_obj):
        pass


class ProcessSpeedData(ProcessData):
    MODEL_ID = 1

    def __init__(self):
        super(ProcessSpeedData, self).__init__()

        self.metrics = [
            {
                "name": "velDist"
            },
            {
                "name": "Time"
            },
            {
                "name": "Speedlimit"
            },
            {
                "name": "Distance"
            }
        ]

    def load(self, data, execution_obj):
        scene_obj = execution_obj.scene
        self.delete_previous_data(execution_obj.scene)

        line_objs = MetroLine.objects.prefetch_related("metrotrack_set").filter(scene=scene_obj).order_by("id")
        operation_periods = OperationPeriod.objects.filter(scene=scene_obj).order_by("id")

        self.delete_previous_data(scene_obj)

        object_list = []

        for metric in self.metrics:
            for line_obj in line_objs:
                track_objs = line_obj.metrotrack_set.all().order_by("id")
                # metro line metrics direction = going (g) or reverse (r)
                for direction in [0, 1]:
                    system_direction = MetroLineMetric.GOING if direction == 0 else MetroLineMetric.REVERSE
                    for operation_period in operation_periods:
                        for track_index, track_obj in enumerate(track_objs):
                            line_id = line_obj.id - line_objs[0].id
                            op_id = operation_period.id - operation_periods[0].id
                            track_id = track_obj.id - track_objs[0].id
                            values = data[metric["name"]][line_id][direction][op_id][track_id]

                            if not isinstance(values, numpy.ndarray):
                                values = [values]
                            for index, value in enumerate(values):
                                record = ModelAnswer(execution=execution_obj, metroLine=line_obj,
                                                     direction=system_direction,
                                                     operationPeriod=operation_period, metroTrack=track_obj,
                                                     attributeName=metric["name"], order=index, value=value)
                                object_list.append(record)

            ModelAnswer.objects.bulk_create(object_list)
            del object_list[:]