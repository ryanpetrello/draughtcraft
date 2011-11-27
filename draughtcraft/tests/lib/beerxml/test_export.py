from draughtcraft                   import model
from draughtcraft.lib.beerxml       import export
from draughtcraft.tests             import TestModel
from datetime                       import timedelta
from unittest                       import TestCase

def prepare_xml(xml):
    return ''.join([n.strip() for n in xml])


class TestField(TestCase):

    def test_field_value(self):
        f = export.Field()
        f.name = 'name'
        assert f.get_value('Cascade') == {'name': 'Cascade'}

    def test_field_value_with_transform(self):
        f = export.Field(lambda x: x.upper())
        f.name = 'name'
        assert f.get_value('Cascade') == {'name': 'CASCADE'}

    def test_unicode_coercion(self):
        f = export.Field()
        f.name = 'name'
        assert f.get_value('Wyeast 2565 - K\xf6lsch') == {'name': 'Wyeast 2565 - Kolsch'}


class TestNode(TestCase):

    def test_declarative_fields(self):
        n = export.Node()
        assert 'version' in n.__fields__
        assert n.__fields__['version'].__class__ == export.Field
        assert n.__values__['version'] == 1
        assert n.render() == '<NODE><VERSION>1</VERSION></NODE>'

    def test_declarative_subtype(self):
        class Ingredient(export.Node):
            name = export.Field()

        n = Ingredient(name = '2-Row')

        assert 'version' in n.__fields__
        assert 'name' in n.__fields__
        assert n.__fields__['version'].__class__ == export.Field
        assert n.__values__['version'] == 1
        assert n.__fields__['name'].__class__ == export.Field
        assert n.__values__['name'] == '2-Row'
        assert n.render() == prepare_xml([
            '<INGREDIENT>',
            '   <NAME>2-Row</NAME>',
            '   <VERSION>1</VERSION>',
            '</INGREDIENT>'
        ])


class NodeSet(TestCase):

    def test_simple_nodeset(self):
        class Hop(export.Node):
            name = export.Field()

        class Recipe(export.Node):
            name = export.Field()
            hops = export.NodeSet(Hop)

        n = Recipe(
            name    = 'Rocky Mountain River IPA',
            hops    = [
                Hop(name = 'Cascade')
            ]
        )
        
        assert 'version' in n.__fields__
        assert 'name' in n.__fields__
        assert n.__fields__['version'].__class__ == export.Field
        assert n.__values__['version'] == 1
        assert n.render() == prepare_xml([
            '<RECIPE>',
            '   <HOPS>',
            '       <HOP>',
            '           <NAME>Cascade</NAME>',
            '           <VERSION>1</VERSION>',
            '       </HOP>',
            '   </HOPS>',
            '   <NAME>Rocky Mountain River IPA</NAME>',
            '   <VERSION>1</VERSION>',
            '</RECIPE>'
        ])

    def test_singular_node_reference(self):
        class Style(export.Node):
            name = export.Field()

        class Recipe(export.Node):
            name    = export.Field()
            style   = export.Field()

        n = Recipe(
            name    = 'Rocky Mountain River IPA',
            style   = Style(name = 'American IPA')
        )
        
        assert 'version' in n.__fields__
        assert 'name' in n.__fields__
        assert n.__fields__['version'].__class__ == export.Field
        assert n.__values__['version'] == 1
        assert n.render() == prepare_xml([
            '<RECIPE>',
            '   <NAME>Rocky Mountain River IPA</NAME>',
            '   <STYLE>',
            '       <NAME>American IPA</NAME>',
            '       <VERSION>1</VERSION>',
            '   </STYLE>',
            '   <VERSION>1</VERSION>',
            '</RECIPE>'
        ])


class TestRecipeNodes(TestCase):

    def test_hop(self):
        assert export.Hop(
            name    = 'Target',
            alpha   = 10.5,
            amount  = 0.0625,
            use     = 'BOIL',
            time    = 60,
            notes   = 'English mid-to-high alpha hop bred from Kent Goldings.',
            form    = 'LEAF',
            origin  = 'GERMAN'
        ).render() == prepare_xml([
            '<HOP>',
            '   <ALPHA>10.5</ALPHA>',
            '   <AMOUNT>0.0625</AMOUNT>',
            '   <FORM>LEAF</FORM>',
            '   <NAME>Target</NAME>',
            '   <NOTES>English mid-to-high alpha hop bred from Kent Goldings.</NOTES>',
            '   <ORIGIN>GERMAN</ORIGIN>',
            '   <TIME>60</TIME>',
            '   <USE>BOIL</USE>',
            '   <VERSION>1</VERSION>',
            '</HOP>'
        ])

    def test_fermentable(self):
        assert export.Fermentable(
            name    = 'US 2-Row Malt',
            type    = 'Grain',
            amount  = 1,
            YIELD   = 80.00,
            color   = 1.8,
            origin  = 'US'
        ).render() == prepare_xml([
            '<FERMENTABLE>',
            '   <AMOUNT>1</AMOUNT>',
            '   <COLOR>1.8</COLOR>',
            '   <NAME>US 2-Row Malt</NAME>',
            '   <ORIGIN>US</ORIGIN>',
            '   <TYPE>Grain</TYPE>',
            '   <VERSION>1</VERSION>',
            '   <YIELD>80.0</YIELD>',
            '</FERMENTABLE>'
        ])

    def test_yeast(self):
        assert export.Yeast(
            name        = 'Wyeast 1056 - American Ale',
            type        = 'Ale',
            amount      = .135,
            form        = 'Liquid',
            attenuation = 75.0
        ).render() == prepare_xml([
            '<YEAST>',
            '   <AMOUNT>0.135</AMOUNT>',
            '   <ATTENUATION>75.0</ATTENUATION>',
            '   <FORM>Liquid</FORM>',
            '   <NAME>Wyeast 1056 - American Ale</NAME>',
            '   <TYPE>Ale</TYPE>',
            '   <VERSION>1</VERSION>',
            '</YEAST>'
        ])

    def test_misc(self):
        assert export.Misc(
            name        = 'Irish Moss',
            type        = 'Fining',
            use         = 'Boil',
            amount      = .125,
            time        = 15,
        ).render() == prepare_xml([
            '<MISC>',
            '   <AMOUNT>0.125</AMOUNT>',
            '   <NAME>Irish Moss</NAME>',
            '   <TIME>15</TIME>',
            '   <TYPE>Fining</TYPE>',
            '   <USE>Boil</USE>',
            '   <VERSION>1</VERSION>'
            '</MISC>'
        ])


