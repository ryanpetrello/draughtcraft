from draughtcraft.tests     import TestApp
from draughtcraft           import model
from datetime               import datetime, timedelta
from urllib                 import urlencode

def R(kwargs):
    recipe = model.Recipe(**kwargs)
    if 'author' not in kwargs:
        recipe.author = model.User.query.first() or model.User(email = 'ryan@example.com')
    return recipe


class TestRecipeBrowser(TestApp):
    """
    Abstract class with helpers for testing /recipes/recipes
    """

    _default = {
        'page'      : '1',
        'order_by'  : 'last_updated',
        'direction' : 'DESC',
        'style'     : '',
        'color'     : '',
        'mash'      : 'on',
        'minimash'  : 'on',
        'extract'   : 'on'
    }

    def _get(self, args={}, **kwargs):
        default = self._default.copy()
        default.update(args)
        url = '/recipes/recipes?%s' % urlencode(default)

        self._ns = self.get(url, **kwargs)
        if self._ns.status_int == 200:
            self._ns = self._ns.namespace
        return self._ns

    def _eq(self, key, value):
        assert self._ns[key] == value


class TestRecipeBrowse(TestRecipeBrowser):

    def test_browse_index(self):
        model.Style(name = 'American IPA')
        model.commit()

        response = self.get('/recipes/')
        assert response.status_int == 200
        assert len(response.namespace.get('styles')) == 1

    def test_browse_ajax(self):
        response = self.get('/recipes/recipes', status=200)
        assert response.status_int == 200


class TestRecipeBase(TestRecipeBrowser):
    """
    Make sure non-published recipes are filtered out.
    """

    def test_filter_drafts(self):
        R({'name': 'Simple Recipe'})
        model.commit()

        assert model.Recipe.query.first().state != 'PUBLISHED'

        self._get()
        self._eq('pages', 1)
        self._eq('current_page', 1)
        self._eq('offset', 0)
        self._eq('perpage', 15)
        self._eq('total', 0)
        self._eq('order_by', 'last_updated')
        self._eq('direction', 'DESC')
        self._eq('recipes', [])


class TestPaging(TestRecipeBrowser):
    """
    Make sure recipe pagination works properly.
    """

    def test_zero_results(self):
        self._get()
        self._eq('pages', 1)
        self._eq('current_page', 1)
        self._eq('offset', 0)
        self._eq('perpage', 15)
        self._eq('total', 0)
        self._eq('order_by', 'last_updated')
        self._eq('direction', 'DESC')
        self._eq('recipes', [])

    def test_single_page(self):
        R({'name': 'Simple Recipe', 'state': 'PUBLISHED'})
        model.commit()

        self._get()
        self._eq('pages', 1)
        self._eq('current_page', 1)
        self._eq('offset', 0)
        self._eq('perpage', 15)
        self._eq('total', 1)
        self._eq('order_by', 'last_updated')
        self._eq('direction', 'DESC')
        assert self._ns['recipes'][0].id == model.Recipe.query.first().id

    def test_multiple_pages(self):
        for i in range(31):
            R({'name': 'Simple Recipe', 'state': 'PUBLISHED'})
            model.commit()

        self._get()
        self._eq('pages', 3)
        self._eq('current_page', 1)
        self._eq('offset', 0)
        self._eq('perpage', 15)
        self._eq('total', 31)
        self._eq('order_by', 'last_updated')
        self._eq('direction', 'DESC')
        assert len(self._ns['recipes']) == 15

        self._get({'page': '2'})
        self._eq('pages', 3)
        self._eq('current_page', 2)
        self._eq('offset', 15)
        self._eq('perpage', 15)
        self._eq('total', 31)
        self._eq('order_by', 'last_updated')
        self._eq('direction', 'DESC')
        assert len(self._ns['recipes']) == 15

        self._get({'page': '3'})
        self._eq('pages', 3)
        self._eq('current_page', 3)
        self._eq('offset', 30)
        self._eq('perpage', 15)
        self._eq('total', 31)
        self._eq('order_by', 'last_updated')
        self._eq('direction', 'DESC')
        assert len(self._ns['recipes']) == 1


