from __future__ import unicode_literals

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

        # NAMES
        WORKSHEET_NAME = "Speed"
        DESCRIPTION = "Descripción"
        LINE_DESCRIPTION = "Línea"
        OP_DESCRIPTION = "Período operación"
        TRACK_DESCRIPTION = "Túnel"

        # attribute to save
        ATTR = "velDist"
        ATTR_NAME = "Velocidad [m/s]"
        ATTR2_NAME = "Distancia [m]"

        # data
        line_objs = list(MetroLine.objects.prefetch_related("metrotrack_set__startStation",
                                                            "metrostation_set__endstation").filter(scene=self.scene_obj).order_by("id"))
        operation_periods = list(OperationPeriod.objects.filter(scene=self.scene_obj).order_by("id"))

        stringIO = BytesIO()
        workbook = xlsxwriter.Workbook(stringIO, {'in_memory': True})
        excel_helper = ExcelHelper(workbook)

        worksheet = workbook.add_worksheet(WORKSHEET_NAME)

        first_column_index = 0
        first_row_index = 0

        current_row = first_row_index
        current_column = first_column_index
        # header
        corner = (current_row, first_column_index)
        excel_helper.makeTitleCell(worksheet, corner, DESCRIPTION, width=2)
        current_row += 1
        for description in [LINE_DESCRIPTION, OP_DESCRIPTION, TRACK_DESCRIPTION]:
            corner = (current_row, current_column)
            excel_helper.makeTitleCell(worksheet, corner, description)
            current_column += 1
        current_row += 1

        for line_obj in line_objs:
            track_objs = list(line_obj.metrotrack_set.all().order_by("id"))
            for operation_period in operation_periods:
                worksheet.write(current_row, 0, line_obj.name)
                worksheet.write(current_row, 1, operation_period.name)
                for direction in [0, 1]:
                    for track_index, track_obj in enumerate(track_objs):
                        current_column = 4
                        if direction == 1:
                            track_name = track_obj.get_name(direction=MetroLineMetric.REVERSE)
                        else:
                            track_name = track_obj.get_name()
                        worksheet.write(current_row, 2, track_name)

                        line_id = line_objs.index(line_obj)
                        op_id = operation_periods.index(operation_period)
                        track_id = track_objs.index(track_obj)

                        values = data[ATTR][line_id][direction][op_id][track_id]

                        worksheet.write(current_row, 3, ATTR2_NAME)
                        worksheet.write(current_row + 1, 3, ATTR_NAME)
                        for distance, value in enumerate(values):
                            worksheet.write(current_row, current_column, distance)
                            worksheet.write(current_row + 1, current_column, value)
                            current_column += 1

                        current_row += 3

        workbook.close()
        self.execution_obj.downloadFile.save("prueba.xlsx", ContentFile(stringIO.getvalue()))