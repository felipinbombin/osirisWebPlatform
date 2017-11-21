from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from scene.tests.testHelper import TestHelper
from viz.tests.splinterHelper import SplinterTestHelper

import time


class JavascriptTest(StaticLiveServerTestCase):
    """  """

    def setUp(self):
        self.url = self.live_server_url
        self.username = "felipe"
        self.password = "andres"
        self.helper = TestHelper(self, username=self.username, password=self.password)
        self.splinterHelper = SplinterTestHelper()

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

        with self.splinterHelper.get_browser() as browser:
            browser.driver.set_window_size(1120, 550)
            # Visit URL
            browser.visit(self.url)

            self.splinterHelper.login(self.username, self.password)
            self.create_scene(browser)

            #browser.find_by_value("Escenario 5").click()

            #print(browser.html)