class TestFiltering(TestRecipeBrowser):

    def test_filter_by_style(self):
        style = model.Style(name = 'American IPA')
        R({'name': 'Simple Recipe', 'state': 'PUBLISHED', 'style': style})
        model.commit()

        self._get()
        self._eq('pages', 1)
        self._eq('current_page', 1)
        self._eq('offset', 0)
        self._eq('perpage', 15)
        self._eq('total', 1)
        self._eq('order_by', 'last_updated')
        self._eq('direction', 'DESC')
        assert self._ns['recipes'][0].id == model.Recipe.query.first().id

        self._get({'style': '1'})
        self._eq('pages', 1)
        self._eq('current_page', 1)
        self._eq('offset', 0)
        self._eq('perpage', 15)
        self._eq('total', 1)
        self._eq('order_by', 'last_updated')
        self._eq('direction', 'DESC')
        assert self._ns['recipes'][0].id == model.Recipe.query.first().id

        model.Style(name = 'American Stout')
        model.commit()

        self._get({'style': '2'})
        self._eq('pages', 1)
        self._eq('current_page', 1)
        self._eq('offset', 0)
        self._eq('perpage', 15)
        self._eq('total', 0)
        self._eq('order_by', 'last_updated')
        self._eq('direction', 'DESC')
        assert len(self._ns['recipes']) == 0

    def test_filter_by_srm(self):
        R({'name': 'Light', 'state': 'PUBLISHED', '_srm': 6})
        R({'name': 'Light/Amber', 'state': 'PUBLISHED', '_srm': 8})
        R({'name': 'Amber', 'state': 'PUBLISHED', '_srm': 12})
        R({'name': 'Amber/Brown', 'state': 'PUBLISHED', '_srm': 16})
        R({'name': 'Brown', 'state': 'PUBLISHED', '_srm': 20})
        R({'name': 'Brown/Dark', 'state': 'PUBLISHED', '_srm': 25})
        R({'name': 'Dark', 'state': 'PUBLISHED', '_srm': 30})
        model.commit()

        self._get()
        self._eq('pages', 1)
        self._eq('current_page', 1)
        self._eq('offset', 0)
        self._eq('perpage', 15)
        self._eq('total', 7)
        self._eq('order_by', 'last_updated')
        self._eq('direction', 'DESC')
        assert len(self._ns['recipes']) == 7

        self._get({'color': 'light'})
        self._eq('pages', 1)
        self._eq('current_page', 1)
        self._eq('offset', 0)
        self._eq('perpage', 15)
        self._eq('total', 2)
        self._eq('order_by', 'last_updated')
        self._eq('direction', 'DESC')
        assert len(self._ns['recipes']) == 2

        self._get({'color': 'amber'})
        self._eq('pages', 1)
        self._eq('current_page', 1)
        self._eq('offset', 0)
        self._eq('perpage', 15)
        self._eq('total', 3)
        self._eq('order_by', 'last_updated')
        self._eq('direction', 'DESC')
        assert len(self._ns['recipes']) == 3

        self._get({'color': 'brown'})
        self._eq('pages', 1)
        self._eq('current_page', 1)
        self._eq('offset', 0)
        self._eq('perpage', 15)
        self._eq('total', 3)
        self._eq('order_by', 'last_updated')
        self._eq('direction', 'DESC')
        assert len(self._ns['recipes']) == 3

        self._get({'color': 'dark'})
        self._eq('pages', 1)
        self._eq('current_page', 1)
        self._eq('offset', 0)
        self._eq('perpage', 15)
        self._eq('total', 2)
        self._eq('order_by', 'last_updated')
        self._eq('direction', 'DESC')
        assert len(self._ns['recipes']) == 2


