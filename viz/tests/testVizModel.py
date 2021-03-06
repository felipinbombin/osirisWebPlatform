from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from django.utils import timezone

from scene.tests.testHelper import TestHelper
from scene.models import MetroLine, MetroStation, OperationPeriod, MetroTrack
from scene.statusResponse import Status

from cmmmodel.models import ModelExecutionHistory, CMMModel
from cmmmodel.saveJobResponse import process_answer
from cmmmodel.transform.processEnergyData import ProcessEnergyData

from viz.tests.splinterHelper import SplinterTestHelper

from unittest import skip

import uuid
import pickle
import os
import json
import gzip


def create_fake_execution(scene_obj, model_id, file_path):
    """  create record of execution """
    l1 = MetroLine.objects.create(scene=scene_obj, name="L1", externalId=uuid.uuid4())

    stations = [MetroStation.objects.create(name="S{}".format(index), externalId=uuid.uuid4(), metroLine=l1) for
                index in range(1, 11)]
    for index, station in enumerate(stations[:-1]):
        MetroTrack.objects.create(metroLine=l1, name="Track{}".format(index),
                                  startStation_id=station.id, endStation_id=stations[index + 1].id)

    l2 = MetroLine.objects.create(scene=scene_obj, name="L2", externalId=uuid.uuid4())
    stations = [MetroStation.objects.create(name="S{}".format(index), externalId=uuid.uuid4(), metroLine=l2) for
                index in range(12, 24)]
    for index, station in enumerate(stations[:-1]):
        MetroTrack.objects.create(metroLine=l2, name="Track{}".format(index),
                                  startStation_id=station.id, endStation_id=stations[index + 1].id)

    OperationPeriod.objects.create(scene=scene_obj, externalId=uuid.uuid4(), name="OP1",
                                   start="09:00:00", end="10:00:00", temperature=0, humidity=0,
                                   co2Concentration=0,
                                   solarRadiation=0, sunElevationAngle=0)
    OperationPeriod.objects.create(scene=scene_obj, externalId=uuid.uuid4(), name="OP2",
                                   start="10:00:00", end="11:00:00", temperature=0, humidity=0,
                                   co2Concentration=0,
                                   solarRadiation=0, sunElevationAngle=0)

    execution_obj = ModelExecutionHistory.objects.create(scene=scene_obj, model_id=model_id,
                                                         externalId=uuid.uuid4(), start=timezone.now())

    with gzip.open(file_path, "rb") as answer_file:
        answer = pickle.load(answer_file)
        answer = answer["output"]
        process_answer(answer, execution_obj)


speed_file_name = "speed.model_output.gz"
force_file_name = "force.model_output.gz"
energy_file_name = "energy.model_output.gz"
thermal_file_name = "heat.model_output.gz"


class SpeedModelVizTest(TestCase):
    """ test web page to see output of speed model """
    fixtures = ["models", "possibleQueue"]

    def setUp(self):
        file_path = os.path.join("cmmmodel", "tests", speed_file_name)

        self.test_helper = TestHelper(self)
        self.client = self.test_helper.get_logged_client()

        # create scene
        scene_name = "test scene name"
        self.scene_obj = self.test_helper.create_scene(scene_name)

        create_fake_execution(self.scene_obj, CMMModel.SPEED_MODEL_ID, file_path)

    def test_loadHTML(self):
        """ ask for speed output html file """

        url = reverse("viz:speedModel", kwargs={"scene_id": self.scene_obj.id})
        self.test_helper.make_get_request(url, {}, expected_response=None)

        # get error 404 because scene id does not exist
        url = reverse("viz:speedModel", kwargs={"scene_id": 1000})
        self.test_helper.make_get_request(url, {}, expected_response=None, expected_server_response_code=404)

    def test_getSpeedModelDataWithExecutionRunning(self):
        """ ask model output data with last execution status == runnning """

        url = reverse("viz:speedModelData", kwargs={"scene_id": self.scene_obj.id})

        params = {
            "direction": "g",
            "operationPeriod": "OP1",
            "metroLineName": "L1",
            "tracks[]": [str(mt.externalId) for mt in MetroTrack.objects.all()],
            "attributes[]": ["velDist", "Speedlimit", "Time"]
        }

        # with error because last execution of model is running
        response = self.test_helper.make_get_request(url, params, expected_response=None)
        content = json.loads(response.content.decode("utf-8"))

        self.assertNotIn("answer", content.keys())
        self.assertEqual(content["status"]["code"],
                         Status.getJsonStatus(Status.LAST_MODEL_FINISHED_BADLY_ERROR, {})["status"]["code"])
        self.assertEqual(content["status"]["message"],
                         Status.getJsonStatus(Status.LAST_MODEL_FINISHED_BADLY_ERROR, {})["status"]["message"])

    def test_getSpeedModelDataWithOKExecution(self):
        """ ask model output data with last execution status ok """

        url = reverse("viz:speedModelData", kwargs={"scene_id": self.scene_obj.id})

        # simulate execution finished well
        ModelExecutionHistory.objects.update(status=ModelExecutionHistory.OK)

        params = {
            "direction": "g",
            "operationPeriod": "OP1",
            "metroLineName": "L1",
            "tracks[]": [str(mt.externalId) for mt in MetroTrack.objects.all()],
            "attributes[]": ["velDist", "Speedlimit", "Time"]
        }

        response = self.test_helper.make_get_request(url, params, expected_response=None)
        content = json.loads(response.content.decode("utf-8"))

        self.assertEqual(len(content["answer"]), 9)
        for track in content["answer"]:
            self.assertIn("direction", track.keys())
            self.assertIn("startStation", track.keys())
            self.assertIn("endStation", track.keys())
            self.assertIn("Speedlimit", track["attributes"])
            self.assertIn("velDist", track["attributes"])
            self.assertIn("Time", track["attributes"])


