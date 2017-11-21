from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from django.utils import timezone
from django.conf import settings

from splinter import Browser

from scene.tests.testHelper import TestHelper
from scene.models import MetroLine, MetroStation, OperationPeriod, MetroTrack
from scene.statusResponse import Status

from cmmmodel.models import ModelExecutionHistory, Model
from cmmmodel.saveJobResponse import process_answer

import uuid
import pickle
import os
import json
import time


class ModelVizTest(TestCase):
    fixtures = ["models", "possibleQueue"]

    def set_up(self, model_id, file_path):
        """
            create user and log in
        """
        self.testHelper = TestHelper(self)

        self.client = self.testHelper.get_logged_client()

        # create scene
        self.scene_name = "test scene name"
        self.scene_obj = self.testHelper.create_scene(self.scene_name)

        self.create_fake_execution(model_id, file_path)

    def create_fake_execution(self, model_id, file_path):
        """  create record of execution """

        L1 = MetroLine.objects.create(scene=self.scene_obj, name="L1", externalId=uuid.uuid4())

        stations = [MetroStation.objects.create(name="S{}".format(index), externalId=uuid.uuid4(), metroLine=L1) for
                    index in range(1, 11)]
        for index, station in enumerate(stations[:-1]):
            MetroTrack.objects.create(metroLine=L1, name="Track{}".format(index),
                                      startStation_id=station.id, endStation_id=stations[index + 1].id)

        L2 = MetroLine.objects.create(scene=self.scene_obj, name="L2", externalId=uuid.uuid4())
        stations = [MetroStation.objects.create(name="S{}".format(index), externalId=uuid.uuid4(), metroLine=L2) for
                    index in range(12, 24)]
        for index, station in enumerate(stations[:-1]):
            MetroTrack.objects.create(metroLine=L2, name="Track{}".format(index),
                                      startStation_id=station.id, endStation_id=stations[index + 1].id)

        OperationPeriod.objects.create(scene=self.scene_obj, externalId=uuid.uuid4(), name="OP1",
                                       start="09:00:00", end="10:00:00", temperature=0, humidity=0,
                                       co2Concentration=0,
                                       solarRadiation=0, sunElevationAngle=0)
        OperationPeriod.objects.create(scene=self.scene_obj, externalId=uuid.uuid4(), name="OP2",
                                       start="10:00:00", end="11:00:00", temperature=0, humidity=0,
                                       co2Concentration=0,
                                       solarRadiation=0, sunElevationAngle=0)

        execution_obj = ModelExecutionHistory.objects.create(scene=self.scene_obj, model_id=model_id,
                                                             externalId=uuid.uuid4(), start=timezone.now())

        with open(file_path, "rb") as answer_file:
            answer = pickle.load(answer_file)
            answer = answer["output"]
            process_answer(answer, execution_obj)


class SpeedModelVizTest(ModelVizTest):
    """ test web page to see output of speed model """

    def setUp(self):
        file_name = "44b4f769-c8c1-468b-9a35-491e4c1cea89.output"
        file_path = os.path.join("cmmmodel", "tests", file_name)

        self.set_up(Model.SPEED_MODEL_ID, file_path)

    def test_loadHTML(self):
        """ ask for speed output html file """

        URL = reverse("viz:speedModel", kwargs={"sceneId": self.scene_obj.id})
        self.testHelper.make_get_request(URL, {}, expected_response=None)

        # get error 404 because scene id does not exist
        URL = reverse("viz:speedModel", kwargs={"sceneId": 1000})
        self.testHelper.make_get_request(URL, {}, expected_response=None, expected_server_response_code=404)

    def test_getSpeedModelDataWithExecutionRunning(self):
        """ ask model output data with last execution status == runnning """

        URL = reverse("viz:speedModelData", kwargs={"sceneId": self.scene_obj.id})

        params = {
            "direction": "g",
            "operationPeriod": "OP1",
            "metroLineName": "L1",
            "tracks[]": [str(mt.externalId) for mt in MetroTrack.objects.all()],
            "attributes[]": ["velDist", "Speedlimit", "Time"]
        }

        # with error because last execution of model is running
        response = self.testHelper.make_get_request(URL, params, expected_response=None)
        content = json.loads(response.content.decode("utf-8"))

        self.assertNotIn("answer", content.keys())
        self.assertEqual(content["status"]["code"],
                         Status.getJsonStatus(Status.LAST_MODEL_FINISHED_BADLY_ERROR, {})["status"]["code"])
        self.assertEqual(content["status"]["message"],
                         Status.getJsonStatus(Status.LAST_MODEL_FINISHED_BADLY_ERROR, {})["status"]["message"])

    def test_getSpeedModelDataWithOKExecution(self):
        """ ask model output data with last execution status ok """

        URL = reverse("viz:speedModelData", kwargs={"sceneId": self.scene_obj.id})

        # simulate execution finished well
        ModelExecutionHistory.objects.update(status=ModelExecutionHistory.OK)

        params = {
            "direction": "g",
            "operationPeriod": "OP1",
            "metroLineName": "L1",
            "tracks[]": [str(mt.externalId) for mt in MetroTrack.objects.all()],
            "attributes[]": ["velDist", "Speedlimit", "Time"]
        }

        response = self.testHelper.make_get_request(URL, params, expected_response=None)
        content = json.loads(response.content.decode("utf-8"))

        self.assertEqual(len(content["answer"]), 9)
        for track in content["answer"]:
            self.assertIn("direction", track.keys())
            self.assertIn("startStation", track.keys())
            self.assertIn("endStation", track.keys())
            self.assertIn("Speedlimit", track["attributes"])
            self.assertIn("velDist", track["attributes"])
            self.assertIn("Time", track["attributes"])


