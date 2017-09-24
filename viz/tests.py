from django.test import TestCase
from django.urls import reverse

from scene.tests.testHelper import TestHelper


class SpeedModelVizTest(TestCase):
    """ test web page to see output of speed model """

    def setUp(self):
        """
            create user and log in
        """
        self.testHelper = TestHelper(self)

        self.client = self.testHelper.get_logged_client()

        # create scene
        self.scene_name = "test scene name"
        self.scene_obj = self.testHelper.create_scene(self.scene_name)

    def test_loadHTML(self):
        """ ask for speed output html file """
        URL = reverse("viz:speedModel", kwargs={"sceneId": self.scene_obj.id})
        self.testHelper.make_get_request(URL, {}, expected_response=None)

        # get error 404 because scene id does not exist
        URL = reverse("viz:speedModel", kwargs={"sceneId": 1000})
        self.testHelper.make_get_request(URL, {}, expected_response=None, expected_server_response_code=404)


    def test_getSpeedModelData(self):
        """ ask model output data """
        URL = reverse("viz:speedModelData", kwargs={"sceneId": self.scene_obj.id})

        response = self.testHelper.make_get_request(URL, {}, expected_response=None)