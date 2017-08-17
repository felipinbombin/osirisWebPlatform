# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from django.urls import reverse
from django.conf import settings

from scene.models import Scene, MetroLineMetric
from scene.statusResponse import Status

from testHelper import TestHelper

from collections import defaultdict

import os
import json

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

    def test_FillAllSteps(self):
        """ simulate correct process to create a escene """
        pass

    def test_change_scene_name(self):
        """ test step 1 without previous step """
        pass
        #self.upload_topologic_file()
        #self.check_step_1()

    def test_delete_scene(self):
        """ test step 2 without previous step """
        pass
        #self.check_step_2()