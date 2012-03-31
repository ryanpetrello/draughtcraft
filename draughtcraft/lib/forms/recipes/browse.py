from pecan.ext.wtforms import Form, fields as f, validators as v, default
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from draughtcraft import model


def any_style():
    return model.Style.query.all()


class RecipeSearchForm(Form):
    page = f.IntegerField('', filters=[default(1)], validators=[
        v.NumberRange(min=1)
    ])
    order_by = f.TextField('', filters=[default('last_updated')])
    direction = f.TextField('', filters=[default('DESC')], validators=[
        v.AnyOf(['ASC', 'DESC'])
    ])
    color = f.TextField('', filters=[default(None)], validators=[
        v.Optional(),
        v.AnyOf(['light', 'amber', 'brown', 'dark'])
    ])
    style = QuerySelectField(query_factory=any_style, allow_blank=True)

    mash = f.BooleanField('')
    minimash = f.BooleanField('')
    extract = f.BooleanField('')
