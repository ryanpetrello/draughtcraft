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

        time.sleep(.1)
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

    def test_volume_change_save(self):
        self.b.find_element_by_name("volume").clear()
        self.b.find_element_by_name("volume").send_keys("10")
        self.blur()
        time.sleep(2)

        self.b.refresh()
        self.wait.until(
            lambda driver:
            self.b.find_element_by_name("volume").get_attribute("value") ==
            "10"
        )

    def test_notes_change_save(self):
        self.b.find_element_by_css_selector('.notes textarea').send_keys("ABC")
        self.blur()
        time.sleep(2)

        self.b.refresh()
        self.wait.until(
            lambda driver:
            self.b.find_element_by_css_selector('.notes textarea')
                .get_attribute("value") == "ABC"
        )

    def test_remove_addition(self):
        model.Hop(
            name="Simcoe",
            origin='US',
            alpha_acid=13,
            description='Sample Description'
        )
        model.commit()
        self.b.refresh()

        for step in ('Mash', 'Boil', 'Ferment'):
            self.b.find_element_by_link_text(step).click()

            assert len(self.b.find_elements_by_css_selector(
                '.%s .ingredient-list .addition' % step.lower()
            )) == 0

            label = 'Add Dry Hops...' if step == 'Ferment' else 'Add Hops...'
            self.b.find_element_by_link_text(label).click()
            self.b.find_element_by_link_text("Simcoe (US)").click()
            time.sleep(2)

            assert len(self.b.find_elements_by_css_selector(
                '.%s .ingredient-list .addition:not(:empty)' % step.lower()
            )) == 1

            self.b.find_element_by_css_selector(
                '.%s .ingredient-list .addition .close a' % step.lower()
            ).click()
            time.sleep(2)
            self.b.refresh()

            assert len(self.b.find_elements_by_css_selector(
                '.%s .ingredient-list .addition' % step.lower()
            )) == 0

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

        for step in ('Mash', 'Boil'):
            self.b.find_element_by_link_text(step).click()

            assert len(self.b.find_elements_by_css_selector(
                '.%s .ingredient-list .addition' % step.lower()
            )) == 0

            self.b.find_element_by_link_text(
                "Add Malt/Fermentables..."
            ).click()
            self.b.find_element_by_link_text("2-Row (US)").click()

            assert len(self.b.find_elements_by_css_selector(
                '.%s .ingredient-list .addition:not(:empty)' % step.lower()
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

        for step in ('Mash', 'Boil'):
            self.b.find_element_by_link_text(step).click()

            assert len(self.b.find_elements_by_css_selector(
                '.%s .ingredient-list .addition' % step.lower()
            )) == 0

            self.b.find_element_by_link_text("Add Malt Extract...").click()
            self.b.find_element_by_link_text(
                "Cooper's Amber LME (Australian)"
            ).click()

            assert len(self.b.find_elements_by_css_selector(
                '.%s .ingredient-list .addition:not(:empty)' % step.lower()
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

        for step in ('Mash', 'Boil', 'Ferment'):
            self.b.find_element_by_link_text(step).click()

            assert len(self.b.find_elements_by_css_selector(
                '.%s .ingredient-list .addition' % step.lower()
            )) == 0

            label = 'Add Dry Hops...' if step == 'Ferment' else 'Add Hops...'
            self.b.find_element_by_link_text(label).click()
            self.b.find_element_by_link_text("Simcoe (US)").click()

            assert len(self.b.find_elements_by_css_selector(
                '.%s .ingredient-list .addition:not(:empty)' % step.lower()
            )) == 1

    def test_add_extra(self):
        model.Extra(
            name="Whirlfloc Tablet",
            description='Sample Description'
        )
        model.commit()
        self.b.refresh()

        for step in ('Mash', 'Boil', 'Ferment'):
            self.b.find_element_by_link_text(step).click()

            assert len(self.b.find_elements_by_css_selector(
                '.%s .ingredient-list .addition' % step.lower()
            )) == 0

            self.b.find_element_by_link_text("Add Misc...").click()
            self.b.find_element_by_link_text("Whirlfloc Tablet").click()

            assert len(self.b.find_elements_by_css_selector(
                '.%s .ingredient-list .addition:not(:empty)' % step.lower()
            )) == 1

    def test_mash_method_change(self):
        Select(
            self.b.find_element_by_name('mash_method')
        ).select_by_visible_text("Multi-Step")
        self.blur()
        time.sleep(2)

        self.b.refresh()
        self.wait.until(
            lambda driver:
            self.b.find_element_by_name("mash_method").
            get_attribute("value") == "MULTISTEP"
        )

    def test_mash_instructions_change(self):
        self.b.find_element_by_name('mash_instructions').clear()
        self.b.find_element_by_name('mash_instructions').send_keys(
            'Testing 1 2 3'
        )
        self.blur()
        time.sleep(2)

        self.b.refresh()
        self.wait.until(
            lambda driver:
            self.b.find_element_by_name("mash_instructions").
            get_attribute("value") == "Testing 1 2 3"
        )

    def test_boil_minutes(self):
        self.b.find_element_by_link_text('Boil').click()

        self.b.find_element_by_name('boil_minutes').clear()
        self.b.find_element_by_name('boil_minutes').send_keys('90')
        self.blur()
        time.sleep(2)

        self.b.refresh()
        self.wait.until(
            lambda driver:
            self.b.find_element_by_name("boil_minutes").
            get_attribute("value") == "90"
        )

    def test_fermentation_schedule_change(self):
        self.b.find_element_by_link_text('Ferment').click()

        self.b.find_element_by_link_text("Add...").click()
        self.b.find_element_by_link_text("Add...").click()

        days = self.b.find_elements_by_css_selector('.process select.days')
        temps = self.b.find_elements_by_css_selector(
            '.process select.fahrenheit'
        )
        assert len(days) == 3
        assert len(temps) == 3

        for i, el in enumerate(days):
            Select(el).select_by_visible_text(str(14 + (7 * i)))

        for j, el in enumerate(temps):
            Select(el).select_by_visible_text(str(68 + (2 * j)))

        self.blur()
        time.sleep(2)

        self.b.refresh()

        time.sleep(1)
        days = self.b.find_elements_by_css_selector('.process select.days')
        temps = self.b.find_elements_by_css_selector(
            '.process select.fahrenheit'
        )
        assert len(days) == 3
        assert len(temps) == 3
        for i, d in enumerate(days):
            assert d.get_attribute('value') == str(14 + (7 * i))
        for j, t in enumerate(temps):
            assert t.get_attribute('value') == str(68 + (2 * j))

    def test_change_fermentable_amount(self):
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

        for step in ('Mash', 'Boil'):
            self.b.find_element_by_link_text(step).click()

            self.b.find_element_by_link_text(
                "Add Malt/Fermentables..."
            ).click()
            self.b.find_element_by_link_text("2-Row (US)").click()

            i = self.b.find_element_by_css_selector(
                '.%s .addition .amount input' % step.lower()
            )
            i.clear()
            i.send_keys('10 lb')
            self.blur()
            time.sleep(2)

            self.b.refresh()

            i = self.b.find_element_by_css_selector(
                '.%s .addition .amount input' % step.lower()
            )
            assert i.get_attribute('value') == '10 lb'

    def test_metric_entry(self):
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

        for step in ('Mash', 'Boil'):
            self.b.find_element_by_link_text(step).click()

            self.b.find_element_by_link_text(
                "Add Malt/Fermentables..."
            ).click()
            self.b.find_element_by_link_text("2-Row (US)").click()

            i = self.b.find_element_by_css_selector(
                '.%s .addition .amount input' % step.lower()
            )
            i.clear()
            i.send_keys('1 kg')
            self.blur()
            time.sleep(2)

            self.b.refresh()

            i = self.b.find_element_by_css_selector(
                '.%s .addition .amount input' % step.lower()
            )
            assert i.get_attribute('value') == '2.204 lb'

    def test_change_hop_form(self):
        model.Hop(
            name="Simcoe",
            origin='US',
            alpha_acid=13,
            description='Sample Description'
        )
        model.commit()
        self.b.refresh()

        for step in ('Mash', 'Boil', 'Ferment'):
            self.b.find_element_by_link_text(step).click()

            label = 'Add Dry Hops...' if step == 'Ferment' else 'Add Hops...'
            self.b.find_element_by_link_text(label).click()
            self.b.find_element_by_link_text("Simcoe (US)").click()

            s = Select(self.b.find_element_by_css_selector(
                '.%s .addition .form select' % step.lower()
            ))
            s.select_by_visible_text('Pellet')
            self.blur()
            time.sleep(2)

            self.b.refresh()

            s = self.b.find_element_by_css_selector(
                '.%s .addition .form select' % step.lower()
            )
            assert s.get_attribute('value') == 'PELLET'

    def test_change_hop_aa(self):
        model.Hop(
            name="Simcoe",
            origin='US',
            alpha_acid=13,
            description='Sample Description'
        )
        model.commit()
        self.b.refresh()

        for step in ('Mash', 'Boil', 'Ferment'):
            self.b.find_element_by_link_text(step).click()

            label = 'Add Dry Hops...' if step == 'Ferment' else 'Add Hops...'
            self.b.find_element_by_link_text(label).click()
            self.b.find_element_by_link_text("Simcoe (US)").click()

            i = self.b.find_element_by_css_selector(
                '.%s .addition .unit input' % step.lower()
            )
            i.clear()
            i.send_keys('12')
            self.blur()
            time.sleep(2)

            self.b.refresh()

            i = self.b.find_element_by_css_selector(
                '.%s .addition .unit input' % step.lower()
            )
            assert i.get_attribute('value') == '12'

    def test_change_hop_boil_time(self):
        model.Hop(
            name="Simcoe",
            origin='US',
            alpha_acid=13,
            description='Sample Description'
        )
        model.commit()
        self.b.refresh()

        self.b.find_element_by_link_text('Boil').click()

        self.b.find_element_by_link_text('Add Hops...').click()
        self.b.find_element_by_link_text("Simcoe (US)").click()

        selects = self.b.find_elements_by_css_selector(
            '.boil .addition .time select'
        )
        Select(selects[1]).select_by_visible_text('45 min')
        self.blur()
        time.sleep(2)

        self.b.refresh()

        selects = self.b.find_elements_by_css_selector(
            '.boil .addition .time select'
        )
        assert selects[1].get_attribute('value') == '45'

    def test_change_hop_first_wort(self):
        model.Hop(
            name="Simcoe",
            origin='US',
            alpha_acid=13,
            description='Sample Description'
        )
        model.commit()
        self.b.refresh()

        self.b.find_element_by_link_text('Boil').click()

        self.b.find_element_by_link_text('Add Hops...').click()
        self.b.find_element_by_link_text("Simcoe (US)").click()

        selects = self.b.find_elements_by_css_selector(
            '.boil .addition .time select'
        )
        Select(selects[0]).select_by_visible_text('First Wort')
        assert not selects[1].is_displayed()

    def test_change_hop_flameout(self):
        model.Hop(
            name="Simcoe",
            origin='US',
            alpha_acid=13,
            description='Sample Description'
        )
        model.commit()
        self.b.refresh()

        self.b.find_element_by_link_text('Boil').click()

        self.b.find_element_by_link_text('Add Hops...').click()
        self.b.find_element_by_link_text("Simcoe (US)").click()

        selects = self.b.find_elements_by_css_selector(
            '.boil .addition .time select'
        )
        Select(selects[0]).select_by_visible_text('Flame Out')
        assert not selects[1].is_displayed()

    def test_yeast_step(self):
        model.Yeast(
            name='Wyeast 1056 - American Ale',
            type='ALE',
            form='LIQUID',
            attenuation=.75,
            flocculation='MEDIUM/HIGH'
        )
        model.commit()
        self.b.refresh()

        self.b.find_element_by_link_text('Ferment').click()
        self.b.find_element_by_link_text('Add Yeast...').click()
        self.b.find_element_by_link_text('Wyeast 1056 - American Ale').click()

        Select(self.b.find_element_by_css_selector(
            '.ferment .addition select'
        )).select_by_visible_text('Secondary')
        time.sleep(2)

        self.b.refresh()

        assert self.b.find_element_by_css_selector(
            '.ferment .addition select'
        ).get_attribute('value') == 'SECONDARY'


class TestExtractBuilder(TestSeleniumApp):

    def setUp(self):
        super(TestExtractBuilder, self).setUp()

        self.get("/")
        self.b.find_element_by_link_text("Create Your Own Recipe").click()

        time.sleep(.1)
        self.b.find_element_by_id("name").clear()
        self.b.find_element_by_id("name").send_keys("Rocky Mountain River IPA")
        Select(
            self.b.find_element_by_id("type")
        ).select_by_visible_text("Extract")
        self.b.find_element_by_css_selector("button.ribbon").click()

    @property
    def b(self):
        return self.browser

    def test_mash_missing(self):
        assert len(
            self.b.find_elements_by_css_selector('.step.boil h2 a')
        ) == 2


class TestMetricBuilder(TestSeleniumApp):

    def setUp(self):
        super(TestMetricBuilder, self).setUp()

        self.get("/")
        self.b.find_element_by_link_text("Create Your Own Recipe").click()

        self.b.find_element_by_link_text("Want Metric Units?").click()

        time.sleep(.1)
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
            "20",
            self.b.find_element_by_name("volume").get_attribute("value")
        )
        assert self.b.find_element_by_css_selector('.step.mash') is not None
        assert self.b.find_element_by_css_selector('.step.boil') is not None
        assert self.b.find_element_by_css_selector('.step.ferment') \
            is not None

    def test_volume_change_save(self):
        self.b.find_element_by_name("volume").clear()
        self.b.find_element_by_name("volume").send_keys("10")
        self.blur()
        time.sleep(2)

        self.b.refresh()
        self.wait.until(
            lambda driver:
            self.b.find_element_by_name("volume").get_attribute("value") ==
            "10"
        )

    def test_metric_ingredient_amount(self):
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

        for step in ('Mash', 'Boil'):
            self.b.find_element_by_link_text(step).click()

            self.b.find_element_by_link_text(
                "Add Malt/Fermentables..."
            ).click()
            self.b.find_element_by_link_text("2-Row (US)").click()

            i = self.b.find_element_by_css_selector(
                '.%s .addition .amount input' % step.lower()
            )
            i.clear()
            i.send_keys('1 kg')
            self.blur()
            time.sleep(2)

            self.b.refresh()

            i = self.b.find_element_by_css_selector(
                '.%s .addition .amount input' % step.lower()
            )
            assert i.get_attribute('value') == '1 kg'

    def test_fermentation_schedule_change(self):
        self.b.find_element_by_link_text('Ferment').click()

        self.b.find_element_by_link_text("Add...").click()
        self.b.find_element_by_link_text("Add...").click()

        days = self.b.find_elements_by_css_selector('.process select.days')
        temps = self.b.find_elements_by_css_selector(
            '.process select.fahrenheit'
        )
        assert len(days) == 3
        assert len(temps) == 3

        for i, el in enumerate(days):
            Select(el).select_by_visible_text(str(14 + (7 * i)))

        for j, el in enumerate(temps):
            Select(el).select_by_visible_text(str(20 + (2 * j)))

        self.blur()
        time.sleep(2)

        self.b.refresh()

        time.sleep(1)
        days = self.b.find_elements_by_css_selector('.process select.days')
        temps = self.b.find_elements_by_css_selector(
            '.process select.fahrenheit'
        )
        assert len(days) == 3
        assert len(temps) == 3
        for i, d in enumerate(days):
            assert d.get_attribute('value') == str(14 + (7 * i))
        for j, t in enumerate(temps):
            assert t.get_attribute('value') == str(20 + (2 * j))
