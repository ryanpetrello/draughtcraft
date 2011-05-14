from formencode                 import ForEach, Invalid, validators
from beerparts                  import model
from beerparts.lib.schemas.base import FilteredSchema, ModelObject
from datetime                   import timedelta


class TimeDeltaValidator(validators.FancyValidator):

    def _to_python(self, value, state):
        if not value: return None
        try:
            return timedelta(minutes=value)
        except Exception, e:
            raise Invalid(e, value, state)

    def _from_python(self, value, state):
        if value:
            return value.seconds / 60


class BaseRecipeAddition(FilteredSchema):
    type        = validators.OneOf(['RecipeAddition', 'HopAddition'])
    use         = validators.OneOf(model.RecipeAddition.USES)
    duration    = TimeDeltaValidator(if_missing=None) # Timedelta in Minutes

    # Hop-specific
    form        = validators.OneOf(model.HopAddition.FORMS, if_missing=None)
    alpha_acid  = validators.Number(if_missing=None)

class RecipeAddition(BaseRecipeAddition):
    ingredient  = ModelObject(model.Ingredient)

class RecipeAdditionChange(BaseRecipeAddition):
    addition    = ModelObject(model.RecipeAddition)

class RecipeChange(FilteredSchema):
    additions   = ForEach(RecipeAdditionChange)
