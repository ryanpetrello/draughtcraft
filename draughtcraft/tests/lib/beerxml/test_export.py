from draughtcraft.lib.beerxml       import export
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


class TestRecipeComponents(TestCase):

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