class TestRecipeExport(TestModel):

    def test_simplest_recipe(self):
        model.Recipe(
            type            = 'MASH',
            name            = 'Rocky Mountain River IPA',
            author          = model.User(
                first_name  = u'Ryan',
                last_name   = u'Petrello'
            ),
            gallons         = 5,
            boil_minutes    = 60,
            notes           = u'This is my favorite recipe.'
        )
        model.commit()

        recipe = model.Recipe.query.first()
        xml = recipe.to_xml()

        assert xml == prepare_xml([
        '<RECIPE>',
        '   <BATCH_SIZE>18.927</BATCH_SIZE>',
        '   <BOIL_SIZE>23.65875</BOIL_SIZE>',
        '   <BOIL_TIME>60</BOIL_TIME>',
        '   <BREWER>Ryan Petrello</BREWER>',
        '   <EFFICIENCY>75.0</EFFICIENCY>',
        '   <FERMENTABLES/>',
        '   <FERMENTATION_STAGES>0</FERMENTATION_STAGES>',
        '   <HOPS/>',
        '   <MASH/>',
        '   <MISCS/>',
        '   <NAME>Rocky Mountain River IPA</NAME>',
        '   <NOTES>This is my favorite recipe.</NOTES>',
        '   <STYLE>',
        '       <CATEGORY>No Style Chosen</CATEGORY>',
        '       <CATEGORY_NUMBER>0</CATEGORY_NUMBER>',
        '       <COLOR_MAX>0</COLOR_MAX>',
        '       <COLOR_MIN>0</COLOR_MIN>',
        '       <FG_MAX>0</FG_MAX>',
        '       <FG_MIN>0</FG_MIN>',
        '       <IBU_MAX>0</IBU_MAX>',
        '       <IBU_MIN>0</IBU_MIN>',
        '       <NAME></NAME>',
        '       <OG_MAX>0</OG_MAX>',
        '       <OG_MIN>0</OG_MIN>',
        '       <STYLE_LETTER></STYLE_LETTER>',
        '       <TYPE>None</TYPE>',
        '       <VERSION>1</VERSION>',
        '   </STYLE>',
        '   <TYPE>All Grain</TYPE>',
        '   <VERSION>1</VERSION>',
        '   <WATERS/>',
        '   <YEASTS/>',
        '</RECIPE>'
        ])

    def test_all_grain_type(self):
        model.Recipe(
            type            = 'MASH',
            name            = 'Rocky Mountain River IPA',
            author          = model.User(
                first_name  = u'Ryan',
                last_name   = u'Petrello'
            ),
            gallons         = 5,
            boil_minutes    = 60,
            notes           = u'This is my favorite recipe.'
        )
        model.commit()

        recipe = model.Recipe.query.first()
        xml = recipe.to_xml()
        assert '<TYPE>All Grain</TYPE>' in xml

    def test_mini_mash_type(self):
        model.Recipe(
            type            = 'MINIMASH',
            name            = 'Rocky Mountain River IPA',
            author          = model.User(
                first_name  = u'Ryan',
                last_name   = u'Petrello'
            ),
            gallons         = 5,
            boil_minutes    = 60,
            notes           = u'This is my favorite recipe.'
        )
        model.commit()

        recipe = model.Recipe.query.first()
        xml = recipe.to_xml()
        assert '<TYPE>Partial Mash</TYPE>' in xml

    def test_steeped_grains_type(self):
        model.Recipe(
            type            = 'EXTRACTSTEEP',
            name            = 'Rocky Mountain River IPA',
            author          = model.User(
                first_name  = u'Ryan',
                last_name   = u'Petrello'
            ),
            gallons         = 5,
            boil_minutes    = 60,
            notes           = u'This is my favorite recipe.'
        )
        model.commit()

        recipe = model.Recipe.query.first()
        xml = recipe.to_xml()
        assert '<TYPE>Partial Mash</TYPE>' in xml

    def test_extract_type(self):
        model.Recipe(
            type            = 'EXTRACT',
            name            = 'Rocky Mountain River IPA',
            author          = model.User(
                first_name  = u'Ryan',
                last_name   = u'Petrello'
            ),
            gallons         = 5,
            boil_minutes    = 60,
            notes           = u'This is my favorite recipe.'
        )
        model.commit()

        recipe = model.Recipe.query.first()
        xml = recipe.to_xml()
        assert '<TYPE>Extract</TYPE>' in xml
        assert '<EFFICIENCY>' not in xml

    def test_recipe_with_fermentation_steps(self):
        model.Recipe(
            type               = 'MASH',
            name               = 'Rocky Mountain River IPA',
            author             = model.User(
                first_name  = u'Ryan',
                last_name   = u'Petrello'
            ),
            gallons            = 5,
            boil_minutes       = 60,
            notes              = u'This is my favorite recipe.',
            fermentation_steps = [
                model.FermentationStep(
                    step       = 'PRIMARY',
                    days       = 14,
                    fahrenheit = 65
                ),
                model.FermentationStep(
                    step       = 'SECONDARY',
                    days       = 28,
                    fahrenheit = 72
                ),
                model.FermentationStep(
                    step       = 'TERTIARY',
                    days       = 28,
                    fahrenheit = 42
                )
            ]
        )
        model.commit()

        recipe = model.Recipe.query.first()
        xml = recipe.to_xml()

        assert xml == prepare_xml([
        '<RECIPE>',
        '   <BATCH_SIZE>18.927</BATCH_SIZE>',
        '   <BOIL_SIZE>23.65875</BOIL_SIZE>',
        '   <BOIL_TIME>60</BOIL_TIME>',
        '   <BREWER>Ryan Petrello</BREWER>',
        '   <EFFICIENCY>75.0</EFFICIENCY>',
        '   <FERMENTABLES/>',
        '   <FERMENTATION_STAGES>3</FERMENTATION_STAGES>',
        '   <HOPS/>',
        '   <MASH/>',
        '   <MISCS/>',
        '   <NAME>Rocky Mountain River IPA</NAME>',
        '   <NOTES>This is my favorite recipe.</NOTES>',
        '   <PRIMARY_AGE>14</PRIMARY_AGE>',
        '   <PRIMARY_TEMP>18.0</PRIMARY_TEMP>',
        '   <SECONDARY_AGE>28</SECONDARY_AGE>',
        '   <SECONDARY_TEMP>22.0</SECONDARY_TEMP>',
        '   <STYLE>',
        '       <CATEGORY>No Style Chosen</CATEGORY>',
        '       <CATEGORY_NUMBER>0</CATEGORY_NUMBER>',
        '       <COLOR_MAX>0</COLOR_MAX>',
        '       <COLOR_MIN>0</COLOR_MIN>',
        '       <FG_MAX>0</FG_MAX>',
        '       <FG_MIN>0</FG_MIN>',
        '       <IBU_MAX>0</IBU_MAX>',
        '       <IBU_MIN>0</IBU_MIN>',
        '       <NAME></NAME>',
        '       <OG_MAX>0</OG_MAX>',
        '       <OG_MIN>0</OG_MIN>',
        '       <STYLE_LETTER></STYLE_LETTER>',
        '       <TYPE>None</TYPE>',
        '       <VERSION>1</VERSION>',
        '   </STYLE>',
        '   <TERTIARY_AGE>28</TERTIARY_AGE>',
        '   <TERTIARY_TEMP>6.0</TERTIARY_TEMP>',
        '   <TYPE>All Grain</TYPE>',
        '   <VERSION>1</VERSION>',
        '   <WATERS/>',
        '   <YEASTS/>',
        '</RECIPE>'
        ])

    def test_recipe_with_style(self):
        style = model.Style(
            name            = 'American Pale Ale',
            url             = 'http://www.bjcp.org/2008styles/style10.php#1a',

            # Gravities
            min_og          = 1.045,
            max_og          = 1.06,
            min_fg          = 1.01,
            max_fg          = 1.015,

            # IBU
            min_ibu         = 30,
            max_ibu         = 45,

            # SRM
            min_srm         = 5,
            max_srm         = 14,

            # ABV
            min_abv         = 0.045,
            max_abv         = 0.06,

            category        = 'American Ale',
            category_number = 10,
            style_letter    = 'A',

            type            = 'ALE'
        )
        model.Recipe(
            type            = 'MASH',
            name            = 'Rocky Mountain River IPA',
            author          = model.User(
                first_name  = u'Ryan',
                last_name   = u'Petrello'
            ),
            style           = style,
            gallons         = 5,
            boil_minutes    = 60,
            notes           = u'This is my favorite recipe.'
        )
        model.commit()

        recipe = model.Recipe.query.first()
        xml = recipe.to_xml()

        assert xml == prepare_xml([
        '<RECIPE>',
        '   <BATCH_SIZE>18.927</BATCH_SIZE>',
        '   <BOIL_SIZE>23.65875</BOIL_SIZE>',
        '   <BOIL_TIME>60</BOIL_TIME>',
        '   <BREWER>Ryan Petrello</BREWER>',
        '   <EFFICIENCY>75.0</EFFICIENCY>',
        '   <FERMENTABLES/>',
        '   <FERMENTATION_STAGES>0</FERMENTATION_STAGES>',
        '   <HOPS/>',
        '   <MASH/>',
        '   <MISCS/>',
        '   <NAME>Rocky Mountain River IPA</NAME>',
        '   <NOTES>This is my favorite recipe.</NOTES>',
        '   <STYLE>',
        '       <ABV_MAX>0.06</ABV_MAX>',
        '       <ABV_MIN>0.045</ABV_MIN>',
        '       <CATEGORY>American Ale</CATEGORY>',
        '       <CATEGORY_NUMBER>10</CATEGORY_NUMBER>',
        '       <COLOR_MAX>14</COLOR_MAX>',
        '       <COLOR_MIN>5</COLOR_MIN>',
        '       <FG_MAX>1.015</FG_MAX>',
        '       <FG_MIN>1.01</FG_MIN>',
        '       <IBU_MAX>45</IBU_MAX>',
        '       <IBU_MIN>30</IBU_MIN>',
        '       <NAME>American Pale Ale</NAME>',
        '       <OG_MAX>1.06</OG_MAX>',
        '       <OG_MIN>1.045</OG_MIN>',
        '       <STYLE_GUIDE>BJCP</STYLE_GUIDE>',
        '       <STYLE_LETTER>A</STYLE_LETTER>',
        '       <TYPE>Ale</TYPE>',
        '       <VERSION>1</VERSION>',
        '   </STYLE>',
        '   <TYPE>All Grain</TYPE>',
        '   <VERSION>1</VERSION>',
        '   <WATERS/>',
        '   <YEASTS/>',
        '</RECIPE>'
        ])


