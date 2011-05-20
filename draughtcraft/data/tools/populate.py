from elixir                         import entities
from draughtcraft                   import model
from draughtcraft.data              import ingredients

for type in ('Fermentable', 'Hop', 'Yeast', 'Extra'):
    for ingredient in getattr(ingredients, type, []):
        result = getattr(entities, type)(**ingredient)
        print result.printed_name

model.commit()
