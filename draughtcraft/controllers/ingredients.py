from pecan                  import expose, abort
from pecan.rest             import RestController
from draughtcraft           import model


class IngredientsController(RestController):

    @expose('ingredients/index.html')
    def get_one(self, ingredientID):
        ingredient = model.Ingredient.get(int(ingredientID))
        if ingredient is None:
            abort(404)
        return dict(ingredient=ingredient)
