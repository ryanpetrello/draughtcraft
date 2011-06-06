from formencode                     import validators
from draughtcraft                   import model
from draughtcraft.lib.schemas.base  import FilteredSchema 

class RecipeCreation(FilteredSchema):
    """
    This schema is for adding a new ingredient to
    a recipe.
    """
    name        = validators.String(not_empty=True) 
    type        = validators.OneOf(model.Recipe.TYPES)
    gallons     = validators.Number()
