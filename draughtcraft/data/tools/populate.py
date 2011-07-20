from elixir                         import entities
from sqlalchemy.ext.sqlsoup         import SqlSoup

from draughtcraft                   import model, data

import os
import json

print "BUILDING SCHEMA"
print "="*80
model.start()
model.metadata.create_all()

print "GENERATING INGREDIENTS"
print "="*80

tables = [
    ('fermentables', 'Fermentable'),
    ('hops', 'Hop'),
    ('yeast', 'Yeast'),
    ('extras', 'Extra')
]

path = os.path.dirname(os.path.abspath(data.__file__))
handle = SqlSoup(
    'sqlite:///%s' % os.path.join(path, 'ingredients.db')
)

for table, cls in tables:
    for ingredient in getattr(handle, table).all():

        # Coerce the data mapping into a dictionary
        kwargs = dict(
            (
                k, 
                getattr(ingredient, k, '')
            )
            for k in ingredient.c.keys()
        )

        # Attempt to look up the entity first
        ingredient = getattr(entities, cls).get(kwargs['id'])

        # If the entity doesn't already exist, create it
        if ingredient is None:
            ingredient = getattr(entities, cls)()

        # Update necessary columns
        for k,v in kwargs.items():
            setattr(ingredient, k, v)

        print ingredient.printed_name

print "GENERATING STYLES"
print "="*80

path = os.path.dirname(os.path.abspath(data.__file__))
handle = open(os.path.join(path, 'styles.js'), 'rb')
styles = json.loads(handle.read())

for s in styles:
    s = dict([(str(k), v) for k,v in s.items()])
    style = entities.Style(**s)

    # Normalize ABV as a percentage
    if style.min_abv and style.max_abv:
        style.min_abv /= 100
        style.max_abv /= 100

    print style.name

model.commit()