class TestRecipeWithHops(TestModel):

    def test_60_minute_boil(self):
        model.Recipe(
            type            = 'MASH',
            name            = 'Rocky Mountain River IPA',
            author          = model.User(
                first_name  = u'Ryan',
                last_name   = u'Petrello'
            ),
            gallons         = 5,
            boil_minutes    = 60,
            notes           = u'This is my favorite recipe.',
            additions       = [
                model.HopAddition(
                    use         = 'BOIL',
                    amount      = 1,
                    unit        = 'POUND',
                    duration    = timedelta(seconds = 3600),
                    form        = 'PELLET',
                    hop         = model.Hop(
                        name        = 'Cascade',
                        description = 'The Cascade Hop',
                        alpha_acid  = 4.5,
                        origin      = 'US'
                    )
                )
            ]
        )
        model.commit()

        recipe = model.Recipe.query.first()
        xml = recipe.to_xml()

        assert prepare_xml([
        '<HOP>',
        '   <ALPHA>4.5</ALPHA>',
        '   <AMOUNT>0.45359237</AMOUNT>', # 1lb in kg
        '   <FORM>Pellet</FORM>',
        '   <NAME>Cascade</NAME>',
        '   <NOTES>The Cascade Hop</NOTES>',
        '   <ORIGIN>US</ORIGIN>',
        '   <TIME>60</TIME>',
        '   <USE>Boil</USE>',
        '   <VERSION>1</VERSION>',
        '</HOP>'
        ]) in xml

    def test_hops_in_mash(self):
        model.Recipe(
            type            = 'MASH',
            name            = 'Rocky Mountain River IPA',
            author          = model.User(
                first_name  = u'Ryan',
                last_name   = u'Petrello'
            ),
            gallons         = 5,
            boil_minutes    = 60,
            notes           = u'This is my favorite recipe.',
            additions       = [
                model.HopAddition(
                    use         = 'MASH',
                    amount      = 1,
                    unit        = 'POUND',
                    form        = 'PELLET',
                    hop         = model.Hop(
                        name        = 'Cascade',
                        description = 'The Cascade Hop',
                        alpha_acid  = 4.5,
                        origin      = 'US'
                    )
                )
            ]
        )
        model.commit()

        recipe = model.Recipe.query.first()
        xml = recipe.to_xml()

        assert prepare_xml([
        '<HOP>',
        '   <ALPHA>4.5</ALPHA>',
        '   <AMOUNT>0.45359237</AMOUNT>', # 1lb in kg
        '   <FORM>Pellet</FORM>',
        '   <NAME>Cascade</NAME>',
        '   <NOTES>The Cascade Hop</NOTES>',
        '   <ORIGIN>US</ORIGIN>',
        '   <TIME>0</TIME>',
        '   <USE>Mash</USE>',
        '   <VERSION>1</VERSION>',
        '</HOP>'
        ]) in xml

    def test_hops_post_boil(self):
        model.Recipe(
            type            = 'MASH',
            name            = 'Rocky Mountain River IPA',
            author          = model.User(
                first_name  = u'Ryan',
                last_name   = u'Petrello'
            ),
            gallons         = 5,
            boil_minutes    = 60,
            notes           = u'This is my favorite recipe.',
            additions       = [
                model.HopAddition(
                    use         = 'POST-BOIL',
                    amount      = 1,
                    unit        = 'POUND',
                    form        = 'PELLET',
                    hop         = model.Hop(
                        name        = 'Cascade',
                        description = 'The Cascade Hop',
                        alpha_acid  = 4.5,
                        origin      = 'US'
                    )
                )
            ]
        )
        model.commit()

        recipe = model.Recipe.query.first()
        xml = recipe.to_xml()

        assert prepare_xml([
        '<HOP>',
        '   <ALPHA>4.5</ALPHA>',
        '   <AMOUNT>0.45359237</AMOUNT>', # 1lb in kg
        '   <FORM>Pellet</FORM>',
        '   <NAME>Cascade</NAME>',
        '   <NOTES>The Cascade Hop</NOTES>',
        '   <ORIGIN>US</ORIGIN>',
        '   <TIME>0</TIME>',
        '   <USE>Aroma</USE>',
        '   <VERSION>1</VERSION>',
        '</HOP>'
        ]) in xml

    def test_hops_flame_out(self):
        model.Recipe(
            type            = 'MASH',
            name            = 'Rocky Mountain River IPA',
            author          = model.User(
                first_name  = u'Ryan',
                last_name   = u'Petrello'
            ),
            gallons         = 5,
            boil_minutes    = 60,
            notes           = u'This is my favorite recipe.',
            additions       = [
                model.HopAddition(
                    use         = 'FLAME OUT',
                    amount      = 1,
                    unit        = 'POUND',
                    form        = 'PELLET',
                    hop         = model.Hop(
                        name        = 'Cascade',
                        description = 'The Cascade Hop',
                        alpha_acid  = 4.5,
                        origin      = 'US'
                    )
                )
            ]
        )
        model.commit()

        recipe = model.Recipe.query.first()
        xml = recipe.to_xml()

        assert prepare_xml([
        '<HOP>',
        '   <ALPHA>4.5</ALPHA>',
        '   <AMOUNT>0.45359237</AMOUNT>', # 1lb in kg
        '   <FORM>Pellet</FORM>',
        '   <NAME>Cascade</NAME>',
        '   <NOTES>The Cascade Hop</NOTES>',
        '   <ORIGIN>US</ORIGIN>',
        '   <TIME>0</TIME>',
        '   <USE>Aroma</USE>',
        '   <VERSION>1</VERSION>',
        '</HOP>'
        ]) in xml

    def test_primary_dry_hop(self):
        model.Recipe(
            type            = 'MASH',
            name            = 'Rocky Mountain River IPA',
            author          = model.User(
                first_name  = u'Ryan',
                last_name   = u'Petrello'
            ),
            gallons         = 5,
            boil_minutes    = 60,
            notes           = u'This is my favorite recipe.',
            additions       = [
                model.HopAddition(
                    use         = 'PRIMARY',
                    amount      = 1,
                    unit        = 'POUND',
                    form        = 'PELLET',
                    hop         = model.Hop(
                        name        = 'Cascade',
                        description = 'The Cascade Hop',
                        alpha_acid  = 4.5,
                        origin      = 'US'
                    )
                )
            ]
        )
        model.commit()

        recipe = model.Recipe.query.first()
        xml = recipe.to_xml()

        assert prepare_xml([
        '<HOP>',
        '   <ALPHA>4.5</ALPHA>',
        '   <AMOUNT>0.45359237</AMOUNT>', # 1lb in kg
        '   <FORM>Pellet</FORM>',
        '   <NAME>Cascade</NAME>',
        '   <NOTES>The Cascade Hop</NOTES>',
        '   <ORIGIN>US</ORIGIN>',
        '   <TIME>0</TIME>',
        '   <USE>Dry Hop</USE>',
        '   <VERSION>1</VERSION>',
        '</HOP>'
        ]) in xml

    def test_secondary_dry_hop(self):
        model.Recipe(
            type            = 'MASH',
            name            = 'Rocky Mountain River IPA',
            author          = model.User(
                first_name  = u'Ryan',
                last_name   = u'Petrello'
            ),
            gallons         = 5,
            boil_minutes    = 60,
            notes           = u'This is my favorite recipe.',
            additions       = [
                model.HopAddition(
                    use         = 'SECONDARY',
                    amount      = 1,
                    unit        = 'POUND',
                    duration    = timedelta(seconds = 3600),
                    form        = 'PELLET',
                    hop         = model.Hop(
                        name        = 'Cascade',
                        description = 'The Cascade Hop',
                        alpha_acid  = 4.5,
                        origin      = 'US'
                    )
                )
            ]
        )
        model.commit()

        recipe = model.Recipe.query.first()
        xml = recipe.to_xml()

        assert prepare_xml([
        '<HOP>',
        '   <ALPHA>4.5</ALPHA>',
        '   <AMOUNT>0.45359237</AMOUNT>', # 1lb in kg
        '   <FORM>Pellet</FORM>',
        '   <NAME>Cascade</NAME>',
        '   <NOTES>The Cascade Hop</NOTES>',
        '   <ORIGIN>US</ORIGIN>',
        '   <TIME>60</TIME>',
        '   <USE>Dry Hop</USE>',
        '   <VERSION>1</VERSION>',
        '</HOP>'
        ]) in xml

    def test_tertiary_dry_hop(self):
        model.Recipe(
            type            = 'MASH',
            name            = 'Rocky Mountain River IPA',
            author          = model.User(
                first_name  = u'Ryan',
                last_name   = u'Petrello'
            ),
            gallons         = 5,
            boil_minutes    = 60,
            notes           = u'This is my favorite recipe.',
            additions       = [
                model.HopAddition(
                    use         = 'TERTIARY',
                    amount      = 1,
                    unit        = 'POUND',
                    duration    = timedelta(seconds = 3600),
                    form        = 'PELLET',
                    hop         = model.Hop(
                        name        = 'Cascade',
                        description = 'The Cascade Hop',
                        alpha_acid  = 4.5,
                        origin      = 'US'
                    )
                )
            ]
        )
        model.commit()

        recipe = model.Recipe.query.first()
        xml = recipe.to_xml()

        assert prepare_xml([
        '<HOP>',
        '   <ALPHA>4.5</ALPHA>',
        '   <AMOUNT>0.45359237</AMOUNT>', # 1lb in kg
        '   <FORM>Pellet</FORM>',
        '   <NAME>Cascade</NAME>',
        '   <NOTES>The Cascade Hop</NOTES>',
        '   <ORIGIN>US</ORIGIN>',
        '   <TIME>60</TIME>',
        '   <USE>Dry Hop</USE>',
        '   <VERSION>1</VERSION>',
        '</HOP>'
        ]) in xml

    def test_hops_in_ounces(self):
        model.Recipe(
            type            = 'MASH',
            name            = 'Rocky Mountain River IPA',
            author          = model.User(
                first_name  = u'Ryan',
                last_name   = u'Petrello'
            ),
            gallons         = 5,
            boil_minutes    = 60,
            notes           = u'This is my favorite recipe.',
            additions       = [
                model.HopAddition(
                    use         = 'BOIL',
                    amount      = 1,
                    unit        = 'OUNCE',
                    duration    = timedelta(seconds = 3600),
                    form        = 'PELLET',
                    hop         = model.Hop(
                        name        = 'Cascade',
                        description = 'The Cascade Hop',
                        alpha_acid  = 4.5,
                        origin      = 'US'
                    )
                )
            ]
        )
        model.commit()

        recipe = model.Recipe.query.first()
        xml = recipe.to_xml()

        assert prepare_xml([
        '<HOP>',
        '   <ALPHA>4.5</ALPHA>',
        '   <AMOUNT>0.0283495231</AMOUNT>',
        '   <FORM>Pellet</FORM>',
        '   <NAME>Cascade</NAME>',
        '   <NOTES>The Cascade Hop</NOTES>',
        '   <ORIGIN>US</ORIGIN>',
        '   <TIME>60</TIME>',
        '   <USE>Boil</USE>',
        '   <VERSION>1</VERSION>',
        '</HOP>'
        ]) in xml


