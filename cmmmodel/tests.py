from django.test import TestCase

from django.urls import reverse

# Create your tests here.
from scene.tests.testHelper import TestHelper


class ExecuteModel(TestCase):
    """
    test execution of model
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

    def completeScene(self):
        """ complete all data of scene """
        pass

    def test_checkModelExecution(self):
        """ ask for status of models """
        STATUS_URL = reverse("cmmmodel:status")
        data = {
            "sceneId": self.scene_obj.id
        }

        json_response = self.testHelper.make_get_request(STATUS_URL, data)

        print(json_response)

    def test_stopModelExecution(self):
        """  """
        pass

    def test_runModelExecution(self):
        """  """
        pass