from urlparse import urlparse
from wsgiref.simple_server import make_server
import threading

from selenium import webdriver
from pecan.deploy import deploy

from draughtcraft.tests import TestApp


class ServerThread(threading.Thread):
    """
    Run WSGI server on a background thread.
    Pass in WSGI app object and serve pages from it for Selenium browser.
    """

    HOST_BASE = "http://localhost:8521"

    def __init__(self, app):
        threading.Thread.__init__(self)
        self.app = app
        self.srv = None

    def run(self):
        """
        Open WSGI server to listen to HOST_BASE address
        """
        parts = urlparse(self.HOST_BASE)
        domain, port = parts.netloc.split(":")
        self.srv = make_server(domain, int(port), self.app)
        try:
            self.srv.serve_forever()
        except:
            import traceback
            traceback.print_exc()
            # Failed to start
            self.srv = None

    def quit(self):
        if self.srv:
            self.srv.shutdown()


class TestSeleniumApp(TestApp):

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

        self.server = ServerThread(self.app)
        self.server.start()

    def tearDown(self):
        super(TestSeleniumApp, self).tearDown()
        self.server.quit()

    def load_test_app(self, config):
        return deploy(config)

    def get(self, path):
        self.browser.get(ServerThread.HOST_BASE + path)