class TestRecipeWithFermentables(TestModel):
    
    def test_malt(self):
        model.Recipe(
            type            = 'MASH',
            name            = 'Rocky Mountain River IPA',
            author          = model.User(
                first_name  = u'Ryan',
                last_name   = u'Petrello'
            ),
            gallons         = 5,
            boil_minutes    = 60,
            notes           = u'This is my favorite recipe.',
            additions       = [
                model.RecipeAddition(
                    use         = 'MASH',
                    amount      = 1,
                    unit        = 'POUND',
                    duration    = timedelta(seconds = 3600),
                    fermentable = model.Fermentable(
                        name        = '2-Row',
                        ppg         = 36,
                        lovibond    = 2,
                        type        = 'MALT',
                        description = 'A standard base grain.',
                        origin      = 'US'
                    )
                )
            ]
        )
        model.commit()

        recipe = model.Recipe.query.first()
        xml = recipe.to_xml()

        assert prepare_xml([
        '<FERMENTABLE>',
        '   <ADD_AFTER_BOIL>False</ADD_AFTER_BOIL>',
        '   <AMOUNT>0.45359237</AMOUNT>',
        '   <COLOR>2.0</COLOR>',
        '   <NAME>2-Row</NAME>',
        '   <NOTES>A standard base grain.</NOTES>',
        '   <ORIGIN>US</ORIGIN>',
        '   <TYPE>Grain</TYPE>',
        '   <VERSION>1</VERSION>',
        '   <YIELD>78.0</YIELD>',
        '</FERMENTABLE>'
        ]) in xml

    def test_grain(self):
        model.Recipe(
            type            = 'MASH',
            name            = 'Rocky Mountain River IPA',
            author          = model.User(
                first_name  = u'Ryan',
                last_name   = u'Petrello'
            ),
            gallons         = 5,
            boil_minutes    = 60,
            notes           = u'This is my favorite recipe.',
            additions       = [
                model.RecipeAddition(
                    use         = 'MASH',
                    amount      = 1,
                    unit        = 'POUND',
                    duration    = timedelta(seconds = 3600),
                    fermentable = model.Fermentable(
                        name        = 'Flaked Oats',
                        ppg         = 37,
                        lovibond    = 1,
                        type        = 'GRAIN',
                        description = 'Adds body.',
                        origin      = 'US'
                    )
                )
            ]
        )
        model.commit()

        recipe = model.Recipe.query.first()
        xml = recipe.to_xml()

        assert prepare_xml([
        '<FERMENTABLE>',
        '   <ADD_AFTER_BOIL>False</ADD_AFTER_BOIL>',
        '   <AMOUNT>0.45359237</AMOUNT>',
        '   <COLOR>1.0</COLOR>',
        '   <NAME>Flaked Oats</NAME>',
        '   <NOTES>Adds body.</NOTES>',
        '   <ORIGIN>US</ORIGIN>',
        '   <TYPE>Grain</TYPE>',
        '   <VERSION>1</VERSION>',
        '   <YIELD>80.0</YIELD>',
        '</FERMENTABLE>'
        ]) in xml

    def test_sugar(self):
        model.Recipe(
            type            = 'MASH',
            name            = 'Rocky Mountain River IPA',
            author          = model.User(
                first_name  = u'Ryan',
                last_name   = u'Petrello'
            ),
            gallons         = 5,
            boil_minutes    = 60,
            notes           = u'This is my favorite recipe.',
            additions       = [
                model.RecipeAddition(
                    use         = 'MASH',
                    amount      = 1,
                    unit        = 'POUND',
                    duration    = timedelta(seconds = 3600),
                    fermentable = model.Fermentable(
                        name        = 'Sucrose',
                        ppg         = 46,
                        lovibond    = 1,
                        type        = 'SUGAR',
                        description = 'Table Sugar',
                        origin      = 'US'
                    )
                )
            ]
        )
        model.commit()

        recipe = model.Recipe.query.first()
        xml = recipe.to_xml()

        assert prepare_xml([
        '<FERMENTABLE>',
        '   <ADD_AFTER_BOIL>False</ADD_AFTER_BOIL>',
        '   <AMOUNT>0.45359237</AMOUNT>',
        '   <COLOR>1.0</COLOR>',
        '   <NAME>Sucrose</NAME>',
        '   <NOTES>Table Sugar</NOTES>',
        '   <ORIGIN>US</ORIGIN>',
        '   <TYPE>Sugar</TYPE>',
        '   <VERSION>1</VERSION>',
        '   <YIELD>100.0</YIELD>',
        '</FERMENTABLE>'
        ]) in xml

    def test_extract(self):
        model.Recipe(
            type            = 'MASH',
            name            = 'Rocky Mountain River IPA',
            author          = model.User(
                first_name  = u'Ryan',
                last_name   = u'Petrello'
            ),
            gallons         = 5,
            boil_minutes    = 60,
            notes           = u'This is my favorite recipe.',
            additions       = [
                model.RecipeAddition(
                    use         = 'BOIL',
                    amount      = 1,
                    unit        = 'POUND',
                    duration    = timedelta(seconds = 3600),
                    fermentable = model.Fermentable(
                        name        = 'Briess Munich LME',
                        ppg         = 35,
                        lovibond    = 8,
                        type        = 'EXTRACT',
                        description = 'Light Munich Liquid Extract',
                        origin      = 'US'
                    )
                )
            ]
        )
        model.commit()

        recipe = model.Recipe.query.first()
        xml = recipe.to_xml()

        assert prepare_xml([
        '<FERMENTABLE>',
        '   <ADD_AFTER_BOIL>False</ADD_AFTER_BOIL>',
        '   <AMOUNT>0.45359237</AMOUNT>',
        '   <COLOR>8.0</COLOR>',
        '   <NAME>Briess Munich LME</NAME>',
        '   <NOTES>Light Munich Liquid Extract</NOTES>',
        '   <ORIGIN>US</ORIGIN>',
        '   <TYPE>Extract</TYPE>',
        '   <VERSION>1</VERSION>',
        '   <YIELD>76.0</YIELD>',
        '</FERMENTABLE>'
        ]) in xml

    def test_dry_extract(self):
        model.Recipe(
            type            = 'MASH',
            name            = 'Rocky Mountain River IPA',
            author          = model.User(
                first_name  = u'Ryan',
                last_name   = u'Petrello'
            ),
            gallons         = 5,
            boil_minutes    = 60,
            notes           = u'This is my favorite recipe.',
            additions       = [
                model.RecipeAddition(
                    use         = 'BOIL',
                    amount      = 1,
                    unit        = 'POUND',
                    duration    = timedelta(seconds = 3600),
                    fermentable = model.Fermentable(
                        name        = 'Briess Munich DME',
                        ppg         = 35,
                        lovibond    = 8,
                        type        = 'EXTRACT',
                        description = 'Light Munich Dry Extract',
                        origin      = 'US'
                    )
                )
            ]
        )
        model.commit()

        recipe = model.Recipe.query.first()
        xml = recipe.to_xml()

        assert prepare_xml([
        '<FERMENTABLE>',
        '   <ADD_AFTER_BOIL>False</ADD_AFTER_BOIL>',
        '   <AMOUNT>0.45359237</AMOUNT>',
        '   <COLOR>8.0</COLOR>',
        '   <NAME>Briess Munich DME</NAME>',
        '   <NOTES>Light Munich Dry Extract</NOTES>',
        '   <ORIGIN>US</ORIGIN>',
        '   <TYPE>Dry Extract</TYPE>',
        '   <VERSION>1</VERSION>',
        '   <YIELD>76.0</YIELD>',
        '</FERMENTABLE>'
        ]) in xml

    def test_adjunct(self):
        model.Recipe(
            type            = 'MASH',
            name            = 'Rocky Mountain River IPA',
            author          = model.User(
                first_name  = u'Ryan',
                last_name   = u'Petrello'
            ),
            gallons         = 5,
            boil_minutes    = 60,
            notes           = u'This is my favorite recipe.',
            additions       = [
                model.RecipeAddition(
                    use         = 'BOIL',
                    amount      = 1,
                    unit        = 'POUND',
                    duration    = timedelta(seconds = 3600),
                    fermentable = model.Fermentable(
                        name        = 'Barley Hulls',
                        ppg         = 0,
                        lovibond    = 0,
                        type        = 'ADJUNCT',
                        description = 'Aid in lautering.',
                        origin      = 'US'
                    )
                )
            ]
        )
        model.commit()

        recipe = model.Recipe.query.first()
        xml = recipe.to_xml()

        assert prepare_xml([
        '<FERMENTABLE>',
        '   <ADD_AFTER_BOIL>False</ADD_AFTER_BOIL>',
        '   <AMOUNT>0.45359237</AMOUNT>',
        '   <COLOR>0.0</COLOR>',
        '   <NAME>Barley Hulls</NAME>',
        '   <NOTES>Aid in lautering.</NOTES>',
        '   <ORIGIN>US</ORIGIN>',
        '   <TYPE>Adjunct</TYPE>',
        '   <VERSION>1</VERSION>',
        '   <YIELD>0.0</YIELD>',
        '</FERMENTABLE>'
        ]) in xml

    def test_fermentation_addition(self):
        model.Recipe(
            type            = 'MASH',
            name            = 'Rocky Mountain River IPA',
            author          = model.User(
                first_name  = u'Ryan',
                last_name   = u'Petrello'
            ),
            gallons         = 5,
            boil_minutes    = 60,
            notes           = u'This is my favorite recipe.',
            additions       = [
                model.RecipeAddition(
                    use         = 'PRIMARY',
                    amount      = 1,
                    unit        = 'POUND',
                    duration    = timedelta(seconds = 3600),
                    fermentable = model.Fermentable(
                        name        = 'Sucrose',
                        ppg         = 46,
                        lovibond    = 1,
                        type        = 'SUGAR',
                        description = 'Table Sugar',
                        origin      = 'US'
                    )
                )
            ]
        )
        model.commit()

        recipe = model.Recipe.query.first()
        xml = recipe.to_xml()

        assert prepare_xml([
        '<FERMENTABLE>',
        '   <ADD_AFTER_BOIL>True</ADD_AFTER_BOIL>',
        '   <AMOUNT>0.45359237</AMOUNT>',
        '   <COLOR>1.0</COLOR>',
        '   <NAME>Sucrose</NAME>',
        '   <NOTES>Table Sugar</NOTES>',
        '   <ORIGIN>US</ORIGIN>',
        '   <TYPE>Sugar</TYPE>',
        '   <VERSION>1</VERSION>',
        '   <YIELD>100.0</YIELD>',
        '</FERMENTABLE>'
        ]) in xml

