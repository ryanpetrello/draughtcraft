from draughtcraft                   import model
from draughtcraft.lib.schemas.base  import FilteredSchema 
from formencode                     import validators


class UserRecipeSchema(FilteredSchema):
    """
    This schema is for validating recipe building settings.
    """
    default_recipe_type     = validators.OneOf(model.Recipe.TYPES)
    default_recipe_volume   = validators.Number()
    default_ibu_formula     = validators.OneOf(['tinseth', 'rager', 'daniels'])
    unit_system             = validators.OneOf(['US', 'METRIC'])
    brewhouse_efficiency    = validators.Number(min=50, max=100, not_empty=True)