class StrongModelVizTest(ModelVizTest):
    """ test web page to see output of strong model """

    def setUp(self):
        file_name = "6a9b3d69-1bb6-4582-9b72-ed2c591976a1.output"
        file_path = os.path.join("cmmmodel", "tests", file_name)

        self.set_up(Model.STRONG_MODEL_ID, file_path)

    def test_loadHTML(self):
        """ ask for strong output html file """

        URL = reverse("viz:strongModel", kwargs={"sceneId": self.scene_obj.id})
        self.testHelper.make_get_request(URL, {}, expected_response=None)

        # get error 404 because scene id does not exist
        URL = reverse("viz:strongModel", kwargs={"sceneId": 1000})
        self.testHelper.make_get_request(URL, {}, expected_response=None, expected_server_response_code=404)

    def test_getStrongModelDataWithExecutionRunning(self):
        """ ask model output data with last execution status == runnning """

        URL = reverse("viz:strongModelData", kwargs={"sceneId": self.scene_obj.id})

        params = {
            "direction": "g",
            "operationPeriod": "OP1",
            "metroLineName": "L1",
            "attributes[]": ["velDist", "Speedlimit", "Time"]
        }

        # with error because last execution of model is running
        response = self.testHelper.make_get_request(URL, params, expected_response=None)
        content = json.loads(response.content.decode("utf-8"))

        self.assertNotIn("answer", content.keys())
        self.assertEqual(content["status"]["code"],
                         Status.getJsonStatus(Status.LAST_MODEL_FINISHED_BADLY_ERROR, {})["status"]["code"])
        self.assertEqual(content["status"]["message"],
                         Status.getJsonStatus(Status.LAST_MODEL_FINISHED_BADLY_ERROR, {})["status"]["message"])

    def test_getStrongModelDataWithOKExecution(self):
        """ ask model output data with last execution status ok """

        URL = reverse("viz:strongModelData", kwargs={"sceneId": self.scene_obj.id})

        # simulate execution finished well
        ModelExecutionHistory.objects.update(status=ModelExecutionHistory.OK)

        params = {
            "direction": "g",
            "operationPeriod": "OP1",
            "metroLineName": "L1",
            "attributes[]": ["Tiempo_LR", "Potencia_drive_LR", "Potencia_ESS_LR"]
        }

        response = self.testHelper.make_get_request(URL, params, expected_response=None)
        content = json.loads(response.content.decode("utf-8"))

        self.assertEqual(len(content["answer"]), 1)
        for line in content["answer"]:
            self.assertIn("direction", line.keys())
            self.assertIn("Tiempo_LR", line["attributes"])
            self.assertIn("Potencia_drive_LR", line["attributes"])
            self.assertIn("Potencia_ESS_LR", line["attributes"])


class EnergyModelVizTest(ModelVizTest):
    """ test web page to see output of energy model """

    def setUp(self):
        file_name = "261fe0ff-5e87-4d26-866a-5496cc1bf064.output"
        file_path = os.path.join("cmmmodel", "tests", file_name)

        self.set_up(Model.ENERGY_MODEL_ID, file_path)

    def test_loadHTML(self):
        """ ask for strong output html file """

        URL = reverse("viz:energyModel", kwargs={"sceneId": self.scene_obj.id})
        self.testHelper.make_get_request(URL, {}, expected_response=None)

        # get error 404 because scene id does not exist
        URL = reverse("viz:energyModel", kwargs={"sceneId": 1000})
        self.testHelper.make_get_request(URL, {}, expected_response=None, expected_server_response_code=404)

    def test_getEnergyModelDataWithExecutionRunning(self):
        """ ask model output data with last execution status == runnning """

        URL = reverse("viz:energyModelData", kwargs={"sceneId": self.scene_obj.id})

        params = {
            "prefix": "totalConsumption",
        }

        # with error because last execution of model is running
        response = self.testHelper.make_get_request(URL, params, expected_response=None)
        content = json.loads(response.content.decode("utf-8"))

        self.assertNotIn("answer", content.keys())
        self.assertEqual(content["status"]["code"],
                         Status.getJsonStatus(Status.LAST_MODEL_FINISHED_BADLY_ERROR, {})["status"]["code"])
        self.assertEqual(content["status"]["message"],
                         Status.getJsonStatus(Status.LAST_MODEL_FINISHED_BADLY_ERROR, {})["status"]["message"])

    def test_getEnergyModelDataWithOKExecution(self):
        """ ask model output data with last execution status ok """

        URL = reverse("viz:energyModelData", kwargs={"sceneId": self.scene_obj.id})

        # simulate execution finished well
        ModelExecutionHistory.objects.update(status=ModelExecutionHistory.OK)

        params = {
            "prefix": "totalConsumption",
        }

        response = self.testHelper.make_get_request(URL, params, expected_response=None)
        content = json.loads(response.content.decode("utf-8"))

        self.assertEqual(len(content["answer"]), 1)
        for line in content["answer"]:
            print(line)
            self.assertIn("direction", line.keys())
            self.assertIn("Tiempo_LR", line["attributes"])
            self.assertIn("Potencia_drive_LR", line["attributes"])
            self.assertIn("Potencia_ESS_LR", line["attributes"])


