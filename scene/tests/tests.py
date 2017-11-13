# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.urls import reverse
from django.conf import settings

from collections import defaultdict

from scene.models import MetroLineMetric
from scene.statusResponse import Status
from cmmmodel.firstInput import first_input
from .testHelper import TestHelper

import os
import json

TOPOLOGIC_FILE_NAME = "Escenario_topologico.xlsx"
SYSTEMIC_FILE_NAME = "Escenario_sistemico.xlsx"
OPERATION_FILE_NAME = "Escenario_operacion.xlsx"
SPEED_FILE_NAME = "Escenario_velocidad.xlsx"


class CompleteSceneDataTest(TestCase):
    """
    test for scene wizard
    """

    def setUp(self):
        """
            create user and log in
        """
        self.testHelper = TestHelper(self)

        self.client = self.testHelper.get_logged_client()

        # create scene
        self.scene_name = "Escenario 1"
        self.scene_obj = self.testHelper.create_scene(self.scene_name)

        self.FILE_PATH, _ = os.path.split(os.path.abspath(__file__))

    def tearDown(self):
        """ executed after every test """
        self.scene_obj = self.testHelper.get_scene_obj(self.scene_name)

        # delete uploaded files
        if self.scene_obj.step1File:
            os.remove(os.path.join(settings.MEDIA_ROOT, str(self.scene_obj.step1File)))
        if self.scene_obj.step3File:
            os.remove(os.path.join(settings.MEDIA_ROOT, str(self.scene_obj.step3File)))
        if self.scene_obj.step5File:
            os.remove(os.path.join(settings.MEDIA_ROOT, str(self.scene_obj.step5File)))
        if self.scene_obj.step6File:
            os.remove(os.path.join(settings.MEDIA_ROOT, str(self.scene_obj.step6File)))

    def check_step_0(self):
        """ simulate upload data for step 0 """
        STEP_0_JSON_FILE_NAME = "step0_data.json"
        STEP_0_URL = reverse("scene:validation", kwargs={"step_id": 0, "scene_id": self.scene_obj.id})

        with open(os.path.join(self.FILE_PATH, STEP_0_JSON_FILE_NAME)) as fp:
            data = json.loads(fp.read())
            self.testHelper.make_post_request(STEP_0_URL, json.dumps(data), "application/json")

            # check data was created correctly
            self.scene_obj = self.testHelper.get_scene_obj(self.scene_name, with_related=True)
            lines = self.scene_obj.metroline_set.all().order_by("id")

            for json_line, line_obj in zip(data["lines"], lines):
                self.assertEqual(json_line["name"], line_obj.name)
                self.assertIsNotNone(line_obj.externalId)

                for json_station, stationObj in zip(json_line["stations"],
                                                    line_obj.metrostation_set.all().order_by("id")):
                    self.assertEqual(json_station["name"], stationObj.name)
                    self.assertIsNotNone(stationObj.externalId)

                for json_depot, depotObj in zip(json_line["depots"], line_obj.metrodepot_set.all().order_by("id")):
                    self.assertEqual(json_depot["name"], depotObj.name)
                    self.assertIsNotNone(depotObj.externalId)

    def check_step_1(self):
        """ simulate step 1 process """
        STEP_1_URL = reverse("scene:validation", kwargs={"step_id": 1, "scene_id": self.scene_obj.id})
        self.testHelper.make_post_request(STEP_1_URL, {})

    def check_step_2(self):
        """ simulate step 2 process """
        STEP_2_JSON_FILE_NAME = "step2_data.json"
        STEP_2_URL = reverse("scene:validation", kwargs={"step_id": 2, "scene_id": self.scene_obj.id})

        with open(os.path.join(self.FILE_PATH, STEP_2_JSON_FILE_NAME)) as fp:
            data = json.loads(fp.read())
            self.testHelper.make_post_request(STEP_2_URL, json.dumps(data), "application/json")

            # check data was created correctly
            self.scene_obj = self.testHelper.get_scene_obj(self.scene_name, with_related=True)

            self.assertEqual(self.scene_obj.systemicparams_set.all().count(), 1)

            params = self.scene_obj.systemicparams_set.first()

            for name, value in params.__dict__.items():
                if isinstance(value, float):
                    self.assertEqual(value, data["systemicParams"][name])

    def check_step_3(self):
        """ simulate step 3 process """
        STEP_3_URL = reverse("scene:validation", kwargs={"step_id": 3, "scene_id": self.scene_obj.id})
        self.testHelper.make_post_request(STEP_3_URL, {})

    def check_step_4(self):
        """ simulate step 4 process """
        STEP_4_JSON_FILE_NAME = "step4_data.json"
        STEP_4_URL = reverse("scene:validation", kwargs={"step_id": 4, "scene_id": self.scene_obj.id})

        with open(os.path.join(self.FILE_PATH, STEP_4_JSON_FILE_NAME)) as fp:
            data = json.loads(fp.read())
            self.testHelper.make_post_request(STEP_4_URL, json.dumps(data), "application/json")

            # check data was created correctly
            self.scene_obj = self.testHelper.get_scene_obj(self.scene_name, with_related=True)

            self.assertEqual(self.scene_obj.annualTemperatureAverage, float(data["annualTemperatureAverage"]))
            self.assertEqual(self.scene_obj.averageMassOfAPassanger, float(data["averageMassOfAPassanger"]))
            self.assertEqual(self.scene_obj.operationperiod_set.all().count(), 2)

            for period_obj, period_data in zip(self.scene_obj.operationperiod_set.all().order_by("id"),
                                               data["operationPeriods"]):
                for name, value in period_obj.__dict__.items():
                    if isinstance(value, float):
                        self.assertEqual(value, float(period_data[name]))

    def check_step_5(self):
        """ simulate step 5 process """
        STEP_5_URL = reverse("scene:validation", kwargs={"step_id": 5, "scene_id": self.scene_obj.id})
        self.testHelper.make_post_request(STEP_5_URL, {})

    def check_step_6(self):
        """ simulate step 6 process """
        STEP_6_URL = reverse("scene:validation", kwargs={"step_id": 6, "scene_id": self.scene_obj.id})
        self.testHelper.make_post_request(STEP_6_URL, {})

    def upload_topologic_file(self):
        """ simulate step 1 uploading excel file """
        UPLOAD_TOPOLOGIC_FILE_URL = reverse("scene:uploadTopologicFile", kwargs={"scene_id": self.scene_obj.id})

        # upload file
        with open(os.path.join(self.FILE_PATH, TOPOLOGIC_FILE_NAME), "rb") as fp:
            data = {"file": fp}
            response = self.client.post(UPLOAD_TOPOLOGIC_FILE_URL, data)

            self.assertEqual(response.status_code, 200)
            status = json.loads(response.content.decode("utf-8"))["status"]
            self.assertEqual(status["code"], Status.getJsonStatus(Status.OK, {})["status"]["code"])

            self.scene_obj = self.testHelper.get_scene_obj(self.scene_name, with_related=True)

            metric_length = [9, 11]
            for index, line_obj in enumerate(self.scene_obj.metroline_set.all().order_by("id")):
                self.assertEqual(line_obj.metrotrack_set.count(), line_obj.metrostation_set.count() - 1)

                for track_obj in line_obj.metrotrack_set.all():
                    self.assertIsNotNone(track_obj.crossSection)
                    self.assertIsNotNone(track_obj.averagePerimeter)
                    self.assertIsNotNone(track_obj.length)
                    self.assertIsNone(track_obj.auxiliariesConsumption)
                    self.assertIsNone(track_obj.ventilationConsumption)

                for station_obj in line_obj.metrostation_set.all():
                    self.assertIsNotNone(station_obj.length)
                    self.assertIsNotNone(station_obj.platformSection)
                    self.assertIsNotNone(station_obj.platformAveragePerimeter)
                    self.assertIsNotNone(station_obj.secondLevelAverageHeight)
                    self.assertIsNotNone(station_obj.secondLevelFloorSurface)

                metric_dict = defaultdict(list)
                for metric_obj in line_obj.metrolinemetric_set.all():
                    self.assertIsNotNone(metric_obj.start)
                    self.assertIsNotNone(metric_obj.end)
                    self.assertIsNotNone(metric_obj.value)

                    metric_id = metric_obj.metric + "-" + str(metric_obj.direction)
                    metric_dict[metric_id].append(metric_obj)

                params = [MetroLineMetric.SLOPE, MetroLineMetric.CURVE_RADIUS, MetroLineMetric.SPEED_LIMIT,
                          MetroLineMetric.GROUND]

                for param in params:
                    for direction in [MetroLineMetric.GOING, MetroLineMetric.REVERSE, None]:
                        metric_id = param + "-" + str(direction)
                        if metric_id in metric_dict:
                            self.assertEqual(len(metric_dict[metric_id]), metric_length[index])

            self.assertIsNotNone(self.scene_obj.timeStampStep1File)

    def upload_systemic_file(self):
        """ simulate step 3 uploading excel file """
        UPLOAD_SYSTEMIC_FILE_URL = reverse("scene:uploadSystemicFile", kwargs={"scene_id": self.scene_obj.id})

        # upload file
        with open(os.path.join(self.FILE_PATH, SYSTEMIC_FILE_NAME), "rb") as fp:
            data = {"file": fp}
            response = self.client.post(UPLOAD_SYSTEMIC_FILE_URL, data)

            self.assertEqual(response.status_code, 200)
            status = json.loads(response.content.decode("utf-8"))["status"]
            self.assertEqual(status["code"], Status.getJsonStatus(Status.OK, {})["status"]["code"])

            self.scene_obj = self.testHelper.get_scene_obj(self.scene_name, with_related=True)

            for index, line_obj in enumerate(self.scene_obj.metroline_set.all().order_by("id")):

                for track_obj in line_obj.metrotrack_set.all():
                    self.assertIsNotNone(track_obj.auxiliariesConsumption)
                    self.assertIsNotNone(track_obj.ventilationConsumption)

                for depot_obj in line_obj.metrodepot_set.all():
                    self.assertIsNotNone(depot_obj.auxConsumption)
                    self.assertIsNotNone(depot_obj.ventilationConsumption)
                    self.assertIsNotNone(depot_obj.dcConsumption)

                for station_obj in line_obj.metrostation_set.all():
                    self.assertIsNotNone(station_obj.minAuxConsumption)
                    self.assertIsNotNone(station_obj.maxAuxConsumption)
                    self.assertIsNotNone(station_obj.minHVACConsumption)
                    self.assertIsNotNone(station_obj.maxHVACConsumption)
                    self.assertIsNotNone(station_obj.tau)

                self.assertIsNotNone(line_obj.usableEnergyContent)
                self.assertIsNotNone(line_obj.chargingEfficiency)
                self.assertIsNotNone(line_obj.dischargingEfficiency)
                self.assertIsNotNone(line_obj.peakPower)
                self.assertIsNotNone(line_obj.maximumEnergySavingPossiblePerHour)
                self.assertIsNotNone(line_obj.energySavingMode)
                self.assertIsNotNone(line_obj.powerLimitToFeed)

            self.assertIsNotNone(self.scene_obj.timeStampStep3File)

    def upload_operation_file(self):
        """ simulate step 5 uploading excel file """
        UPLOAD_OPERATION_FILE_URL = reverse("scene:uploadOperationalFile", kwargs={"scene_id": self.scene_obj.id})

        # upload file
        with open(os.path.join(self.FILE_PATH, OPERATION_FILE_NAME), "rb") as fp:
            data = {"file": fp}
            response = self.client.post(UPLOAD_OPERATION_FILE_URL, data)

            self.assertEqual(response.status_code, 200)
            status = json.loads(response.content.decode("utf-8"))["status"]
            self.assertEqual(status["code"], Status.getJsonStatus(Status.OK, {})["status"]["code"])

            self.scene_obj = self.testHelper.get_scene_obj(self.scene_name, with_related=True)

            for index, line_obj in enumerate(self.scene_obj.metroline_set.all().order_by("id")):

                for operation_obj in self.scene_obj.operationperiod_set.all().order_by("id"):
                    from scene.models import OperationPeriodForMetroLine, OperationPeriodForMetroStation, OperationPeriodForMetroTrack
                    op_for_lines = OperationPeriodForMetroLine.objects.filter(operationPeriod=operation_obj,
                                                                              metroLine=line_obj).count()
                    #for o in OperationPeriodForMetroLine.objects.filter(operationPeriod=operation_obj,
                    #                                                          metroLine=line_obj).order_by("id"):
                    #    print("{} {} {}".format(o.metric, o.value, o.direction))
                    self.assertEqual(op_for_lines, 11)
                    for station_obj in line_obj.metrostation_set.all().order_by("id"):
                        op_for_stations = OperationPeriodForMetroStation.objects.filter(operationPeriod=operation_obj,
                                                                                        metroStation=station_obj).count()
                        self.assertEqual(op_for_stations, 5)

                    for track_obj in line_obj.metrotrack_set.all().order_by("id"):
                        op_for_tracks = OperationPeriodForMetroTrack.objects.filter(operationPeriod=operation_obj,
                                                                                    metroTrack=track_obj).count()
                        self.assertEqual(op_for_tracks, 4)

            self.assertIsNotNone(self.scene_obj.timeStampStep5File)

    def upload_speed_file(self):
        """ simulate step 6 uploading excel file """
        UPLOAD_SPEED_FILE_URL = reverse("scene:uploadSpeedFile", kwargs={"scene_id": self.scene_obj.id})
        
        # upload file
        with open(os.path.join(self.FILE_PATH, SPEED_FILE_NAME), "rb") as fp:
            data = {"file": fp}
            response = self.client.post(UPLOAD_SPEED_FILE_URL, data)

            self.assertEqual(response.status_code, 200)
            status = json.loads(response.content.decode("utf-8"))["status"]
            self.assertEqual(status["code"], Status.getJsonStatus(Status.OK, {})["status"]["code"])

            self.scene_obj = self.testHelper.get_scene_obj(self.scene_name, with_related=True)
            # now check changes

        self.assertIsNotNone(self.scene_obj.timeStampStep6File)

    def download_file(self, url, file_path):
        """ check that url to download template files and files uploaded by users works """
        response = self.testHelper.make_get_request(url, {}, expected_server_response_code=302, expected_response=None)
        self.assertEquals(response.url, file_path)

    def test_FillAllSteps(self):
        """ simulate correct process to create a escene """

        self.check_step_0()
        self.upload_topologic_file()
        self.check_step_1()
        self.check_step_2()
        self.upload_systemic_file()
        self.check_step_3()
        self.check_step_4()
        self.upload_operation_file()
        self.check_step_5()
        self.upload_speed_file()
        self.check_step_6()

        # check that i can download files
        file_urls = [
            reverse("scene:downloadStepFile", kwargs={"step_id": 1, "scene_id": self.scene_obj.id}),
            reverse("scene:downloadStepFile", kwargs={"step_id": 3, "scene_id": self.scene_obj.id}),
            reverse("scene:downloadStepFile", kwargs={"step_id": 5, "scene_id": self.scene_obj.id}),
            reverse("scene:downloadStepFile", kwargs={"step_id": 6, "scene_id": self.scene_obj.id}),
            reverse("scene:downloadStepTemplate", kwargs={"step_id": 1, "scene_id": self.scene_obj.id}),
            reverse("scene:downloadStepTemplate", kwargs={"step_id": 3, "scene_id": self.scene_obj.id}),
            reverse("scene:downloadStepTemplate", kwargs={"step_id": 5, "scene_id": self.scene_obj.id}),
            reverse("scene:downloadStepTemplate", kwargs={"step_id": 6, "scene_id": self.scene_obj.id}),
        ]
        file_paths = [
            self.scene_obj.step1File.url, self.scene_obj.step3File.url, self.scene_obj.step5File.url,
            self.scene_obj.step6File.url,
            self.scene_obj.step1Template.url, self.scene_obj.step3Template.url, self.scene_obj.step5Template.url,
            self.scene_obj.step6Template.url,
        ]
        for url, file_path in zip(file_urls, file_paths):
            self.download_file(url, file_path)

        # generate input to run models
        first_input(self.scene_obj.id)

        # load html for scene and return scene data
        page_urls = [
            reverse("scene:wizard", kwargs={"scene_id": self.scene_obj.id}),
            reverse("scene:getSceneData", kwargs={"scene_id": self.scene_obj.id}),
            reverse("scene:panel", kwargs={"scene_id": self.scene_obj.id}),
            reverse("scene:panelData", kwargs={"scene_id": self.scene_obj.id})
        ]

        for url in page_urls:
            self.testHelper.make_get_request(url, {}, expected_response=None)
