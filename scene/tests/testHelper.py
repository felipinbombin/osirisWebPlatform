
from django.contrib.auth.models import User

from django.urls import reverse
from django.test import Client
from django.test.client import MULTIPART_CONTENT
from scene.models import Scene

from scene.statusResponse import Status

import json

class TestHelper():

    def __init__(self, testInstance):
        """ constructor """
        self.testInstance = testInstance
        self.client = self.create_logged_client()

    def create_logged_client(self):
        """ get test logged test client  """

        # log in inputs
        username = "Felipinbombin"
        password = "Felipinbombin"
        email = "a@b.cl"

        # create user on django contrib user model
        User.objects.create_superuser(username=username, email=email, password=password)

        # log in process
        client = Client()
        response = client.login(username=username, password=password)
        self.testInstance.assertTrue(response)

        return client

    def get_logged_client(self):
        """  """
        return self.client

    def create_scene(self, name):
        """ create scene object using url """

        URL = reverse("admin:scene_scene_add")
        response = self.client.post(URL, {"name": name}, follow=True)

        self.testInstance.assertEqual(response.status_code, 200)
        self.testInstance.assertEqual(Scene.objects.count(), 1)

        return Scene.objects.get(name=name)

    def get_scene_obj(self, name, with_related=False):
        """ reload scene obj with latest data """
        query = Scene.objects
        if with_related:
            query = query.prefetch_related("metroline_set__metrodepot_set",
                                           "metroline_set__metrostation_set",
                                           "metroline_set__metrotrack_set",
                                           "metroline_set__metrolinemetric_set",
                                           "systemicparams_set",
                                           "metroconnection_set")
        return query.get(name=name)


    def __process_response(self, response, expected_server_response_code, expected_response):
        """  """
        self.testInstance.assertEqual(response.status_code, expected_server_response_code)
        if expected_response is not None:
            status = json.loads(response.content.decode("utf-8"))["status"]
            self.testInstance.assertEqual(status["code"], expected_response["status"]["code"])

        return response

    def make_post_request(self, url, data, content_type=MULTIPART_CONTENT, expected_server_response_code=200,
                          expected_response=Status.getJsonStatus(Status.OK, {})):
        """  """
        response = self.client.post(url, data, content_type)

        return self.__process_response(response, expected_server_response_code, expected_response)

    def make_get_request(self, url, data, expected_server_response_code=200,
                          expected_response=Status.getJsonStatus(Status.OK, {})):
        """  """
        response = self.client.get(url, data)

        return self.__process_response(response, expected_server_response_code, expected_response)