class ForceModelVizTest(TestCase):
    """ test web page to see output of force model """
    fixtures = ["models", "possibleQueue"]

    def setUp(self):
        file_path = os.path.join("cmmmodel", "tests", force_file_name)

        self.test_helper = TestHelper(self)
        self.client = self.test_helper.get_logged_client()

        # create scene
        scene_name = "test scene name"
        self.scene_obj = self.test_helper.create_scene(scene_name)

        create_fake_execution(self.scene_obj, CMMModel.FORCE_MODEL_ID, file_path)

    def test_loadHTML(self):
        """ ask for force output html file """

        url = reverse("viz:forceModel", kwargs={"scene_id": self.scene_obj.id})
        self.test_helper.make_get_request(url, {}, expected_response=None)

        # get error 404 because scene id does not exist
        url = reverse("viz:forceModel", kwargs={"scene_id": 1000})
        self.test_helper.make_get_request(url, {}, expected_response=None, expected_server_response_code=404)

    def test_getForceModelDataWithExecutionRunning(self):
        """ ask model output data with last execution status == runnning """

        url = reverse("viz:forceModelData", kwargs={"scene_id": self.scene_obj.id})

        params = {
            "direction": "g",
            "operationPeriod": "OP1",
            "metroLineName": "L1",
            "attributes[]": ["velDist", "Speedlimit", "Time"]
        }

        # with error because last execution of model is running
        response = self.test_helper.make_get_request(url, params, expected_response=None)
        content = json.loads(response.content.decode("utf-8"))

        self.assertNotIn("answer", content.keys())
        self.assertEqual(content["status"]["code"],
                         Status.getJsonStatus(Status.LAST_MODEL_FINISHED_BADLY_ERROR, {})["status"]["code"])
        self.assertEqual(content["status"]["message"],
                         Status.getJsonStatus(Status.LAST_MODEL_FINISHED_BADLY_ERROR, {})["status"]["message"])

    def test_getForceModelDataWithOKExecution(self):
        """ ask model output data with last execution status ok """

        url = reverse("viz:forceModelData", kwargs={"scene_id": self.scene_obj.id})

        # simulate execution finished well
        ModelExecutionHistory.objects.update(status=ModelExecutionHistory.OK)

        params = {
            "direction": "g",
            "operationPeriod": "OP1",
            "metroLineName": "L1",
            "attributes[]": ["Tiempo_LR", "Potencia_drive_LR", "Potencia_ESS_LR"]
        }

        response = self.test_helper.make_get_request(url, params, expected_response=None)
        content = json.loads(response.content.decode("utf-8"))

        self.assertEqual(len(content["answer"]), 1)
        for line in content["answer"]:
            self.assertIn("direction", line.keys())
            self.assertIn("Tiempo_LR", line["attributes"])
            self.assertIn("Potencia_drive_LR", line["attributes"])
            self.assertIn("Potencia_ESS_LR", line["attributes"])


