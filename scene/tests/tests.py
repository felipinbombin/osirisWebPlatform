# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.test import Client

from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings

from scene.models import Scene, MetroLineMetric, SystemicParams
from scene.statusResponse import Status

from collections import defaultdict

import os
import json


class CompleteSceneData(TestCase):
    """
    test for scene wizard
    """

    def setUp(self):
        """
            create user and log in
        """

        # log in inputs
        username = "Felipinbombin"
        password = "Felipinbombin"
        email = "a@b.cl"

        # create user on django contrib user model
        User.objects.create_superuser(username=username, email=email, password=password)

        # log in process
        self.client = Client()
        response = self.client.login(username=username, password=password)
        self.assertTrue(response)

        # create scene
        self.scene_name = "Escenario 1"
        URL = reverse("admin:scene_scene_add")
        response = self.client.post(URL, {"name": self.scene_name}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Scene.objects.count(), 1)

        self.FILE_PATH, _ = os.path.split(os.path.abspath(__file__))

        self.load_scene_obj()

    def tearDown(self):
        """ executed after every test """
        self.load_scene_obj()

        # delete uploaded files
        if self.sceneObj.step1File:
            os.remove(os.path.join(settings.MEDIA_ROOT, str(self.sceneObj.step1File)))
        if self.sceneObj.step3File:
            os.remove(os.path.join(settings.MEDIA_ROOT, str(self.sceneObj.step3File)))
        if self.sceneObj.step5File:
            os.remove(os.path.join(settings.MEDIA_ROOT, str(self.sceneObj.step5File)))
        if self.sceneObj.step6File:
            os.remove(os.path.join(settings.MEDIA_ROOT, str(self.sceneObj.step6File)))

    def load_scene_obj(self):
        """ reload scene obj with latest data """
        self.sceneObj = Scene.objects.prefetch_related("metroline_set__metrodepot_set",
                                                       "metroline_set__metrostation_set",
                                                       "metroline_set__metrotrack_set",
                                                       "metroline_set__metrolinemetric_set",
                                                       "systemicparams_set",
                                                       "metroconnection_set").get(name=self.scene_name)

    def validate_step(self, url, data, content_type=""):
        """ validate step to continue to next step """
        response = self.client.post(url, data, content_type)

        self.assertEqual(response.status_code, 200)
        status = json.loads(response.content.decode("utf-8"))["status"]
        self.assertEqual(status["code"], Status.getJsonStatus(Status.OK, {})["status"]["code"])

        return response

    def check_step_0(self):
        """ simulate upload data for step 0 """
        STEP_0_JSON_FILE_NAME = "step0_data.json"
        STEP_0_URL = reverse("scene:validation", kwargs={"stepId": 0, "sceneId": self.sceneObj.id})

        with open(os.path.join(self.FILE_PATH, STEP_0_JSON_FILE_NAME)) as fp:
            data = json.loads(fp.read())
            self.validate_step(STEP_0_URL, json.dumps(data), "application/json")

            # check data was created correctly
            self.load_scene_obj()
            lines = self.sceneObj.metroline_set.all().order_by("id")

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
        STEP_1_URL = reverse("scene:validation", kwargs={"stepId": 1, "sceneId": self.sceneObj.id})
        self.validate_step(STEP_1_URL, {})

    def check_step_2(self):
        """ simulate step 2 process """
        STEP_2_JSON_FILE_NAME = "step2_data.json"
        STEP_2_URL = reverse("scene:validation", kwargs={"stepId": 2, "sceneId": self.sceneObj.id})

        with open(os.path.join(self.FILE_PATH, STEP_2_JSON_FILE_NAME)) as fp:
            data = json.loads(fp.read())
            self.validate_step(STEP_2_URL, json.dumps(data), "application/json")

            # check data was created correctly
            self.load_scene_obj()

            params = self.sceneObj.systemicparams_set.first()
            print(SystemicParams.objects.first())
            #self.assertEqual(self.sceneObj.systemicparams_set.all().count(), 1)

            for v, i in params.items():
                print(v)
                print(i)



    def check_step_3(self):
        """ simulate step 3 process """
        STEP_3_URL = reverse("scene:validation", kwargs={"stepId": 3, "sceneId": self.sceneObj.id})
        self.validate_step(STEP_3_URL, {})

    def check_step_4(self):
        """ simulate step 4 process """
        STEP_4_URL = reverse("scene:validation", kwargs={"stepId": 4, "sceneId": self.sceneObj.id})

    def check_step_5(self):
        """ simulate step 5 process """
        STEP_5_URL = reverse("scene:validation", kwargs={"stepId": 5, "sceneId": self.sceneObj.id})
        self.validate_step(STEP_5_URL, {})

    def check_step_6(self):
        """ simulate step 6 process """
        STEP_6_URL = reverse("scene:validation", kwargs={"stepId": 6, "sceneId": self.sceneObj.id})
        self.validate_step(STEP_6_URL, {})

    def upload_topologic_file(self):
        """ simulate step 1 uploading excel file """
        UPLOAD_TOPOLOGIC_FILE_URL = reverse("scene:uploadTopologicFile", kwargs={"sceneId": self.sceneObj.id})
        TOPOLOGIC_FILE_NAME = u"Escenario_topologico.xlsx"

        # upload file
        with open(os.path.join(self.FILE_PATH, TOPOLOGIC_FILE_NAME), "rb") as fp:
            data = {"file": fp}
            response = self.client.post(UPLOAD_TOPOLOGIC_FILE_URL, data)

            self.assertEqual(response.status_code, 200)
            status = json.loads(response.content.decode("utf-8"))["status"]
            self.assertEqual(status["code"], Status.getJsonStatus(Status.OK, {})["status"]["code"])

            self.load_scene_obj()

            metric_length = [9, 11]
            for index, line_obj in enumerate(self.sceneObj.metroline_set.all().order_by("id")):
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

            self.assertIsNotNone(self.sceneObj.timeStampStep1File)

    def upload_systemic_file(self):
        """ simulate step 3 uploading excel file """
        pass

    def upload_operation_file(self):
        """ simulate step 5 uploading excel file """
        pass

    def upload_speed_file(self):
        """ simulate step 6 uploading excel file """
        pass

    def test_FillAllSteps(self):
        """ simulate correct process to create a escene """

        self.check_step_0()
        self.upload_topologic_file()
        self.check_step_1()
        self.check_step_2()
        self.upload_systemic_file()
        """
        self.check_step_3()
        self.check_step_4()
        self.upload_operation_file()
        self.check_step_5()
        self.upload_speed_file()
        self.check_step_6()
        """

    def test_checkStep1WithoutPrevious(self):
        """ test step 1 without previous step """
        self.upload_topologic_file()
        self.check_step_1()

    def test_checkStep2WithoutPrevious(self):
        """ test step 2 without previous step """
        self.check_step_2()