class TestRecipeWithYeast(TestModel):

    def test_ale_yeast(self):
        model.Recipe(
            type            = 'MASH',
            name            = 'Rocky Mountain River IPA',
            author          = model.User(
                first_name  = u'Ryan',
                last_name   = u'Petrello'
            ),
            gallons         = 5,
            boil_minutes    = 60,
            notes           = u'This is my favorite recipe.',
            additions       = [
                model.RecipeAddition(
                    use     = 'PRIMARY',
                    yeast   = model.Yeast(
                        name        = 'Wyeast 1056 - American Ale',
                        type        = 'ALE',
                        form        = 'LIQUID',
                        attenuation = 0.75,
                        description = 'A yeast for American Ales.',
                        origin      = 'US'
                    )
                )
            ]
        )
        model.commit()

        recipe = model.Recipe.query.first()
        xml = recipe.to_xml()

        assert prepare_xml([
        '<YEAST>',
        '   <AMOUNT>0.125</AMOUNT>',
        '   <ATTENUATION>75.0</ATTENUATION>',
        '   <FORM>Liquid</FORM>',
        '   <NAME>Wyeast 1056 - American Ale</NAME>',
        '   <NOTES>A yeast for American Ales.</NOTES>',
        '   <TYPE>Ale</TYPE>',
        '   <VERSION>1</VERSION>',
        '</YEAST>'
        ]) in xml
    
    def test_wild_yeast(self):
        model.Recipe(
            type            = 'MASH',
            name            = 'Rocky Mountain River IPA',
            author          = model.User(
                first_name  = u'Ryan',
                last_name   = u'Petrello'
            ),
            gallons         = 5,
            boil_minutes    = 60,
            notes           = u'This is my favorite recipe.',
            additions       = [
                model.RecipeAddition(
                    use     = 'PRIMARY',
                    yeast   = model.Yeast(
                        name        = 'Wyeast 5112 - Brettanomyces Bruxellensis',
                        type        = 'WILD',
                        form        = 'LIQUID',
                        attenuation = 0.75,
                        description = 'A yeast for wild ales.',
                        origin      = 'US'
                    )
                )
            ]
        )
        model.commit()

        recipe = model.Recipe.query.first()
        xml = recipe.to_xml()

        assert prepare_xml([
        '<YEAST>',
        '   <AMOUNT>0.125</AMOUNT>',
        '   <ATTENUATION>75.0</ATTENUATION>',
        '   <FORM>Liquid</FORM>',
        '   <NAME>Wyeast 5112 - Brettanomyces Bruxellensis</NAME>',
        '   <NOTES>A yeast for wild ales.</NOTES>',
        '   <TYPE>Ale</TYPE>',
        '   <VERSION>1</VERSION>',
        '</YEAST>'
        ]) in xml

    def test_lager_yeast(self):
        model.Recipe(
            type            = 'MASH',
            name            = 'Rocky Mountain River IPA',
            author          = model.User(
                first_name  = u'Ryan',
                last_name   = u'Petrello'
            ),
            gallons         = 5,
            boil_minutes    = 60,
            notes           = u'This is my favorite recipe.',
            additions       = [
                model.RecipeAddition(
                    use     = 'PRIMARY',
                    yeast   = model.Yeast(
                        name        = 'Wyeast 2035 - American Lager',
                        type        = 'LAGER',
                        form        = 'LIQUID',
                        attenuation = 0.75,
                        description = 'A yeast for American Lagers.',
                        origin      = 'US'
                    )
                )
            ]
        )
        model.commit()

        recipe = model.Recipe.query.first()
        xml = recipe.to_xml()

        assert prepare_xml([
        '<YEAST>',
        '   <AMOUNT>0.125</AMOUNT>',
        '   <ATTENUATION>75.0</ATTENUATION>',
        '   <FORM>Liquid</FORM>',
        '   <NAME>Wyeast 2035 - American Lager</NAME>',
        '   <NOTES>A yeast for American Lagers.</NOTES>',
        '   <TYPE>Lager</TYPE>',
        '   <VERSION>1</VERSION>',
        '</YEAST>'
        ]) in xml

    def test_mead_yeast(self):
        model.Recipe(
            type            = 'MASH',
            name            = 'Rocky Mountain River IPA',
            author          = model.User(
                first_name  = u'Ryan',
                last_name   = u'Petrello'
            ),
            gallons         = 5,
            boil_minutes    = 60,
            notes           = u'This is my favorite recipe.',
            additions       = [
                model.RecipeAddition(
                    use     = 'PRIMARY',
                    yeast   = model.Yeast(
                        name        = 'Wyeast 4184 - Sweet Mead',
                        type        = 'MEAD',
                        form        = 'LIQUID',
                        attenuation = 0.75,
                        description = 'A yeast for meads.',
                        origin      = 'US'
                    )
                )
            ]
        )
        model.commit()

        recipe = model.Recipe.query.first()
        xml = recipe.to_xml()

        assert prepare_xml([
        '<YEAST>',
        '   <AMOUNT>0.125</AMOUNT>',
        '   <ATTENUATION>75.0</ATTENUATION>',
        '   <FORM>Liquid</FORM>',
        '   <NAME>Wyeast 4184 - Sweet Mead</NAME>',
        '   <NOTES>A yeast for meads.</NOTES>',
        '   <TYPE>Wine</TYPE>',
        '   <VERSION>1</VERSION>',
        '</YEAST>'
        ]) in xml

    def test_cider_yeast(self):
        model.Recipe(
            type            = 'MASH',
            name            = 'Rocky Mountain River IPA',
            author          = model.User(
                first_name  = u'Ryan',
                last_name   = u'Petrello'
            ),
            gallons         = 5,
            boil_minutes    = 60,
            notes           = u'This is my favorite recipe.',
            additions       = [
                model.RecipeAddition(
                    use     = 'PRIMARY',
                    yeast   = model.Yeast(
                        name        = 'Wyeast 4766 - Cider',
                        type        = 'CIDER',
                        form        = 'LIQUID',
                        attenuation = 0.75,
                        description = 'A yeast for ciders.',
                        origin      = 'US'
                    )
                )
            ]
        )
        model.commit()

        recipe = model.Recipe.query.first()
        xml = recipe.to_xml()

        assert prepare_xml([
        '<YEAST>',
        '   <AMOUNT>0.125</AMOUNT>',
        '   <ATTENUATION>75.0</ATTENUATION>',
        '   <FORM>Liquid</FORM>',
        '   <NAME>Wyeast 4766 - Cider</NAME>',
        '   <NOTES>A yeast for ciders.</NOTES>',
        '   <TYPE>Wine</TYPE>',
        '   <VERSION>1</VERSION>',
        '</YEAST>'
        ]) in xml

    def test_wine_yeast(self):
        model.Recipe(
            type            = 'MASH',
            name            = 'Rocky Mountain River IPA',
            author          = model.User(
                first_name  = u'Ryan',
                last_name   = u'Petrello'
            ),
            gallons         = 5,
            boil_minutes    = 60,
            notes           = u'This is my favorite recipe.',
            additions       = [
                model.RecipeAddition(
                    use     = 'PRIMARY',
                    yeast   = model.Yeast(
                        name        = 'White Labs WLP715 - Champagne Yeast',
                        type        = 'WINE',
                        form        = 'LIQUID',
                        attenuation = 0.75,
                        description = 'A yeast for wine.',
                        origin      = 'US'
                    )
                )
            ]
        )
        model.commit()

        recipe = model.Recipe.query.first()
        xml = recipe.to_xml()

        assert prepare_xml([
        '<YEAST>',
        '   <AMOUNT>0.125</AMOUNT>',
        '   <ATTENUATION>75.0</ATTENUATION>',
        '   <FORM>Liquid</FORM>',
        '   <NAME>White Labs WLP715 - Champagne Yeast</NAME>',
        '   <NOTES>A yeast for wine.</NOTES>',
        '   <TYPE>Wine</TYPE>',
        '   <VERSION>1</VERSION>',
        '</YEAST>'
        ]) in xml

    def test_dry_yeast(self):
        model.Recipe(
            type            = 'MASH',
            name            = 'Rocky Mountain River IPA',
            author          = model.User(
                first_name  = u'Ryan',
                last_name   = u'Petrello'
            ),
            gallons         = 5,
            boil_minutes    = 60,
            notes           = u'This is my favorite recipe.',
            additions       = [
                model.RecipeAddition(
                    use     = 'PRIMARY',
                    yeast   = model.Yeast(
                        name        = 'DCL S-04 - SafAle English Ale',
                        type        = 'ALE',
                        form        = 'DRY',
                        attenuation = 0.75,
                        description = 'A dry yeast.',
                        origin      = 'US'
                    )
                )
            ]
        )
        model.commit()

        recipe = model.Recipe.query.first()
        xml = recipe.to_xml()

        assert prepare_xml([
        '<YEAST>',
        '   <AMOUNT>0.0115</AMOUNT>',
        '   <AMOUNT_IS_WEIGHT>True</AMOUNT_IS_WEIGHT>',
        '   <ATTENUATION>75.0</ATTENUATION>',
        '   <FORM>Dry</FORM>',
        '   <NAME>DCL S-04 - SafAle English Ale</NAME>',
        '   <NOTES>A dry yeast.</NOTES>',
        '   <TYPE>Ale</TYPE>',
        '   <VERSION>1</VERSION>',
        '</YEAST>'
        ]) in xml

    def test_yeast_in_secondary(self):
        model.Recipe(
            type            = 'MASH',
            name            = 'Rocky Mountain River IPA',
            author          = model.User(
                first_name  = u'Ryan',
                last_name   = u'Petrello'
            ),
            gallons         = 5,
            boil_minutes    = 60,
            notes           = u'This is my favorite recipe.',
            additions       = [
                model.RecipeAddition(
                    use     = 'SECONDARY',
                    yeast   = model.Yeast(
                        name        = 'Wyeast 1056 - American Ale',
                        type        = 'ALE',
                        form        = 'LIQUID',
                        attenuation = 0.75,
                        description = 'A yeast for American Ales.',
                        origin      = 'US'
                    )
                )
            ]
        )
        model.commit()

        recipe = model.Recipe.query.first()
        xml = recipe.to_xml()

        assert prepare_xml([
        '<YEAST>',
        '   <ADD_TO_SECONDARY>True</ADD_TO_SECONDARY>',
        '   <AMOUNT>0.125</AMOUNT>',
        '   <ATTENUATION>75.0</ATTENUATION>',
        '   <FORM>Liquid</FORM>',
        '   <NAME>Wyeast 1056 - American Ale</NAME>',
        '   <NOTES>A yeast for American Ales.</NOTES>',
        '   <TYPE>Ale</TYPE>',
        '   <VERSION>1</VERSION>',
        '</YEAST>'
        ]) in xml

    def test_yeast_in_tertiary(self):
        model.Recipe(
            type            = 'MASH',
            name            = 'Rocky Mountain River IPA',
            author          = model.User(
                first_name  = u'Ryan',
                last_name   = u'Petrello'
            ),
            gallons         = 5,
            boil_minutes    = 60,
            notes           = u'This is my favorite recipe.',
            additions       = [
                model.RecipeAddition(
                    use     = 'TERTIARY',
                    yeast   = model.Yeast(
                        name        = 'Wyeast 1056 - American Ale',
                        type        = 'ALE',
                        form        = 'LIQUID',
                        attenuation = 0.75,
                        description = 'A yeast for American Ales.',
                        origin      = 'US'
                    )
                )
            ]
        )
        model.commit()

        recipe = model.Recipe.query.first()
        xml = recipe.to_xml()

        assert prepare_xml([
        '<YEAST>',
        '   <ADD_TO_SECONDARY>True</ADD_TO_SECONDARY>',
        '   <AMOUNT>0.125</AMOUNT>',
        '   <ATTENUATION>75.0</ATTENUATION>',
        '   <FORM>Liquid</FORM>',
        '   <NAME>Wyeast 1056 - American Ale</NAME>',
        '   <NOTES>A yeast for American Ales.</NOTES>',
        '   <TYPE>Ale</TYPE>',
        '   <VERSION>1</VERSION>',
        '</YEAST>'
        ]) in xml


