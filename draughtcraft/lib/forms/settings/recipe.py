from pecan.ext.wtforms import SecureForm, fields as f, validators as v


class UserRecipeForm(SecureForm):
    unit_system = f.SelectField('Display Recipes Using', choices=[
        ('US', 'U.S. units (lb, oz, gallon)'),
        ('METRIC', 'Metric units (kg, g, liter)')
    ])
    default_recipe_type = f.SelectField('Default Recipe Type', choices=[
        ('MASH', 'All Grain'),
        ('EXTRACT', 'Extract'),
        ('EXTRACTSTEEP', 'Extract w/ Steeped Grains'),
        ('MINIMASH', 'Extract with Mini-Mash')
    ])
    default_recipe_volume = f.FloatField('Default Batch Size', validators=[
        v.Required()
    ])
    default_ibu_formula = f.SelectField('Preferred IBU Calculation', choices=[
        ('tinseth', 'Tinseth Formula'),
        ('rager', 'Rager Formula'),
        ('daniels', 'Daniels Formula')
    ])
    brewhouse_efficiency = f.IntegerField(
        'Brewhouse Efficiency',
        validators=[v.Required(), v.NumberRange(min=50, max=100)]
    )