class TestFilteringByType(TestRecipeBrowser):

    _default = {
        'page'      : '1',
        'order_by'  : 'last_updated',
        'direction' : 'DESC',
        'style'     : '',
        'color'     : ''
    }

    def test_filter_by_type(self):
        R({'name': 'MASH', 'state': 'PUBLISHED', 'type': 'MASH'})
        R({'name': 'MINIMASH', 'state': 'PUBLISHED', 'type': 'MINIMASH'})
        R({'name': 'EXTRACTSTEEP', 'state': 'PUBLISHED', 'type': 'EXTRACTSTEEP'})
        R({'name': 'EXTRACT', 'state': 'PUBLISHED', 'type': 'EXTRACT'})
        model.commit()

        self._get({'mash': 'on', 'minimash': 'on', 'extract': 'on'})
        self._eq('pages', 1)
        self._eq('current_page', 1)
        self._eq('offset', 0)
        self._eq('perpage', 15)
        self._eq('total', 4)
        self._eq('order_by', 'last_updated')
        self._eq('direction', 'DESC')
        assert len(self._ns['recipes']) == 4

        # Mash Only
        self._get({'mash': 'on'})
        self._eq('pages', 1)
        self._eq('current_page', 1)
        self._eq('offset', 0)
        self._eq('perpage', 15)
        self._eq('total', 1)
        self._eq('order_by', 'last_updated')
        self._eq('direction', 'DESC')
        assert len(self._ns['recipes']) == 1
        assert self._ns['recipes'][0].id == model.Recipe.get_by(name='MASH').id

        # Mini-Mash Only
        self._get({'minimash': 'on'})
        self._eq('pages', 1)
        self._eq('current_page', 1)
        self._eq('offset', 0)
        self._eq('perpage', 15)
        self._eq('total', 1)
        self._eq('order_by', 'last_updated')
        self._eq('direction', 'DESC')
        assert len(self._ns['recipes']) == 1
        assert self._ns['recipes'][0].id == model.Recipe.get_by(name='MINIMASH').id

        # Extracts
        self._get({'extract': 'on'})
        self._eq('pages', 1)
        self._eq('current_page', 1)
        self._eq('offset', 0)
        self._eq('perpage', 15)
        self._eq('total', 2)
        self._eq('order_by', 'last_updated')
        self._eq('direction', 'DESC')
        assert len(self._ns['recipes']) == 2
        identifiers = [r.id for r in self._ns['recipes']]
        for recipe in model.Recipe.query.filter(model.Recipe.type.like('EXTRACT%')).all():
            assert recipe.id in identifiers

        # All three types disabled
        self._get({})
        self._eq('pages', 1)
        self._eq('current_page', 1)
        self._eq('offset', 0)
        self._eq('perpage', 15)
        self._eq('total', 0)
        self._eq('order_by', 'last_updated')
        self._eq('direction', 'DESC')
        assert len(self._ns['recipes']) == 0


