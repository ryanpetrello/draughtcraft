from formencode                 import ForEach, Invalid, validators
from beerparts                  import model
from beerparts.lib.units        import UnitConvert
from beerparts.lib.schemas.base import FilteredSchema, ModelObject
from datetime                   import timedelta


class TimeDeltaValidator(validators.FancyValidator):
    """
    Used to convert integer minutes into a Python timedelta
    """

    def _to_python(self, value, state):
        if not value: return None
        try:
            return timedelta(minutes=value)
        except Exception, e:
            raise Invalid(e, value, state)

    def _from_python(self, value, state):
        if value:
            return value.seconds / 60


class AmountValidator(validators.FancyValidator):
    """
    Used to convert between strings and (amount, lib.units.UNITS), e.g.,

    "5lb, 8oz" <==> (5.5, "POUND")
    """

    def _to_python(self, value, state):
        if not value: return None
        try:
            return UnitConvert.from_str(value)
        except Exception, e:
            raise Invalid(e, value, state)

    def _from_python(self, value, state):
        if value:
            return UnitConvert.to_str(*value)


class BaseRecipeAddition(FilteredSchema):
    type        = validators.OneOf(['RecipeAddition', 'HopAddition'])
    use         = validators.OneOf(model.RecipeAddition.USES)
    amount      = AmountValidator(if_invalid=None)
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
