from django.test import TestCase

from django.urls import reverse
from django.utils import timezone

from scene.tests.testHelper import TestHelper
from scene.models import Scene
from scene.statusResponse import Status as st

from cmmmodel.models import ModelExecutionQueue, Model, ModelExecutionHistory
from cmmmodel.views import Status
from cmmmodel.saveJobResponse import save_model_response, process_answer

from viz.models import ModelAnswer
from scene.models import MetroLine, MetroTrack, MetroStation, OperationPeriod

import json
import uuid
import os
import pickle

TEST_MODEL_ID = 999


class ExecuteModel(TestCase):
    """
    test execution of model
    """
    fixtures = ['models', 'test_model', 'possibleQueue']

    def setUp(self):
        """
            create user and log in
        """
        self.testHelper = TestHelper(self)

        self.client = self.testHelper.get_logged_client()

        # create scene
        self.scene_name = "Escenario 1"
        self.scene_obj = self.testHelper.create_scene(self.scene_name)

    def get_model_status(self):
        """ ask for model status through url """
        STATUS_URL = reverse("cmmmodel:status")
        data = {
            "sceneId": self.scene_obj.id
        }
        return self.testHelper.make_get_request(STATUS_URL, data, expected_response=None)

    def run_test_model(self, expected_response=None):
        """  """
        RUN_URL = reverse("cmmmodel:run")
        data = {
            "sceneId": self.scene_obj.id,
            "modelId": TEST_MODEL_ID
        }

        return self.testHelper.make_post_request(RUN_URL, data, expected_response=expected_response)

    def stop_test_model(self, expected_response=None):
        """  """
        STOP_URL = reverse("cmmmodel:stop")
        data = {
            "sceneId": self.scene_obj.id,
            "modelId": TEST_MODEL_ID
        }

        return self.testHelper.make_post_request(STOP_URL, data, expected_response=expected_response)

    def test_checkModelExecution(self):
        """ ask for status of models """
        json_response = self.get_model_status()

        for model in json.loads(json_response.content.decode("utf-8")):
            # print(model)
            pass

    def test_enqueuedTestModel(self):
        """ raise error when it tries to run model because is enqueued """
        # simulate scene is ready to run
        self.scene_obj.status = Scene.OK
        self.scene_obj.save()

        # add test model to queue
        meh = ModelExecutionHistory.objects.create(scene=self.scene_obj, model_id=1, start=timezone.now(),
                                                   externalId=uuid.uuid4())
        model = Model.objects.get(id=TEST_MODEL_ID)
        ModelExecutionQueue.objects.create(modelExecutionHistory=meh, model=model)

        self.run_test_model(expected_response=st.getJsonStatus(st.ENQUEUED_MODEL_ERROR, {}))

    def test_runningTestModel(self):
        """ raise error when it tries to run model because model is actually running """
        # simulate scene is ready to run
        self.scene_obj.status = Scene.OK
        self.scene_obj.save()

        # add test model to queue
        ModelExecutionHistory.objects.create(scene=self.scene_obj, model_id=TEST_MODEL_ID, start=timezone.now(),
                                             externalId=uuid.uuid4())

        self.run_test_model(expected_response=st.getJsonStatus(st.MODEL_IS_RUNNING_ERROR, {}))

    def test_runAndstopTestModelExecution(self):
        """  """

        # scene not ready (current step less than 5)
        self.run_test_model(expected_response=st.getJsonStatus(st.INCOMPLETE_SCENE_ERROR, {}))

        # simulate scene is ready to run
        self.scene_obj.status = Scene.OK
        self.scene_obj.save()

        json_response = self.run_test_model()
        #print(json_response.content)

        # set modelexecutionhistory object to modify model status response (to show a model is running in json)
        #ModelExecutionHistory.objects.update(model_id=1)
        json_response = json.loads(self.get_model_status().content.decode("utf-8"))
        test_model_position = len(json_response) - 1
        self.assertIn("lastExecutionInfo", json_response[test_model_position].keys())
        self.assertIn(Status.RUNNING, json_response[test_model_position]["status"])

        # check that model after be executed is available
        ModelExecutionHistory.objects.update(status=ModelExecutionHistory.OK)
        json_response = json.loads(self.get_model_status().content.decode("utf-8"))
        self.assertIn(Status.AVAILABLE, json_response[test_model_position]["status"])

        # restore model execution status
        ModelExecutionHistory.objects.update(status=ModelExecutionHistory.RUNNING)
        json_response = self.stop_test_model()
        #print(json_response.content)

    def test_saveJob(self):
        """ simulate a call from cluster after finish model execution to saveJobResponse file """

        # simulate scene is ready to run
        self.scene_obj.status = Scene.OK
        self.scene_obj.save()

        # create execution record
        file_name = "44b4f769-c8c1-468b-9a35-491e4c1cea89.output"
        file_path = os.path.join("..", os.path.join("..", os.path.join("cmmmodel", os.path.join("tests", file_name))))
        std_out = ""
        std_err = ""
        external_id = uuid.uuid4()
        meh = ModelExecutionHistory.objects.create(scene=self.scene_obj, model_id=TEST_MODEL_ID, externalId=external_id,
                                             start=timezone.now())

        # added test model to queue to test queue model execution process
        ModelExecutionQueue.objects.create(modelExecutionHistory=meh, model_id=TEST_MODEL_ID)

        save_model_response(str(external_id), file_path, std_out, std_err)

        # stop execution model in cmm cluster (queued model)
        self.stop_test_model()

        meh.refresh_from_db()
        self.assertEqual(meh.status, ModelExecutionHistory.OK)
        self.assertIsNotNone(meh.end)

        std_err = "not empty"
        save_model_response(str(external_id), file_path, std_out, std_err)
        meh.refresh_from_db()
        self.assertEqual(meh.status, ModelExecutionHistory.ERROR)

    def test_processAnswer(self):
        """ test load data from speed model output dict based on situation of file """
        file_name = "44b4f769-c8c1-468b-9a35-491e4c1cea89.output"
        file_path = os.path.join("cmmmodel", os.path.join("tests", file_name))

        L1 = MetroLine.objects.create(scene=self.scene_obj, name="L1", externalId=uuid.uuid4())
        [MetroStation.objects.create(name="S{}".format(index), externalId=uuid.uuid4(), metroLine=L1) for index in range(1, 11)]
        [MetroTrack.objects.create(metroLine=L1, name="t{}".format(index), startStation_id=(index+1), endStation_id=(index+1)) for index in range(9)]

        L2 = MetroLine.objects.create(scene=self.scene_obj, name="L2", externalId=uuid.uuid4())
        [MetroStation.objects.create(name="S{}".format(index), externalId=uuid.uuid4(), metroLine=L2) for index in range(12, 24)]
        [MetroTrack.objects.create(metroLine=L2, name="t{}".format(index), startStation_id=(index+12), endStation_id=(index+12)) for index in range(11)]

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
            answer = answer["second_input"]
            process_answer(answer, execution_obj)

        self.assertEqual(ModelAnswer.objects.count(), 147132)