class EnergyModelVizTest(TestCase):
    """ test web page to see output of energy model """
    fixtures = ["models", "possibleQueue"]

    def setUp(self):
        file_path = os.path.join("cmmmodel", "tests", energy_file_name)

        self.test_helper = TestHelper(self)
        self.client = self.test_helper.get_logged_client()

        # create scene
        scene_name = "test scene name"
        self.scene_obj = self.test_helper.create_scene(scene_name)

        create_fake_execution(self.scene_obj, CMMModel.ENERGY_MODEL_ID, file_path)

    def test_loadHTML(self):
        """ ask for energy output html file """

        url = reverse("viz:energyModel", kwargs={"scene_id": self.scene_obj.id})
        self.test_helper.make_get_request(url, {}, expected_response=None)

        # get error 404 because scene id does not exist
        url = reverse("viz:energyModel", kwargs={"scene_id": 1000})
        self.test_helper.make_get_request(url, {}, expected_response=None, expected_server_response_code=404)

    def test_getEnergyModelDataWithExecutionRunning(self):
        """ ask model output data with last execution status == runnning """

        url = reverse("viz:energyModelData", kwargs={"scene_id": self.scene_obj.id})

        params = {
            "prefix": "totalConsumption",
        }

        # with error because last execution of model is running
        response = self.test_helper.make_get_request(url, params, expected_response=None)
        content = json.loads(response.content.decode("utf-8"))

        self.assertNotIn("answer", content.keys())
        self.assertEqual(content["status"]["code"],
                         Status.getJsonStatus(Status.LAST_MODEL_FINISHED_BADLY_ERROR, {})["status"]["code"])
        self.assertEqual(content["status"]["message"],
                         Status.getJsonStatus(Status.LAST_MODEL_FINISHED_BADLY_ERROR, {})["status"]["message"])

    def test_getEnergyModelDataWithOKExecution(self):
        """ ask model output data with last execution status ok """

        url = reverse("viz:energyModelData", kwargs={"scene_id": self.scene_obj.id})

        # simulate execution finished well
        ModelExecutionHistory.objects.update(status=ModelExecutionHistory.OK)

        params = {
            "prefix": "totalConsumption",
        }

        response = self.test_helper.make_get_request(url, params, expected_response=None)
        content = json.loads(response.content.decode("utf-8"))

        self.assertEqual(len(content["answer"]), 1)
        for line in content["answer"]:
            self.assertIn("prefix", line.keys())
            self.assertIn(ProcessEnergyData.dictionary_detail["recoveredEnergy"], line["attributes"])
            self.assertIn(ProcessEnergyData.dictionary_detail["substations"], line["attributes"])
            self.assertIn(ProcessEnergyData.dictionary_detail["tracks"], line["attributes"])
            self.assertIn(ProcessEnergyData.dictionary_detail["trains"], line["attributes"])


@skip("TODO: remove this when thermal model works")
class ThermalModelVizTest(TestCase):
    """ test web page to see output of thermal model """
    fixtures = ["models", "possibleQueue"]

    def setUp(self):
        file_path = os.path.join("cmmmodel", "tests", thermal_file_name)

        self.test_helper = TestHelper(self)
        self.client = self.test_helper.get_logged_client()

        # create scene
        scene_name = "test scene name"
        self.scene_obj = self.test_helper.create_scene(scene_name)

        create_fake_execution(self.scene_obj, CMMModel.THERMAL_MODEL_ID, file_path)

    def test_loadHTML(self):
        """ ask for energy output html file """

        url = reverse("viz:thermalModel", kwargs={"scene_id": self.scene_obj.id})
        self.test_helper.make_get_request(url, {}, expected_response=None)

        # get error 404 because scene id does not exist
        url = reverse("viz:thermalModel", kwargs={"scene_id": 1000})
        self.test_helper.make_get_request(url, {}, expected_response=None, expected_server_response_code=404)

    def test_getThermalModelDataWithExecutionRunning(self):
        """ ask model output data with last execution status == runnning """

        url = reverse("viz:thermalModelData", kwargs={"scene_id": self.scene_obj.id})

        params = {
            "prefix": "totalConsumption",
        }

        # with error because last execution of model is running
        response = self.test_helper.make_get_request(url, params, expected_response=None)
        content = json.loads(response.content.decode("utf-8"))

        self.assertNotIn("answer", content.keys())
        self.assertEqual(content["status"]["code"],
                         Status.getJsonStatus(Status.LAST_MODEL_FINISHED_BADLY_ERROR, {})["status"]["code"])
        self.assertEqual(content["status"]["message"],
                         Status.getJsonStatus(Status.LAST_MODEL_FINISHED_BADLY_ERROR, {})["status"]["message"])

    def test_getThermalModelDataWithOKExecution(self):
        """ ask model output data with last execution status ok """

        url = reverse("viz:thermalModelData", kwargs={"scene_id": self.scene_obj.id})

        # simulate execution finished well
        ModelExecutionHistory.objects.update(status=ModelExecutionHistory.OK)

        for prefix in ['heatAbsorvedByTheGroundOnTheStations', 'averageAbsolutelyHumidityDuringTheDay']:
            params = {
                "prefix": prefix,
            }

            response = self.test_helper.make_get_request(url, params, expected_response=None)
            content = json.loads(response.content.decode("utf-8"))

            self.assertEqual(len(content["answer"]), 1)
            for line in content["answer"]:
                self.assertIn("prefix", line.keys())
                self.assertIn(ProcessEnergyData.dictionary_detail["recoveredEnergy"], line["attributes"])
                self.assertIn(ProcessEnergyData.dictionary_detail["substations"], line["attributes"])
                self.assertIn(ProcessEnergyData.dictionary_detail["tracks"], line["attributes"])
                self.assertIn(ProcessEnergyData.dictionary_detail["trains"], line["attributes"])


