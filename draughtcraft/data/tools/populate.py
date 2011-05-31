from elixir                         import entities
from draughtcraft                   import model, data

import os
import json

print "BUILDING SCHEMA"
print "="*80
model.start()
model.metadata.create_all()

print "GENERATING INGREDIENTS"
print "="*80

files = [
    ('fermentables.js', 'Fermentable'),
    ('hops.js', 'Hop'),
    ('yeast.js', 'Yeast'),
    ('extras.js', 'Extra')
]

for f, type in files:

    path = os.path.dirname(os.path.abspath(data.__file__))
    handle = open(os.path.join(path, f), 'rb')
    jsondata = json.loads(handle.read())

    for ingredient in jsondata:
        ingredient = dict([(str(k), v) for k,v in ingredient.items()])
        result = getattr(entities, type)(**ingredient)
        print result.printed_name

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
