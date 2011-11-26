from draughtcraft                   import model
from draughtcraft.lib.beerxml       import export
from draughtcraft.tests             import TestModel
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
