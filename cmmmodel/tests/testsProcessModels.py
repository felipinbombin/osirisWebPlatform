import gzip
import os
import pickle
import uuid
from shutil import copyfile

from django.test import TestCase
from django.utils import timezone

from cmmmodel.models import ModelExecutionQueue, CMMModel, ModelExecutionHistory
from cmmmodel.saveJobResponse import save_model_response, process_answer
from cmmmodel.tests.helper import APIHelper
from scene.models import MetroLine, MetroTrack, MetroStation, OperationPeriod
from scene.models import Scene
from scene.tests.testHelper import TestHelper
from viz.models import ModelAnswer, EnergyCenterModelAnswer

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

        self.api_helper = APIHelper(self.testHelper, self.scene_obj, TEST_MODEL_ID)

    def create_topologic_system(self):
        """ create fake topologic system to test process data answer (for viz and excel file) """

        l1 = MetroLine.objects.create(scene=self.scene_obj, name="L1", externalId=uuid.uuid4())

        stations = [MetroStation.objects.create(name="S{}".format(index), externalId=uuid.uuid4(), metroLine=l1) for
                    index in range(1, 11)]
        for index, station in enumerate(stations[:-1]):
            MetroTrack.objects.create(metroLine=l1, name="Track{}".format(index),
                                      startStation_id=station.id, endStation_id=stations[index + 1].id)

        l2 = MetroLine.objects.create(scene=self.scene_obj, name="L2", externalId=uuid.uuid4())
        stations = [MetroStation.objects.create(name="S{}".format(index), externalId=uuid.uuid4(), metroLine=l2) for
                    index in range(12, 24)]
        for index, station in enumerate(stations[:-1]):
            MetroTrack.objects.create(metroLine=l2, name="Track{}".format(index),
                                      startStation_id=station.id, endStation_id=stations[index + 1].id)

        OperationPeriod.objects.create(scene=self.scene_obj, externalId=uuid.uuid4(), name="OP1",
                                       start="09:00:00", end="10:00:00", temperature=0, humidity=0,
                                       co2Concentration=0,
                                       solarRadiation=0, sunElevationAngle=0)
        OperationPeriod.objects.create(scene=self.scene_obj, externalId=uuid.uuid4(), name="OP2",
                                       start="10:00:00", end="11:00:00", temperature=0, humidity=0,
                                       co2Concentration=0,
                                       solarRadiation=0, sunElevationAngle=0)

    def test_saveJob(self):
        """ simulate a call from cluster after finish model execution to saveJobResponse file """

        # simulate scene is ready to run
        self.scene_obj.status = Scene.OK
        self.scene_obj.save()
        # create execution record
        file_name = "speed.model_output.gz"
        # print(file_path)
        std_out = ""
        std_err = ""
        external_id = uuid.uuid4()
        meh = ModelExecutionHistory.objects.create(scene=self.scene_obj, model_id=CMMModel.SPEED_MODEL_ID,
                                                   externalId=external_id, start=timezone.now())

        # added test model to queue to test queue model execution process
        ModelExecutionQueue.objects.create(modelExecutionHistory=meh, model_id=CMMModel.FORCE_MODEL_ID)

        file_path = os.path.join(os.getcwd(), "media", "modelOutput", file_name)
        copyfile(os.path.join(os.getcwd(), 'cmmmodel', 'tests', file_name), file_path)

        save_model_response(str(external_id), file_name, std_out, std_err)

        # remove file
        os.remove(file_path)

        # stop execution model in cmm cluster (queued model)
        self.api_helper.stop_test_model()

        meh.refresh_from_db()
        self.assertEqual(meh.status, ModelExecutionHistory.OK)
        self.assertIsNotNone(meh.end)

        std_err = "not empty"
        save_model_response(str(external_id), file_path, std_out, std_err)
        meh.refresh_from_db()
        self.assertEqual(meh.status, ModelExecutionHistory.ERROR)

    def test_processSpeedAnswer(self):
        """ test load data from speed model output dict based on situation of file """
        file_name = "speed.model_output.gz"
        file_path = os.path.join("cmmmodel", "tests", file_name)

        self.create_topologic_system()

        execution_obj = ModelExecutionHistory.objects.create(scene=self.scene_obj, model_id=CMMModel.SPEED_MODEL_ID,
                                                             externalId=uuid.uuid4(), start=timezone.now())

        with gzip.open(file_path, "rb") as answer_file:
            answer = pickle.load(answer_file)
            answer = answer["output"]
            process_answer(answer, execution_obj)

        self.assertEqual(ModelAnswer.objects.count(), 147132)

    def test_processForceAnswer(self):
        """ test load data from speed model output dict based on situation of file """
        file_name = "force.model_output.gz"
        file_path = os.path.join("cmmmodel", "tests", file_name)

        self.create_topologic_system()

        execution_obj = ModelExecutionHistory.objects.create(scene=self.scene_obj, model_id=CMMModel.FORCE_MODEL_ID,
                                                             externalId=uuid.uuid4(), start=timezone.now())

        with gzip.open(file_path, "rb") as answer_file:
            answer = pickle.load(answer_file)
            answer = answer["output"]
            process_answer(answer, execution_obj)

        self.assertEqual(ModelAnswer.objects.count(), 27657)

    def test_processEnergyAnswer(self):
        """ test load data from speed model output dict based on situation of file """
        file_name = "energy.model_output.gz"
        file_path = os.path.join("cmmmodel", "tests", file_name)

        self.create_topologic_system()

        execution_obj = ModelExecutionHistory.objects.create(scene=self.scene_obj, model_id=CMMModel.ENERGY_MODEL_ID,
                                                             externalId=uuid.uuid4(), start=timezone.now())

        with gzip.open(file_path, "rb") as answer_file:
            answer = pickle.load(answer_file)
            answer = answer["output"]
            process_answer(answer, execution_obj)

        self.assertEqual(ModelAnswer.objects.count(), 21)

    def test_processHeatAnswer(self):
        """ test load data from heat model output dict based on situation of file """
        file_name = "heat.model_output.gz"
        file_path = os.path.join("cmmmodel", "tests", file_name)

        self.create_topologic_system()

        execution_obj = ModelExecutionHistory.objects.create(scene=self.scene_obj, model_id=CMMModel.THERMAL_MODEL_ID,
                                                             externalId=uuid.uuid4(), start=timezone.now())
        with gzip.open(file_path, "rb") as answer_file:
            answer = pickle.load(answer_file)
            answer = answer["output"]
            process_answer(answer, execution_obj)

        self.assertEqual(ModelAnswer.objects.count(), 3336)

    def test_processEnergyCenterModelAnswer(self):
        """ test load data from energy center model output dict based on situation of file """
        file_name = "energycenter.model_output.gz"
        file_path = os.path.join("cmmmodel", "tests", file_name)

        self.create_topologic_system()

        execution_obj = ModelExecutionHistory.objects.create(scene=self.scene_obj,
                                                             model_id=CMMModel.ENERGY_CENTER_MODEL_ID,
                                                             externalId=uuid.uuid4(), start=timezone.now())
        with gzip.open(file_path, "rb") as answer_file:
            answer = pickle.load(answer_file)
            answer = answer["output"]
            process_answer(answer, execution_obj)

        self.assertEqual(EnergyCenterModelAnswer.objects.count(), 4896)
