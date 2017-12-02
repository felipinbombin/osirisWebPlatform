from __future__ import unicode_literals
from django.utils import timezone

from cmmmodel.transform.processData import ProcessData
from cmmmodel.models import Model
from scene.models import MetroLine, MetroLineMetric, OperationPeriod
from scene.views.ExcelWriter import ExcelHelper
from viz.models import ModelAnswer

from django.core.files.base import ContentFile

from io import BytesIO

import numpy
import xlsxwriter


class ProcessForceData(ProcessData):
    def __init__(self, execution_obj):
        super(ProcessForceData, self).__init__(Model.FORCE_MODEL_ID, execution_obj)

        self.metrics = [
            {
                "name": "Potencia_drive_LR",
                "direction": MetroLineMetric.GOING
            },
            {
                "name": "Tiempo_LR",
                "direction": MetroLineMetric.GOING
            },
            {
                "name": "Potencia_ESS_LR",
                "direction": MetroLineMetric.GOING
            },
            {
                "name": "Potencia_drive_RL",
                "direction": MetroLineMetric.REVERSE
            },
            {
                "name": "Tiempo_RL",
                "direction": MetroLineMetric.REVERSE
            },
            {
                "name": "Potencia_ESS_RL",
                "direction": MetroLineMetric.REVERSE
            }
        ]

    def load(self, data):
        self.delete_previous_data()
        line_objs = MetroLine.objects.filter(scene=self.scene_obj).order_by("id")
        operation_periods = OperationPeriod.objects.filter(scene=self.scene_obj).order_by("id")

        object_list = []

        for metric in self.metrics:
            for line_index, line_obj in enumerate(line_objs):
                for op_index, operation_period in enumerate(operation_periods):
                    values = data[metric["name"]][line_index][op_index]
                    if not isinstance(values, numpy.ndarray):
                        values = [values]

                    for index, value in enumerate(values):
                        record = ModelAnswer(execution=self.execution_obj, metroLine=line_obj,
                                             direction=metric["direction"], metroTrack=None,
                                             operationPeriod=operation_period,
                                             attributeName=metric["name"], order=index, value=value)
                        object_list.append(record)

            ModelAnswer.objects.bulk_create(object_list)
            del object_list[:]

    def create_excel_file(self, data):

        # NAMES
        FILE_NAME = "Fuerza"
        FILE_EXTENSION = ".xlsx"

        WORKSHEET_NAME = "Traction"
        DESCRIPTION = "Descripción"
        LINE_DESCRIPTION = "Línea"
        OP_DESCRIPTION = "Período operación"
        TRACK_DESCRIPTION = "Túnel"

        # attribute to save
        ATTRS = ["Tiempo_LR", "Potencia_drive_LR", "Potencia_ESS_LR",
                 "Tiempo_RL", "Potencia_drive_RL", "Potencia_ESS_RL"]

        # attribute name and its reference (distance)
        ATTR_NAMES = ["Time [s]", "Consumed Traction Power[W]", "Provided ESS Power[W]",
                      "Time [s]", "Consumed Traction Power[W]", "Provided ESS Power[W]"]

        # data
        line_objs = MetroLine.objects.prefetch_related("metrostation_set").filter(
            scene=self.scene_obj).order_by("id")
        operation_periods = OperationPeriod.objects.filter(scene=self.scene_obj).order_by("id")

        string_io = BytesIO()
        workbook = xlsxwriter.Workbook(string_io, {'in_memory': True})
        excel_helper = ExcelHelper(workbook)

        worksheet = workbook.add_worksheet(WORKSHEET_NAME)

        first_column_index = 0
        first_row_index = 0

        current_row = first_row_index
        current_column = first_column_index
        # header
        corner = (current_row, first_column_index)
        excel_helper.make_title_cell(worksheet, corner, DESCRIPTION, width=2)
        current_row += 1
        for description in [LINE_DESCRIPTION, OP_DESCRIPTION, TRACK_DESCRIPTION]:
            corner = (current_row, current_column)
            excel_helper.make_title_cell(worksheet, corner, description)
            current_column += 1
        current_row += 1

        for line_index, line_obj in enumerate(line_objs):
            for op_index, operation_period in enumerate(operation_periods):
                for attr_name_index, attr_name in enumerate(ATTR_NAMES):
                    worksheet.write(current_row + attr_name_index, 3, attr_name)

                for attr_index, attr in enumerate(ATTRS):
                    if not attr_index % (len(ATTRS)/2):
                        worksheet.write(current_row, 0, line_obj.name)
                        worksheet.write(current_row, 1, operation_period.name)
                        system_direction = MetroLineMetric.GOING if attr[-2:] == "LR" else MetroLineMetric.REVERSE
                        worksheet.write(current_row, 2, line_obj.get_direction_name(system_direction))
                    values = data[attr][line_index][op_index]
                    current_column = 4
                    for time, value in enumerate(values):
                        worksheet.write(current_row, current_column, value)
                        current_column += 1
                    current_row += 1
                current_row += 1

        workbook.close()
        now = timezone.now().replace(microsecond=0)
        self.execution_obj.timestampFile = now
        self.execution_obj.downloadFile.save("{}_{}{}".format(FILE_NAME, now, FILE_EXTENSION),
                                             ContentFile(string_io.getvalue()))
