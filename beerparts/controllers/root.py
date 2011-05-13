from error      import ErrorController
from recipes    import RecipesController

class RootController(object):

    recipes = RecipesController()
    error   = ErrorController()
