from abc import ABCMeta, abstractmethod

from cmmmodel.models import Model
from scene.models import MetroLine, MetroLineMetric, OperationPeriod
from viz.models import ModelAnswer

import numpy


class ProcessData:
    __metaclass__ = ABCMeta

    def __init__(self, model_id, execution_obj):
        self.model_id = model_id
        self.execution_obj = execution_obj
        self.scene_obj = execution_obj.scene

    def delete_previous_data(self):
        # delete data before insert a new one
        ModelAnswer.objects.filter(execution__model_id=self.model_id,
                                   execution__scene=self.scene_obj).delete()

    @abstractmethod
    def load(self, data):
        pass

    @abstractmethod
    def createExcelFile(self, data):
        pass


class ProcessSpeedData(ProcessData):

    def __init__(self, execution_obj):
        super(ProcessSpeedData, self).__init__(Model.SPEED_MODEL_ID, execution_obj)

        self.metrics = [
            {
                "name": "velDist"
            },
            {
                "name": "Speedlimit"
            }
        ]

    def load(self, data):
        self.delete_previous_data()
        line_objs = MetroLine.objects.prefetch_related("metrotrack_set").filter(scene=self.scene_obj).order_by("id")
        operation_periods = OperationPeriod.objects.filter(scene=self.scene_obj).order_by("id")

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
                                record = ModelAnswer(execution=self.execution_obj, metroLine=line_obj,
                                                     direction=system_direction,
                                                     operationPeriod=operation_period, metroTrack=track_obj,
                                                     attributeName=metric["name"], order=index, value=value)
                                object_list.append(record)

            ModelAnswer.objects.bulk_create(object_list)
            del object_list[:]

    def createExcelFile(self, data):
        pass