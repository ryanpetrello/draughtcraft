import time

from selenium.webdriver.support.ui import Select

from draughtcraft import model
from draughtcraft.tests.selenium import TestSeleniumApp


class TestAllGrainBuilder(TestSeleniumApp):

    def setUp(self):
        super(TestAllGrainBuilder, self).setUp()

        model.Style(
            name='American IPA',
            min_og=1.056,
            max_og=1.075,
            min_fg=1.01,
            max_fg=1.018,
            min_ibu=40,
            max_ibu=70,
            min_srm=6,
            max_srm=15,
            min_abv=.055,
            max_abv=.075,
            category_number=14,
            style_letter='B'
        )
        model.Style(
            name='Spice, Herb, or Vegetable Beer',
            category_number=21,
            style_letter='A'
        )
        model.commit()

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
        self.wait.until(
            lambda driver:
                self.b.find_element_by_name("name").get_attribute("value") ==
                "Rocky Mountain River IPA"
        )
        self.assertEqual(
            "DraughtCraft - Rocky Mountain River IPA",
            self.b.title
        )
        self.assertEqual(
            "5",
            self.b.find_element_by_name("volume").get_attribute("value")
        )
        assert self.b.find_element_by_css_selector('.step.mash') is not None
        assert self.b.find_element_by_css_selector('.step.boil') is not None
        assert self.b.find_element_by_css_selector('.step.ferment') \
            is not None

    def test_name_change_save(self):
        self.b.find_element_by_name("name").send_keys("!")
        self.blur()
        time.sleep(2)

        self.b.refresh()
        self.wait.until(
            lambda driver:
                self.b.find_element_by_name("name").get_attribute("value") ==
                "Rocky Mountain River IPA!"
        )

    def test_style_choose(self):
        self.b.find_element_by_css_selector("span.selectBox-arrow").click()
        self.b.find_element_by_link_text("American IPA").click()
        self.blur()
        time.sleep(2)

        self.b.refresh()
        self.wait.until(
            lambda driver:
                self.b.find_element_by_css_selector(".selectBox-label").text ==
                "American IPA"
        )

        self.b.find_element_by_css_selector("span.selectBox-arrow").click()
        self.b.find_element_by_link_text("No Style Specified").click()
        self.blur()
        time.sleep(2)

        self.b.refresh()
        self.wait.until(
            lambda driver:
                self.b.find_element_by_css_selector(".selectBox-label").text ==
                "No Style Specified"
        )