class TestRecipeWithExtras(TestModel):

    def test_mash_extra(self):
        model.Recipe(
            type            = 'MASH',
            name            = 'Rocky Mountain River IPA',
            author          = model.User(
                first_name  = u'Ryan',
                last_name   = u'Petrello'
            ),
            gallons         = 5,
            boil_minutes    = 60,
            notes           = u'This is my favorite recipe.',
            additions       = [
                model.RecipeAddition(
                    use         = 'MASH',
                    amount      = 1,
                    unit        = 'OUNCE',
                    extra       = model.Extra(
                        name        = 'Irish Moss',
                        description = 'A fining agent.',
                        type        = 'FINING',
                        liquid      = False
                    )
                )
            ]
        )
        model.commit()

        recipe = model.Recipe.query.first()
        xml = recipe.to_xml()

        assert prepare_xml([
        '<MISC>',
        '   <AMOUNT>0.0283495231</AMOUNT>',
        '   <AMOUNT_IS_WEIGHT>True</AMOUNT_IS_WEIGHT>',
        '   <NAME>Irish Moss</NAME>',
        '   <NOTES>A fining agent.</NOTES>',
        '   <TIME>0</TIME>',
        '   <TYPE>Fining</TYPE>',
        '   <USE>Mash</USE>',
        '   <VERSION>1</VERSION>'
        '</MISC>'
        ]) in xml

    def test_boil_extra(self):
        model.Recipe(
            type            = 'MASH',
            name            = 'Rocky Mountain River IPA',
            author          = model.User(
                first_name  = u'Ryan',
                last_name   = u'Petrello'
            ),
            gallons         = 5,
            boil_minutes    = 60,
            notes           = u'This is my favorite recipe.',
            additions       = [
                model.RecipeAddition(
                    use         = 'BOIL',
                    amount      = 1,
                    unit        = 'OUNCE',
                    duration    = timedelta(minutes=15),
                    extra       = model.Extra(
                        name        = 'Irish Moss',
                        description = 'A fining agent.',
                        type        = 'FINING',
                        liquid      = False
                    )
                )
            ]
        )
        model.commit()

        recipe = model.Recipe.query.first()
        xml = recipe.to_xml()

        assert prepare_xml([
        '<MISC>',
        '   <AMOUNT>0.0283495231</AMOUNT>',
        '   <AMOUNT_IS_WEIGHT>True</AMOUNT_IS_WEIGHT>',
        '   <NAME>Irish Moss</NAME>',
        '   <NOTES>A fining agent.</NOTES>',
        '   <TIME>15</TIME>',
        '   <TYPE>Fining</TYPE>',
        '   <USE>Boil</USE>',
        '   <VERSION>1</VERSION>'
        '</MISC>'
        ]) in xml

    def test_primary_extra(self):
        model.Recipe(
            type            = 'MASH',
            name            = 'Rocky Mountain River IPA',
            author          = model.User(
                first_name  = u'Ryan',
                last_name   = u'Petrello'
            ),
            gallons         = 5,
            boil_minutes    = 60,
            notes           = u'This is my favorite recipe.',
            additions       = [
                model.RecipeAddition(
                    use         = 'PRIMARY',
                    amount      = 1,
                    unit        = 'OUNCE',
                    extra       = model.Extra(
                        name        = 'Irish Moss',
                        description = 'A fining agent.',
                        type        = 'FINING',
                        liquid      = False
                    )
                )
            ]
        )
        model.commit()

        recipe = model.Recipe.query.first()
        xml = recipe.to_xml()

        assert prepare_xml([
        '<MISC>',
        '   <AMOUNT>0.0283495231</AMOUNT>',
        '   <AMOUNT_IS_WEIGHT>True</AMOUNT_IS_WEIGHT>',
        '   <NAME>Irish Moss</NAME>',
        '   <NOTES>A fining agent.</NOTES>',
        '   <TIME>0</TIME>',
        '   <TYPE>Fining</TYPE>',
        '   <USE>Primary</USE>',
        '   <VERSION>1</VERSION>'
        '</MISC>'
        ]) in xml

    def test_secondary_extra(self):
        model.Recipe(
            type            = 'MASH',
            name            = 'Rocky Mountain River IPA',
            author          = model.User(
                first_name  = u'Ryan',
                last_name   = u'Petrello'
            ),
            gallons         = 5,
            boil_minutes    = 60,
            notes           = u'This is my favorite recipe.',
            additions       = [
                model.RecipeAddition(
                    use         = 'SECONDARY',
                    amount      = 1,
                    unit        = 'OUNCE',
                    extra       = model.Extra(
                        name        = 'Irish Moss',
                        description = 'A fining agent.',
                        type        = 'FINING',
                        liquid      = False
                    )
                )
            ]
        )
        model.commit()

        recipe = model.Recipe.query.first()
        xml = recipe.to_xml()

        assert prepare_xml([
        '<MISC>',
        '   <AMOUNT>0.0283495231</AMOUNT>',
        '   <AMOUNT_IS_WEIGHT>True</AMOUNT_IS_WEIGHT>',
        '   <NAME>Irish Moss</NAME>',
        '   <NOTES>A fining agent.</NOTES>',
        '   <TIME>0</TIME>',
        '   <TYPE>Fining</TYPE>',
        '   <USE>Secondary</USE>',
        '   <VERSION>1</VERSION>'
        '</MISC>'
        ]) in xml

    def test_tertiary_extra(self):
        model.Recipe(
            type            = 'MASH',
            name            = 'Rocky Mountain River IPA',
            author          = model.User(
                first_name  = u'Ryan',
                last_name   = u'Petrello'
            ),
            gallons         = 5,
            boil_minutes    = 60,
            notes           = u'This is my favorite recipe.',
            additions       = [
                model.RecipeAddition(
                    use         = 'TERTIARY',
                    amount      = 1,
                    unit        = 'OUNCE',
                    extra       = model.Extra(
                        name        = 'Irish Moss',
                        description = 'A fining agent.',
                        type        = 'FINING',
                        liquid      = False
                    )
                )
            ]
        )
        model.commit()

        recipe = model.Recipe.query.first()
        xml = recipe.to_xml()

        assert prepare_xml([
        '<MISC>',
        '   <AMOUNT>0.0283495231</AMOUNT>',
        '   <AMOUNT_IS_WEIGHT>True</AMOUNT_IS_WEIGHT>',
        '   <NAME>Irish Moss</NAME>',
        '   <NOTES>A fining agent.</NOTES>',
        '   <TIME>0</TIME>',
        '   <TYPE>Fining</TYPE>',
        '   <USE>Secondary</USE>',
        '   <VERSION>1</VERSION>'
        '</MISC>'
        ]) in xml

    def test_liquid_extra(self):
        model.Recipe(
            type            = 'MASH',
            name            = 'Rocky Mountain River IPA',
            author          = model.User(
                first_name  = u'Ryan',
                last_name   = u'Petrello'
            ),
            gallons         = 5,
            boil_minutes    = 60,
            notes           = u'This is my favorite recipe.',
            additions       = [
                model.RecipeAddition(
                    use         = 'PRIMARY',
                    amount      = 1,
                    unit        = 'OUNCE',
                    extra       = model.Extra(
                        name        = 'Strawberry Flavoring',
                        description = 'Tastes like strawberries.',
                        type        = 'FLAVOR',
                        liquid      = True
                    )
                )
            ]
        )
        model.commit()

        recipe = model.Recipe.query.first()
        xml = recipe.to_xml()

        assert prepare_xml([
        '<MISC>',
        '   <AMOUNT>0.0295735296</AMOUNT>',
        '   <NAME>Strawberry Flavoring</NAME>',
        '   <NOTES>Tastes like strawberries.</NOTES>',
        '   <TIME>0</TIME>',
        '   <TYPE>Flavor</TYPE>',
        '   <USE>Primary</USE>',
        '   <VERSION>1</VERSION>'
        '</MISC>'
        ]) in xml

    def test_no_unit_extra(self):
        model.Recipe(
            type            = 'MASH',
            name            = 'Rocky Mountain River IPA',
            author          = model.User(
                first_name  = u'Ryan',
                last_name   = u'Petrello'
            ),
            gallons         = 5,
            boil_minutes    = 60,
            notes           = u'This is my favorite recipe.',
            additions       = [
                model.RecipeAddition(
                    use         = 'PRIMARY',
                    amount      = 1,
                    extra       = model.Extra(
                        name        = 'Whirlfloc Tablet',
                        description = 'A fining agent.',
                        type        = 'FINING'
                    )
                )
            ]
        )
        model.commit()

        recipe = model.Recipe.query.first()
        xml = recipe.to_xml()

        assert prepare_xml([
        '<MISC>',
        '   <AMOUNT>0.015</AMOUNT>',
        '   <AMOUNT_IS_WEIGHT>True</AMOUNT_IS_WEIGHT>',
        '   <NAME>Whirlfloc Tablet</NAME>',
        '   <NOTES>A fining agent.</NOTES>',
        '   <TIME>0</TIME>',
        '   <TYPE>Fining</TYPE>',
        '   <USE>Primary</USE>',
        '   <VERSION>1</VERSION>'
        '</MISC>'
        ]) in xml
