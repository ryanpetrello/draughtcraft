from elixir                         import entities
from beerparts                      import model
from beerparts.data                 import ingredients

for type in ('Fermentable', 'Hop', 'Yeast'):
    for ingredient in getattr(ingredients, type, []):
        result = getattr(entities, type)(**ingredient)
        print result.printed_name

model.commit()
