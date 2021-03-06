# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.urls import reverse

from scene.models import Scene
from scene.statusResponse import Status
from .testHelper import TestHelper


class SceneDataPanel(TestCase):
    """
    test for scene panel view
    """

    def setUp(self):
        """
            create user and log in
        """
        self.testHelper = TestHelper(self)

        self.client = self.testHelper.get_logged_client()

        # create scene
        self.scene_name = "test scene name"
        self.scene_obj = self.testHelper.create_scene(self.scene_name)

    def tearDown(self):
        """ executed after every test """
        pass

    def test_ChangeName(self):
        """ change name """
        URL = reverse("scene:changeSceneName", kwargs={"scene_id": self.scene_obj.id})
        new_name = "this is the new name of scene"
        data = {
            "new_name": new_name
        }
        self.testHelper.make_post_request(URL, data,
                                          expected_response=Status.getJsonStatus(Status.SUCCESS_NEW_NAME, {}))

        self.scene_obj.refresh_from_db()
        self.assertEqual(self.scene_obj.name, new_name)

    def test_WrongSceneName(self):
        """ send scene name = "" """
        URL = reverse("scene:changeSceneName", kwargs={"scene_id": self.scene_obj.id})
        new_name = ""
        data = {
            "new_name": new_name
        }
        self.testHelper.make_post_request(URL, data,
                                          expected_response=Status.getJsonStatus(Status.INVALID_SCENE_NAME_ERROR, {}))

        previous_name = self.scene_obj.name
        self.scene_obj.refresh_from_db()
        self.assertEqual(self.scene_obj.name, previous_name)

    def test_ChangeNameSceneDoesNotExist(self):
        """ change name of scen that does not exist """
        URL = reverse("scene:changeSceneName", kwargs={"scene_id": 1000})
        new_name = ""
        data = {
            "new_name": new_name
        }
        self.testHelper.make_post_request(URL, data,
                                          expected_response=Status.getJsonStatus(Status.USER_NOT_LOGGED_ERROR, {}))

    def test_DeleteSceneDoesNotExist(self):
        """ delete scene that does not exist """
        URL = reverse("scene:deleteScene", kwargs={"scene_id": 100})
        self.testHelper.make_post_request(URL, {},
                                          expected_response=Status.getJsonStatus(Status.USER_NOT_LOGGED_ERROR, {}))

    def test_DeleteScene(self):
        """ delete scene """
        URL = reverse("scene:deleteScene", kwargs={"scene_id": self.scene_obj.id})
        self.testHelper.make_post_request(URL, {})

        self.assertRaises(Scene.DoesNotExist, Scene.objects.get, id=self.scene_obj.id)

    def test_loadPanelWebPage(self):
        """ load html """
        URL = reverse("scene:panel", kwargs={"scene_id": self.scene_obj.id})
        self.testHelper.make_get_request(URL, {}, expected_response=None)

    def test_loadPanelDataWebPage(self):
        """ load html """
        URL = reverse("scene:panelData", kwargs={"scene_id": self.scene_obj.id})
        self.testHelper.make_get_request(URL, {}, expected_response=None)