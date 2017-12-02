from django.conf import settings

from splinter import Browser

import os


class SplinterTestHelper:

    def __init__(self, driver="chrome"):
        """  """
        if driver == "chrome":
            executable = "chromedriver"
            browser = "chrome"
        else:
            executable = "phantomjs"
            browser = "phantomjs"

        if os.name == "nt":
            executable += ".exe"
        executable_path = {
            'executable_path': os.path.join(settings.BASE_DIR, "viz", "tests", "driver", executable)
        }

        self.browser = Browser(browser, **executable_path)
        self.browser.driver.set_window_size(1120, 550)

    def get_browser(self):
        return self.browser

    def login(self, username, password):
        self.browser.fill("username", username)
        self.browser.fill("password", password)
        self.browser.find_by_value("Log in").click()