class TestSorting(TestRecipeBrowser):

    def test_sort_by_type(self):
        R({'name': 'Recipe 1', 'state': 'PUBLISHED', 'type': 'MASH'})
        R({'name': 'Recipe 2', 'state': 'PUBLISHED', 'type': 'MINIMASH'})
        R({'name': 'Recipe 3', 'state': 'PUBLISHED', 'type': 'EXTRACT'})
        R({'name': 'Recipe 4', 'state': 'PUBLISHED', 'type': 'EXTRACTSTEEP'})
        model.commit()

        #
        # Sort alphabetically (DESC) based on:
        #   'MASH'          : 'All Grain',
        #   'EXTRACT'       : 'Extract',
        #   'EXTRACTSTEEP'  : 'Extract w/ Steeped Grains',
        #   'MINIMASH'      : 'Mini-Mash'
        # 
        self._get({'order_by': 'type'})
        self._eq('pages', 1)
        self._eq('current_page', 1)
        self._eq('offset', 0)
        self._eq('perpage', 15)
        self._eq('total', 4)
        self._eq('order_by', 'type')
        self._eq('direction', 'DESC')
        assert len(self._ns['recipes']) == 4
        assert self._ns['recipes'][0].name == 'Recipe 2'
        assert self._ns['recipes'][1].name == 'Recipe 4'
        assert self._ns['recipes'][2].name == 'Recipe 3'
        assert self._ns['recipes'][3].name == 'Recipe 1'

        #
        # Sort alphabetically (ASC) based on:
        #   'MASH'          : 'All Grain',
        #   'EXTRACT'       : 'Extract',
        #   'EXTRACTSTEEP'  : 'Extract w/ Steeped Grains',
        #   'MINIMASH'      : 'Mini-Mash'
        # 
        self._get({'order_by': 'type', 'direction': 'ASC'})
        self._eq('pages', 1)
        self._eq('current_page', 1)
        self._eq('offset', 0)
        self._eq('perpage', 15)
        self._eq('total', 4)
        self._eq('order_by', 'type')
        self._eq('direction', 'ASC')
        assert len(self._ns['recipes']) == 4
        assert self._ns['recipes'][0].name == 'Recipe 1'
        assert self._ns['recipes'][1].name == 'Recipe 3'
        assert self._ns['recipes'][2].name == 'Recipe 4'
        assert self._ns['recipes'][3].name == 'Recipe 2'

    def test_sort_by_srm(self):
        R({'name': 'Recipe 1', 'state': 'PUBLISHED', '_srm': 5})
        R({'name': 'Recipe 2', 'state': 'PUBLISHED', '_srm': 15})
        R({'name': 'Recipe 3', 'state': 'PUBLISHED', '_srm': 10})
        R({'name': 'Recipe 4', 'state': 'PUBLISHED', '_srm': 25})
        model.commit()

        self._get({'order_by': 'srm'})
        self._eq('pages', 1)
        self._eq('current_page', 1)
        self._eq('offset', 0)
        self._eq('perpage', 15)
        self._eq('total', 4)
        self._eq('order_by', 'srm')
        self._eq('direction', 'DESC')
        assert len(self._ns['recipes']) == 4
        assert self._ns['recipes'][0].name == 'Recipe 4'
        assert self._ns['recipes'][1].name == 'Recipe 2'
        assert self._ns['recipes'][2].name == 'Recipe 3'
        assert self._ns['recipes'][3].name == 'Recipe 1'

        self._get({'order_by': 'srm', 'direction': 'ASC'})
        self._eq('pages', 1)
        self._eq('current_page', 1)
        self._eq('offset', 0)
        self._eq('perpage', 15)
        self._eq('total', 4)
        self._eq('order_by', 'srm')
        self._eq('direction', 'ASC')
        assert len(self._ns['recipes']) == 4
        assert self._ns['recipes'][0].name == 'Recipe 1'
        assert self._ns['recipes'][1].name == 'Recipe 3'
        assert self._ns['recipes'][2].name == 'Recipe 2'
        assert self._ns['recipes'][3].name == 'Recipe 4'

    def test_sort_by_name(self):
        R({'name': 'Recipe 1', 'state': 'PUBLISHED'})
        R({'name': 'Recipe 3', 'state': 'PUBLISHED'})
        R({'name': 'Recipe 2', 'state': 'PUBLISHED'})
        R({'name': 'Recipe 4', 'state': 'PUBLISHED'})
        model.commit()

        self._get({'order_by': 'name'})
        self._eq('pages', 1)
        self._eq('current_page', 1)
        self._eq('offset', 0)
        self._eq('perpage', 15)
        self._eq('total', 4)
        self._eq('order_by', 'name')
        self._eq('direction', 'DESC')
        assert len(self._ns['recipes']) == 4
        assert self._ns['recipes'][0].name == 'Recipe 4'
        assert self._ns['recipes'][1].name == 'Recipe 3'
        assert self._ns['recipes'][2].name == 'Recipe 2'
        assert self._ns['recipes'][3].name == 'Recipe 1'

        self._get({'order_by': 'name', 'direction': 'ASC'})
        self._eq('pages', 1)
        self._eq('current_page', 1)
        self._eq('offset', 0)
        self._eq('perpage', 15)
        self._eq('total', 4)
        self._eq('order_by', 'name')
        self._eq('direction', 'ASC')
        assert len(self._ns['recipes']) == 4
        assert self._ns['recipes'][0].name == 'Recipe 1'
        assert self._ns['recipes'][1].name == 'Recipe 2'
        assert self._ns['recipes'][2].name == 'Recipe 3'
        assert self._ns['recipes'][3].name == 'Recipe 4'

    def test_sort_by_author_name(self):
        R({
            'name': 'Recipe 1', 
            'state': 'PUBLISHED', 
            'author': model.User(
                username    = 'andy',
                email       = 'one@example.com'
            )
        })
        R({
            'name': 'Recipe 2', 
            'state': 'PUBLISHED', 
            'author': model.User(
                username    = 'tommy',
                email       = 'two@example.com'
            )
        })
        R({
            'name': 'Recipe 3', 
            'state': 'PUBLISHED', 
            'author': model.User(
                username    = 'zeek',
                email       = 'three@example.com'
            )
        })
        R({
            'name': 'Recipe 4', 
            'state': 'PUBLISHED', 
            'author': model.User(
                username    = 'phil',
                email       = 'four@example.com'
            )
        })
        R({
            'name': 'Recipe 5', 
            'state': 'PUBLISHED', 
            'author': model.User(
                username    = 'rob',
                email       = 'five@example.com'
            )
        })
        model.commit()

        self._get({'order_by': 'author'})
        self._eq('pages', 1)
        self._eq('current_page', 1)
        self._eq('offset', 0)
        self._eq('perpage', 15)
        self._eq('total', 5)
        self._eq('order_by', 'author')
        self._eq('direction', 'DESC')
        assert len(self._ns['recipes']) == 5
        assert self._ns['recipes'][0].name == 'Recipe 3'
        assert self._ns['recipes'][1].name == 'Recipe 2'
        assert self._ns['recipes'][2].name == 'Recipe 5'
        assert self._ns['recipes'][3].name == 'Recipe 4'
        assert self._ns['recipes'][4].name == 'Recipe 1'

        self._get({'order_by': 'author', 'direction': 'ASC'})
        self._eq('pages', 1)
        self._eq('current_page', 1)
        self._eq('offset', 0)
        self._eq('perpage', 15)
        self._eq('total', 5)
        self._eq('order_by', 'author')
        self._eq('direction', 'ASC')
        assert len(self._ns['recipes']) == 5
        assert self._ns['recipes'][0].name == 'Recipe 1'
        assert self._ns['recipes'][1].name == 'Recipe 4'
        assert self._ns['recipes'][2].name == 'Recipe 5'
        assert self._ns['recipes'][3].name == 'Recipe 2'
        assert self._ns['recipes'][4].name == 'Recipe 3'

    def test_sort_by_style(self):
        R({'name': 'Recipe 1', 'state': 'PUBLISHED', 'style': model.Style(name='Baltic Porter')})
        R({'name': 'Recipe 2', 'state': 'PUBLISHED', 'style': model.Style(name='American IPA')})
        R({'name': 'Recipe 3', 'state': 'PUBLISHED', 'style': model.Style(name='Schwarzbier')})
        R({'name': 'Recipe 4', 'state': 'PUBLISHED', 'style': model.Style(name='Belgian Golden Ale')})
        model.commit()

        self._get({'order_by': 'style'})
        self._eq('pages', 1)
        self._eq('current_page', 1)
        self._eq('offset', 0)
        self._eq('perpage', 15)
        self._eq('total', 4)
        self._eq('order_by', 'style')
        self._eq('direction', 'DESC')
        assert len(self._ns['recipes']) == 4
        assert self._ns['recipes'][0].name == 'Recipe 3'
        assert self._ns['recipes'][1].name == 'Recipe 4'
        assert self._ns['recipes'][2].name == 'Recipe 1'
        assert self._ns['recipes'][3].name == 'Recipe 2'

        self._get({'order_by': 'style', 'direction': 'ASC'})
        self._eq('pages', 1)
        self._eq('current_page', 1)
        self._eq('offset', 0)
        self._eq('perpage', 15)
        self._eq('total', 4)
        self._eq('order_by', 'style')
        self._eq('direction', 'ASC')
        assert len(self._ns['recipes']) == 4
        assert self._ns['recipes'][0].name == 'Recipe 2'
        assert self._ns['recipes'][1].name == 'Recipe 1'
        assert self._ns['recipes'][2].name == 'Recipe 4'
        assert self._ns['recipes'][3].name == 'Recipe 3'

    def test_sort_by_last_updated(self):

        def _days(days):
            return datetime.utcnow() + timedelta(days=days)

        R({'name': 'Recipe 1', 'state': 'PUBLISHED', 'last_updated': _days(2)})
        R({'name': 'Recipe 2', 'state': 'PUBLISHED', 'last_updated': _days(6)})
        R({'name': 'Recipe 3', 'state': 'PUBLISHED', 'last_updated': _days(1)})
        R({'name': 'Recipe 4', 'state': 'PUBLISHED', 'last_updated': _days(3)})
        model.commit()

        self._get({'order_by': 'last_updated'})
        self._eq('pages', 1)
        self._eq('current_page', 1)
        self._eq('offset', 0)
        self._eq('perpage', 15)
        self._eq('total', 4)
        self._eq('order_by', 'last_updated')
        self._eq('direction', 'DESC')
        assert len(self._ns['recipes']) == 4
        assert self._ns['recipes'][0].name == 'Recipe 2'
        assert self._ns['recipes'][1].name == 'Recipe 4'
        assert self._ns['recipes'][2].name == 'Recipe 1'
        assert self._ns['recipes'][3].name == 'Recipe 3'

        self._get({'order_by': 'last_updated', 'direction': 'ASC'})
        self._eq('pages', 1)
        self._eq('current_page', 1)
        self._eq('offset', 0)
        self._eq('perpage', 15)
        self._eq('total', 4)
        self._eq('order_by', 'last_updated')
        self._eq('direction', 'ASC')
        assert len(self._ns['recipes']) == 4
        assert self._ns['recipes'][0].name == 'Recipe 3'
        assert self._ns['recipes'][1].name == 'Recipe 1'
        assert self._ns['recipes'][2].name == 'Recipe 4'
        assert self._ns['recipes'][3].name == 'Recipe 2'

    def test_sort_by_views(self):
        r = R({'name': 'Recipe 1', 'state': 'PUBLISHED'})
        for i in range(10):
            model.RecipeView(recipe = r)

        r = R({'name': 'Recipe 2', 'state': 'PUBLISHED'})
        for i in range(15):
            model.RecipeView(recipe = r)

        r = R({'name': 'Recipe 3', 'state': 'PUBLISHED'})
        for i in range(3):
            model.RecipeView(recipe = r)

        r = R({'name': 'Recipe 4', 'state': 'PUBLISHED'})
        for i in range(12):
            model.RecipeView(recipe = r)

        model.commit()

        self._get({'order_by': 'views'})
        self._eq('pages', 1)
        self._eq('current_page', 1)
        self._eq('offset', 0)
        self._eq('perpage', 15)
        self._eq('total', 4)
        self._eq('order_by', 'views')
        self._eq('direction', 'DESC')
        assert len(self._ns['recipes']) == 4
        assert self._ns['recipes'][0].name == 'Recipe 2'
        assert self._ns['recipes'][1].name == 'Recipe 4'
        assert self._ns['recipes'][2].name == 'Recipe 1'
        assert self._ns['recipes'][3].name == 'Recipe 3'

        self._get({'order_by': 'views', 'direction': 'ASC'})
        self._eq('pages', 1)
        self._eq('current_page', 1)
        self._eq('offset', 0)
        self._eq('perpage', 15)
        self._eq('total', 4)
        self._eq('order_by', 'views')
        self._eq('direction', 'ASC')
        assert len(self._ns['recipes']) == 4
        assert self._ns['recipes'][0].name == 'Recipe 3'
        assert self._ns['recipes'][1].name == 'Recipe 1'
        assert self._ns['recipes'][2].name == 'Recipe 4'
        assert self._ns['recipes'][3].name == 'Recipe 2'
