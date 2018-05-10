from __future__ import unicode_literals

from io import BytesIO
from itertools import islice

import numpy
import xlsxwriter
from django.core.files.base import ContentFile
from django.utils import timezone

from cmmmodel.models import CMMModel
from cmmmodel.transform.processData import ProcessData
from scene.models import MetroLine, MetroLineMetric, OperationPeriod
from scene.views.ExcelWriter import ExcelHelper
from viz.models import ModelAnswer


class ProcessSpeedData(ProcessData):
    def __init__(self, execution_obj):
        super(ProcessSpeedData, self).__init__(CMMModel.SPEED_MODEL_ID, execution_obj)

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

        def data_generator():
            for metric in self.metrics:
                for line_index, line_obj in enumerate(line_objs):
                    track_objs = line_obj.metrotrack_set.all().order_by("id")
                    # metro line metrics direction = going (g) or reverse (r)
                    for direction in [0, 1]:
                        system_direction = MetroLineMetric.GOING if direction == 0 else MetroLineMetric.REVERSE
                        for op_index, operation_period in enumerate(operation_periods):
                            for track_index, track_obj in enumerate(track_objs):
                                values = data[metric["name"]][line_index][direction][op_index][track_index]

                                if not isinstance(values, numpy.ndarray):
                                    values = [values]

                                for index, value in enumerate(values):
                                    record = ModelAnswer(execution=self.execution_obj, metroLine=line_obj,
                                                         direction=system_direction,
                                                         operationPeriod=operation_period, metroTrack=track_obj,
                                                         attributeName=metric["name"], order=index, value=value)
                                    yield record

        batch_size = 10000
        generator = data_generator()
        while True:
            batch = list(islice(generator, batch_size))
            if not batch:
                break
            ModelAnswer.objects.bulk_create(batch, batch_size)

    def create_excel_file(self, data):

        # NAMES
        FILE_NAME = "Velocidad"
        FILE_EXTENSION = ".xlsx"

        WORKSHEET_NAME = "Speed"
        DESCRIPTION = "Descripción"
        LINE_DESCRIPTION = "Línea"
        OP_DESCRIPTION = "Período operación"
        TRACK_DESCRIPTION = "Túnel"

        # attribute to save
        ATTR = "velDist"

        # attribute name and its reference (distance)
        ATTR_NAMES = ["Distancia [m]", "Velocidad [m/s]"]

        # data
        line_objs = MetroLine.objects.prefetch_related("metrotrack_set__startStation",
                                                       "metrostation_set__endstation").filter(
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
            track_objs = line_obj.metrotrack_set.all().order_by("id")
            for op_index, operation_period in enumerate(operation_periods):
                for direction in [0, 1]:
                    worksheet.write(current_row, 0, line_obj.name)
                    worksheet.write(current_row, 1, operation_period.name)

                    track_objs_iter = track_objs
                    if direction == 1:
                        track_objs_iter = reversed(track_objs)

                    for track_index, track_obj in enumerate(track_objs_iter):
                        current_column = 4
                        if direction == 1:
                            track_name = track_obj.get_name(direction=MetroLineMetric.REVERSE)
                        else:
                            track_name = track_obj.get_name()
                        worksheet.write(current_row, 2, track_name)

                        values = data[ATTR][line_index][direction][op_index][track_index]

                        for index, attr_name in enumerate(ATTR_NAMES):
                            worksheet.write(current_row + index, 3, attr_name)

                        for distance, value in enumerate(values):
                            worksheet.write(current_row, current_column, distance)
                            worksheet.write(current_row + 1, current_column, value)
                            current_column += 1

                        current_row += 3

        workbook.close()
        now = timezone.now().replace(microsecond=0)
        self.execution_obj.timestampFile = now
        self.execution_obj.downloadFile.save("{}_{}{}".format(FILE_NAME, now, FILE_EXTENSION),
                                             ContentFile(string_io.getvalue()))
