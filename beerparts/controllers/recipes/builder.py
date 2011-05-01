from pecan      import expose

class RecipeBuilderController(object):

    @expose('recipes/builder/index.html')
    def index(self):
        return dict()

    @expose('recipes/builder/async.html')
    def async(self):
        return dict()
