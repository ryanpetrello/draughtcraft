from formencode                 import Invalid, validators
from beerparts                  import model
from beerparts.lib.schemas.base import FilteredSchema, ModelObject
from beerparts.lib.units        import UNITS
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


class RecipeAdditionSchema(FilteredSchema):

    type        = validators.OneOf(['RecipeAddition', 'HopAddition'])
    ingredient  = ModelObject(model.Ingredient)
    amount      = validators.Number()
    unit        = validators.OneOf(UNITS)
    use         = validators.OneOf(model.RecipeAddition.USES)
    duration    = TimeDeltaValidator(if_missing=None) # Timedelta in Minutes

    # Hop-specific
    form        = validators.OneOf(model.HopAddition.FORMS, if_missing=None)
    alpha_acid  = validators.Number(if_missing=None)
