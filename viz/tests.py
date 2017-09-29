from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from scene.tests.testHelper import TestHelper
from scene.models import MetroLine, MetroStation, OperationPeriod, MetroTrack
from cmmmodel.models import ModelExecutionHistory
from cmmmodel.saveJobResponse import process_answer

import uuid
import pickle
import os
import json


class SpeedModelVizTest(TestCase):
    """ test web page to see output of speed model """
    fixtures = ["models", "possibleQueue"]

    def setUp(self):
        """
            create user and log in
        """
        self.testHelper = TestHelper(self)

        self.client = self.testHelper.get_logged_client()

        # create scene
        self.scene_name = "test scene name"
        self.scene_obj = self.testHelper.create_scene(self.scene_name)

        self.L1 = MetroLine.objects.create(scene=self.scene_obj, name="L1", externalId=uuid.uuid4())
        self.S1 = MetroStation.objects.create(metroLine=self.L1, name="S1", externalId=uuid.uuid4())

    def test_loadHTML(self):
        """ ask for speed output html file """
        URL = reverse("viz:speedModel", kwargs={"sceneId": self.scene_obj.id})
        self.testHelper.make_get_request(URL, {}, expected_response=None)

        # get error 404 because scene id does not exist
        URL = reverse("viz:speedModel", kwargs={"sceneId": 1000})
        self.testHelper.make_get_request(URL, {}, expected_response=None, expected_server_response_code=404)


    def test_getSpeedModelData(self):
        """ ask model output data """

        # save model
        file_name = "44b4f769-c8c1-468b-9a35-491e4c1cea89.output"
        file_path = os.path.join("cmmmodel", os.path.join("tests", file_name))

        [MetroStation.objects.create(name="S{}".format(index), externalId=uuid.uuid4(), metroLine=self.L1) for index in range(2, 11)]
        [MetroTrack.objects.create(metroLine=self.L1, name="t{}".format(index),
                                   startStation_id=self.S1.id, endStation_id=self.S1.id) for index in range(9)]

        L2 = MetroLine.objects.create(scene=self.scene_obj, name="L2", externalId=uuid.uuid4())
        [MetroStation.objects.create(name="S{}".format(index), externalId=uuid.uuid4(), metroLine=L2) for index in range(12, 24)]
        [MetroTrack.objects.create(metroLine=L2, name="t{}".format(index),
                                   startStation_id=self.S1.id, endStation_id=self.S1.id) for index in range(11)]

        OperationPeriod.objects.create(scene=self.scene_obj, externalId=uuid.uuid4(), name="OP1",
                                       start="09:00:00", end="10:00:00", temperature=0, humidity=0, co2Concentration=0,
                                       solarRadiation=0, sunElevationAngle=0)
        OperationPeriod.objects.create(scene=self.scene_obj, externalId=uuid.uuid4(), name="OP2",
                                       start="10:00:00", end="11:00:00", temperature=0, humidity=0, co2Concentration=0,
                                       solarRadiation=0, sunElevationAngle=0)

        execution_obj = ModelExecutionHistory.objects.create(scene=self.scene_obj, model_id=1, externalId=uuid.uuid4(),
                                                             start=timezone.now())

        with open(file_path, "rb") as answer_file:
            answer = pickle.load(answer_file)
            process_answer(answer, execution_obj)

        URL = reverse("viz:speedModelData", kwargs={"sceneId": self.scene_obj.id})

        response = self.testHelper.make_get_request(URL, {}, expected_response=None)
        content = json.loads(response.content.decode("utf-8"))

        self.assertEqual(content["answer"]["OP1"]["L1"]["Distance"]["r"][0]["t0"],
                         content["answer"]["OP1"]["L1"]["Distance"]["r"][0]["t0"])