class JavascriptTest(StaticLiveServerTestCase):
    """ You need put phantomjs in path visible por system """

    def setUp(self):
        self.url = self.live_server_url
        self.username = "felipe"
        self.password = "andres"
        self.helper = TestHelper(self, username=self.username, password=self.password)

    def login(self, browser):
        browser.fill("username", self.username)
        browser.fill("password", self.password)
        browser.find_by_value("Iniciar sesión").click()

    def go_next_step(self, browser):
        """ move to next step """
        time.sleep(0.5)
        browser.find_by_text("Guardar y avanzar").click()

    def complete_step_0(self, browser):
        """ fill all data for step 0 """
        line_names = ["L1", "L2"]
        station_quantities = [10, 12]

        connection_name = "ConnectionL1L2"
        avg_height = "7.2"
        avg_surface = "4300"
        connection_stations = ["S5", "S6"]

        # first metro line
        time.sleep(0.5)
        browser.find_by_id("addLine").click()
        time.sleep(0.5)
        browser.find_by_id("stationQuantity").fill(station_quantities[0])
        browser.find_by_id("createLine").click()

        # second metro line
        time.sleep(0.5)
        browser.find_by_id("addLine").click()
        time.sleep(0.5)
        browser.find_by_id("stationQuantity").fill(station_quantities[1])
        browser.find_by_id("createLine").click()

        # create depots
        time.sleep(0.5)
        browser.find_by_id("addDepot").click()
        time.sleep(0.5)
        browser.find_by_id("depotLineName")
        browser.find_option_by_text(line_names[0]).click()
        browser.find_by_id("createDepot").click()

        time.sleep(0.5)
        browser.find_by_id("addDepot").click()
        time.sleep(0.5)
        browser.find_option_by_text(line_names[1]).click()
        browser.find_by_id("createDepot").click()

        # create connection
        time.sleep(0.5)
        browser.find_by_id("addConnection").click()
        time.sleep(0.5)
        browser.find_by_id("connectionName").fill(connection_name)
        browser.find_by_id("avgHeight").fill(avg_height)
        browser.find_by_id("avgSurface").fill(avg_surface)

        browser.find_by_id("addConnectionStation").click()
        browser.find_by_id("addConnectionStation").click()

        for index, connection_station_name in enumerate(connection_stations):
            browser.select_by_text("connectionStationLine%s" % index, line_names[index])
            browser.select_by_text("connectionStationName%s" % index, connection_station_name)

        browser.find_by_id("createConnection").click()

    def complete_step_1(self, browser):
        """  upload topologic file """
        file_path = os.path.join(settings.BASE_DIR, "scene", "tests", "Escenario_topologico.xlsx")
        browser.find_by_id("step2form").click()
        #browser.attach_file("file", file_path)

    def create_scene(self, browser):
        """ create scene through webpage """

        # create scene
        browser.find_link_by_partial_href("admin/scene").click()
        browser.find_link_by_partial_href("scene/add").click()
        browser.fill("name", "scene_test")
        browser.find_by_name("_save").click()

        # create topologic variables
        self.complete_step_0(browser)
        self.go_next_step(browser)
        self.complete_step_1(browser)
        self.go_next_step(browser)

        time.sleep(30)
        #browser.find_by_id("addConnection").click()

    def test_loadChart(self):
        """ load web page and press button to show chart """
        executable = "phantomjs"
        browser = "phantomjs"

        executable = "chromedriver"
        browser = "chrome"

        if os.name == "nt":
            executable += ".exe"
        executable_path = {
            'executable_path': os.path.join(settings.BASE_DIR, "viz", "tests", "driver", executable)
        }

        # browser.driver.save_screenshot('your_screenshot.png')

        with Browser(browser, **executable_path) as browser:
            browser.driver.set_window_size(1120, 550)
            # Visit URL
            browser.visit(self.url)

            self.login(browser)
            self.create_scene(browser)

            #browser.find_by_value("Escenario 5").click()

            #print(browser.html)