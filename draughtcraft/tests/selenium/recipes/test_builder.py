import time

from selenium.webdriver.support.ui import Select
from draughtcraft.tests.selenium import TestSeleniumApp


class TestAllGrainBuilder(TestSeleniumApp):

    def setUp(self):
        super(TestAllGrainBuilder, self).setUp()
        self.get("/")
        self.b.find_element_by_link_text("Create Your Own Recipe").click()

        self.b.find_element_by_id("name").clear()
        self.b.find_element_by_id("name").send_keys("Rocky Mountain River IPA")
        Select(
            self.b.find_element_by_id("type")
        ).select_by_visible_text("All Grain")
        self.b.find_element_by_css_selector("button.ribbon").click()

    @property
    def b(self):
        return self.browser

    def blur(self):
        self.b.find_element_by_css_selector(".logo").click()

    def test_defaults(self):
        for i in range(500):
            try:
                b = self.b
                self.assertEqual(
                    "DraughtCraft - Rocky Mountain River IPA",
                    b.title
                )
                self.assertEqual(
                    "Rocky Mountain River IPA",
                    b.find_element_by_name("name").get_attribute("value")
                )
                self.assertEqual(
                    "5",
                    b.find_element_by_name("volume").get_attribute("value")
                )
                assert b.find_element_by_css_selector('.step.mash') is not None
                assert b.find_element_by_css_selector('.step.boil') is not None
                assert b.find_element_by_css_selector('.step.ferment') \
                    is not None
                break
            except:
                pass
            time.sleep(.01)
        else:
            self.fail('timed out')

    def test_name_change_save(self):
        self.b.find_element_by_name("name").send_keys("!")
        self.blur()
        time.sleep(1)

        self.b.refresh()
        for i in range(500):
            try:
                self.assertEqual(
                    "Rocky Mountain River IPA!",
                    self.b.find_element_by_name("name").get_attribute("value")
                )
                break
            except:
                pass
            time.sleep(.01)
        else:
            self.fail('timed out')
