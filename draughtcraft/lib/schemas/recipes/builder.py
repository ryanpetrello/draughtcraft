from formencode                     import ForEach, Invalid, validators
from draughtcraft                   import model
from draughtcraft.lib.units         import UnitConvert
from draughtcraft.lib.schemas.base  import FilteredSchema, ModelObject
from datetime                       import timedelta


class TimeDeltaValidator(validators.FancyValidator):
    """
    Used to convert integer `minutes` into a Python timedelta
    """

    def _to_python(self, value, state):
        if not value: return None
        try:
            return timedelta(minutes=int(value))
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


class HopValidator(validators.FormValidator):
    """
    Used to validate that hop additions
    specify both a `form` (e.g., LEAF, PLUG, PELLET)
    and an `alpha_acid` value.
    """
    
    validate_partial_form = True
    
    def validate_partial(self, field_dict, state):
        self.validate_python(field_dict, state)
    
    def validate_python(self, field_dict, state):
        
        # get the addition type, (e.g., RecipeAddition, HopAddition)
        addition_type = field_dict.get('type', '')
        
        # check the required fields for the type
        errors = {}
        if addition_type == 'HopAddition':
            if not field_dict.get('form'):
                errors['form'] = self.message('empty', state)
            if not field_dict.get('alpha_acid'):
                errors['alpha_acid'] = self.message('empty', state)
    
        # raise the errors, if any
        if errors:
            error_message = '\n'.join(['%s: %s' % (key, error) for key, error in errors.iteritems()])
            raise Invalid(error_message, field_dict, state, error_dict=errors)


class BaseRecipeAddition(FilteredSchema):
    """
    All recipe changes and additions must specify, at minimum:
        * A `type`, (e.g., 'RecipeAddition', 'HopAddition')
        * A `use` (e.g., 'MASH', 'BOIL')
        * A human-readable amount (e.g., '5lb, 8oz')
    """ 
    type        = validators.OneOf(['RecipeAddition', 'HopAddition'])
    use         = validators.OneOf(model.RecipeAddition.USES)
    amount      = AmountValidator(if_invalid=None)
    duration    = TimeDeltaValidator(if_missing=None) # Timedelta in Minutes

    # Hop-specific
    form        = validators.OneOf(model.HopAddition.FORMS, if_missing=None)
    alpha_acid  = validators.Number(min=0, if_missing=None)


class RecipeAddition(BaseRecipeAddition):
    """
    This schema is for adding a new ingredient to
    a recipe.
    """
    ingredient  = ModelObject(model.Ingredient)


class RecipeAdditionChange(BaseRecipeAddition):
    """
    This schema is for modifying an existing
    recipe addition.
    """
    addition            = ModelObject(model.RecipeAddition)
    chained_validators  = [HopValidator()]


class RecipeChange(FilteredSchema):
    additions   = ForEach(RecipeAdditionChange)