class JavascriptModelVizTest(StaticLiveServerTestCase):
    """ test web page to see output of energy model """
    fixtures = ["models", "possibleQueue"]

    def setUp(self):
        self.dir_path = os.path.join("cmmmodel", "tests")

        username = "felipe"
        password = "felipe"

        self.test_helper = TestHelper(self, username=username, password=password)
        # create scene
        scene_name = "test scene name"
        self.scene_obj = self.test_helper.create_scene(scene_name)

        # connect to browser
        self.splinterHelper = SplinterTestHelper()
        self.browser = self.splinterHelper.get_browser()
        self.browser.visit(self.live_server_url)
        self.splinterHelper.login(username, password)

    def tearDown(self):
        self.browser.quit()

    def test_speed_model_javascript(self):
        file_path = os.path.join(self.dir_path, speed_file_name)

        create_fake_execution(self.scene_obj, CMMModel.SPEED_MODEL_ID, file_path)
        # simulate execution finished well
        ModelExecutionHistory.objects.update(status=ModelExecutionHistory.OK)

        # visit energy answer
        url = reverse("viz:speedModel", kwargs={"scene_id": self.scene_obj.id})
        self.browser.visit(self.live_server_url + url)

        self.browser.is_element_not_present_by_css("disabled", wait_time=5)
        self.browser.find_by_id("btnUpdateChart").click()
        self.assertTrue(self.browser.is_element_present_by_tag("canvas", wait_time=5))

    def test_force_model_javascript(self):
        file_path = os.path.join(self.dir_path, force_file_name)

        create_fake_execution(self.scene_obj, CMMModel.FORCE_MODEL_ID, file_path)
        # simulate execution finished well
        ModelExecutionHistory.objects.update(status=ModelExecutionHistory.OK)

        # visit energy answer
        url = reverse("viz:forceModel", kwargs={"scene_id": self.scene_obj.id})
        self.browser.visit(self.live_server_url + url)

        self.browser.is_element_not_present_by_css("disabled", wait_time=5)
        self.browser.find_by_id("btnUpdateChart").click()
        self.assertTrue(self.browser.is_element_present_by_tag("canvas", wait_time=5))

    def test_energy_model_javascript(self):
        file_path = os.path.join(self.dir_path, energy_file_name)

        create_fake_execution(self.scene_obj, CMMModel.ENERGY_MODEL_ID, file_path)
        # simulate execution finished well
        ModelExecutionHistory.objects.update(status=ModelExecutionHistory.OK)

        # visit energy answer
        url = reverse("viz:energyModel", kwargs={"scene_id": self.scene_obj.id})
        self.browser.visit(self.live_server_url + url)
        self.browser.find_by_id("btnUpdateChart").click()
        self.assertTrue(self.browser.is_element_present_by_tag("canvas", wait_time=5))

    def test_heat_model_javascript(self):
        file_path = os.path.join(self.dir_path, thermal_file_name)

        create_fake_execution(self.scene_obj, CMMModel.THERMAL_MODEL_ID, file_path)
        # simulate execution finished well
        ModelExecutionHistory.objects.update(status=ModelExecutionHistory.OK)

        # visit energy answer
        url = reverse("viz:thermalModel", kwargs={"scene_id": self.scene_obj.id})
        self.browser.visit(self.live_server_url + url)
        self.browser.find_by_id("btnUpdateChart").click()
        self.assertTrue(self.browser.is_element_present_by_tag("canvas", wait_time=5))
