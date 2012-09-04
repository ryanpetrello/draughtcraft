from urlparse import urlparse
from wsgiref.simple_server import make_server
import multiprocessing

from selenium import webdriver
from pecan.deploy import deploy

from draughtcraft.tests import TestApp


class TestSeleniumApp(TestApp):

    HOST_BASE = "http://localhost:8521"

    @classmethod
    def setUpClass(cls):
        """
        Create a Firefox test browser instance with hacked settings.

        We do this only once per testing module.
        """
        TestApp.setUpClass()
        profile = webdriver.firefox.firefox_profile.FirefoxProfile()
        cls.browser = webdriver.Firefox(firefox_profile=profile)

    @classmethod
    def tearDownClass(cls):
        TestApp.tearDownClass()
        cls.browser.quit()

    def setUp(self):
        super(TestSeleniumApp, self).setUp()

        # Start a server process
        parts = urlparse(self.HOST_BASE)
        domain, port = parts.netloc.split(":")
        self.server_process = multiprocessing.Process(
            target=make_server(domain, int(port), self.app).serve_forever
        )
        self.server_process.start()

    def tearDown(self):
        super(TestSeleniumApp, self).tearDown()
        self.server_process.terminate()
        self.server_process.join()
        del(self.server_process)

    def load_test_app(self, config):
        return deploy(config)

    def get(self, path):
        self.browser.get(self.HOST_BASE + path)
