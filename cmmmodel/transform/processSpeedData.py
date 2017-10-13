from cmmmodel.transform.processData import ProcessData
from cmmmodel.models import Model
from scene.models import MetroLine, MetroLineMetric, OperationPeriod
from scene.views.ExcelWriter import ExcelHelper
from viz.models import ModelAnswer

from django.core.files.base import ContentFile

from io import BytesIO

import numpy
import xlsxwriter


class ProcessSpeedData(ProcessData):

    def __init__(self, execution_obj):
        super(ProcessSpeedData, self).__init__(Model.SPEED_MODEL_ID, execution_obj)

        self.metrics = [
            {
                "name": "velDist"
            },
            {
                "name": "Speedlimit"
            },
            {
                "name": "Time"
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

    def create_excel_file(self, data):
        line_objs = MetroLine.objects.prefetch_related("metrotrack_set").filter(scene=self.scene_obj).order_by("id")
        operation_periods = OperationPeriod.objects.filter(scene=self.scene_obj).order_by("id")

        stringIO = BytesIO()
        workbook = xlsxwriter.Workbook(stringIO, {'in_memory': True})
        excel_helper = ExcelHelper(workbook)

        # create worksheets
        for line_obj in line_objs:
            worksheet = workbook.add_worksheet(line_obj.name)
            station_name_list = [station.name for station in line_obj.metrostation_set.all().order_by("id")]
            for metric in data.keys():
                excel_helper.makeParamHeader(worksheet, (0, 0), station_name_list, metric, ["1", "2"])

        for metric in data.keys():
            print(metric)
            for line_obj in line_objs:
                track_objs = line_obj.metrotrack_set.all().order_by("id")

                worksheet = workbook.get_worksheet_by_name(line_obj.name)

                for direction in [0, 1]:
                    system_direction = MetroLineMetric.GOING if direction == 0 else MetroLineMetric.REVERSE

                    for operation_period in operation_periods:
                        for track_index, track_obj in enumerate(track_objs):
                            line_id = line_obj.id - line_objs[0].id
                            op_id = operation_period.id - operation_periods[0].id
                            track_id = track_obj.id - track_objs[0].id
                            values = data[metric][line_id][direction][op_id][track_id]

        workbook.close()
        self.execution_obj.downloadFile.save("prueba.xlsx", ContentFile(stringIO.getvalue()))