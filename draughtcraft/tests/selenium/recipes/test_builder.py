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
        self.b.find_element_by_link_text("No Style Specified").click()
        self.b.find_element_by_link_text("American IPA").click()
        self.blur()
        time.sleep(2)

        self.b.refresh()
        self.wait.until(
            lambda driver:
                self.b.find_element_by_css_selector(".selectBox-label").text ==
                "American IPA"
        )

        self.b.find_element_by_link_text("American IPA").click()
        self.b.find_element_by_link_text("No Style Specified").click()
        self.blur()
        time.sleep(2)

        self.b.refresh()
        self.wait.until(
            lambda driver:
                self.b.find_element_by_css_selector(".selectBox-label").text ==
                "No Style Specified"
        )

    def test_add_malt(self):
        model.Fermentable(
            name='2-Row',
            type='MALT',
            origin='US',
            ppg=36,
            lovibond=2,
            description='Sample Description'
        )
        model.commit()

        self.b.refresh()
        assert len(self.b.find_elements_by_css_selector(
            '.mash .ingredient-list .addition'
        )) == 0

        self.b.find_element_by_link_text("Add Malt/Fermentables...").click()
        self.b.find_element_by_link_text("2-Row (US)").click()

        assert len(self.b.find_elements_by_css_selector(
            '.mash .ingredient-list .addition:not(:empty)'
        )) == 1

    def test_add_extract(self):
        model.Fermentable(
            name="Cooper's Amber LME",
            type='EXTRACT',
            origin='AUSTRALIAN',
            ppg=36,
            lovibond=13.3,
            description='Sample Description'
        )
        model.commit()

        self.b.refresh()
        assert len(self.b.find_elements_by_css_selector(
            '.mash .ingredient-list .addition'
        )) == 0

        self.b.find_element_by_link_text("Add Malt Extract...").click()
        self.b.find_element_by_link_text("Cooper's Amber LME (Australian)").click()

        assert len(self.b.find_elements_by_css_selector(
            '.mash .ingredient-list .addition:not(:empty)'
        )) == 1

    def test_add_hop(self):
        model.Hop(
            name="Simcoe",
            origin='US',
            alpha_acid=13,
            description='Sample Description'
        )
        model.commit()

        self.b.refresh()
        assert len(self.b.find_elements_by_css_selector(
            '.mash .ingredient-list .addition'
        )) == 0

        self.b.find_element_by_link_text("Add Hops...").click()
        self.b.find_element_by_link_text("Simcoe (US)").click()

        assert len(self.b.find_elements_by_css_selector(
            '.mash .ingredient-list .addition:not(:empty)'
        )) == 1

    def test_add_extra(self):
        model.Extra(
            name="Whirlfloc Tablet",
            description='Sample Description'
        )
        model.commit()

        self.b.refresh()
        assert len(self.b.find_elements_by_css_selector(
            '.mash .ingredient-list .addition'
        )) == 0

        self.b.find_element_by_link_text("Add Misc...").click()
        self.b.find_element_by_link_text("Whirlfloc Tablet").click()

        assert len(self.b.find_elements_by_css_selector(
            '.mash .ingredient-list .addition:not(:empty)'
        )) == 1
