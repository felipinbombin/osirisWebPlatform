import json
import uuid

from django.test import TestCase
from django.utils import timezone

from cmmmodel.models import ModelExecutionQueue, CMMModel, ModelExecutionHistory
from cmmmodel.tests.helper import APIHelper
from cmmmodel.views import Status
from scene.models import Scene
from scene.statusResponse import Status as st
from scene.tests.testHelper import TestHelper

TEST_MODEL_ID = 999


class CheckAPI(TestCase):
    """

    """
    fixtures = ['models', 'test_model', 'possibleQueue']

    def setUp(self):
        """
            create user and log in
        """
        self.test_helper = TestHelper(self)

        self.client = self.test_helper.get_logged_client()

        self.scene_name = "Escenario 1"
        self.scene_obj = self.test_helper.create_scene(self.scene_name)

        self.api_helper = APIHelper(self.test_helper, self.scene_obj, TEST_MODEL_ID)

    def test_checkModelExecution(self):
        """ ask for status of models """
        json_response = self.api_helper.get_model_status()

        for model in json.loads(json_response.content.decode("utf-8")):
            print(model)

    def test_enqueuedTestModel(self):
        """ raise error when it tries to run model because is enqueued """
        # simulate scene is ready to run
        self.scene_obj.status = Scene.OK
        self.scene_obj.save()

        # add test model to queue
        meh = ModelExecutionHistory.objects.create(scene=self.scene_obj, model_id=1, start=timezone.now(),
                                                   externalId=uuid.uuid4())
        model = CMMModel.objects.get(id=TEST_MODEL_ID)
        ModelExecutionQueue.objects.create(modelExecutionHistory=meh, model=model)

        self.api_helper.run_test_model(expected_response=st.getJsonStatus(st.ENQUEUED_MODEL_ERROR, {}))

    def test_runningTestModel(self):
        """ raise error when it tries to run model because model is actually running """
        # simulate scene is ready to run
        self.scene_obj.status = Scene.OK
        self.scene_obj.save()

        # add test model to queue
        ModelExecutionHistory.objects.create(scene=self.scene_obj, model_id=TEST_MODEL_ID, start=timezone.now(),
                                             externalId=uuid.uuid4())

        self.api_helper.run_test_model(expected_response=st.getJsonStatus(st.MODEL_IS_RUNNING_ERROR, {}))

    def test_runAndstopTestModelExecution(self):
        """  """

        # scene not ready (current step less than 5)
        self.api_helper.run_test_model(expected_response=st.getJsonStatus(st.INCOMPLETE_SCENE_ERROR, {}))

        # simulate scene is ready to run
        self.scene_obj.status = Scene.OK
        self.scene_obj.save()

        json_response = self.api_helper.run_test_model()
        # print(json_response.content)

        # set modelexecutionhistory object to modify model status response (to show a model is running in json)
        # ModelExecutionHistory.objects.update(model_id=1)
        json_response = json.loads(self.api_helper.get_model_status().content.decode("utf-8"))
        test_model_position = len(json_response) - 1
        self.assertIn("lastExecutionInfo", json_response[test_model_position].keys())
        self.assertIn(Status.RUNNING, json_response[test_model_position]["status"])

        # check that model after be executed is available
        ModelExecutionHistory.objects.update(status=ModelExecutionHistory.OK)
        json_response = json.loads(self.api_helper.get_model_status().content.decode("utf-8"))
        self.assertIn(Status.AVAILABLE, json_response[test_model_position]["status"])

        # restore model execution status
        ModelExecutionHistory.objects.update(status=ModelExecutionHistory.RUNNING)
        json_response = self.api_helper.stop_test_model()
        # print(json_response.content)
