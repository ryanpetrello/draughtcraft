from pecan.ext.wtforms import SecureForm, fields as f, validators as v


class RecipeCreationForm(SecureForm):
    name = f.TextField('Recipe Name', validators=[
        v.Required()
    ])
    type = f.SelectField('Recipe Type', choices=[
        ('EXTRACT', 'Extract'),
        ('EXTRACTSTEEP', 'Extract w/ Steeped Grains'),
        ('MINIMASH', 'Partial/Mini-Mash'),
        ('MASH', 'All Grain')
    ])

    volume = f.FloatField('Final Volume', validators=[
        v.Required()
    ])
    unit = f.HiddenField('', validators=[
        v.AnyOf(['GALLON', 'LITER'])
    ])
