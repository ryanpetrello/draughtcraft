from pecan.commands.base            import Command
from elixir                         import entities
from sqlalchemy.ext.sqlsoup         import SqlSoup

from draughtcraft                   import model, data

import os
import sys
import json

BLUE = '\033[94m'
DARKBLUE = '\033[90m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
ENDS = '\033[0m'

class EnvCommand(Command):
    """
    Load a pecan environment (namely, database initialization and binding).
    """
    
    # command information
    usage = 'CONFIG_NAME'
    summary = __doc__.strip().splitlines()[0].rstrip('.')
    
    # command options/arguments
    min_args = 1
    max_args = 1
    
    def command(self):
        
        # load the config and the app
        config = self.load_configuration(self.args[0])
        setattr(config.app, 'reload', False)
        self.load_app(config)

        # establish the model for the app
        self.load_model(config)


def run():
    print "="*80
    print BLUE + "CONFIGURING ENVIRONMENT" + ENDS
    print "="*80
    EnvCommand('env').run([sys.argv[1]])

    print BLUE + "BUILDING SCHEMA" + ENDS
    print "="*80
    model.start()
    model.metadata.create_all()

    print BLUE + "GENERATING INGREDIENTS" + ENDS
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
        print "-"*80
        print DARKBLUE + table.upper() + ENDS
        print "-"*80
        for ingredient in getattr(handle, table).order_by('id').all():

            # Coerce the data mapping into a dictionary
            kwargs = dict(
                (
                    k, 
                    getattr(ingredient, k, '')
                )
                for k in ingredient.c.keys()
            )

            # Attempt to look up the entity first
            primary_key = kwargs.pop('id')
            ingredient = getattr(entities, cls).get(primary_key)

            # If the entity doesn't already exist, create it
            new = False
            changed = False

            if ingredient is None:
                new = True
                ingredient = getattr(entities, cls)()

            # Update necessary columns
            for k,v in kwargs.items():
                if getattr(ingredient, k) != v:
                    print "="*80
                    print k
                    print getattr(ingredient, k)
                    print v
                    print "="*80
                    changed = True
                setattr(ingredient, k, v)

            if new is True:
                print "%s (%s)" % (
                    ingredient.printed_name,
                    '%s New %s' % (GREEN, ENDS)
                )
            elif changed is True:
                print "%s (%s)" % (
                    ingredient.printed_name,
                    '%s Updated %s' % (YELLOW, ENDS)
                )
            else:
                print "%s (No Changes)" % ingredient.printed_name

    print BLUE + "GENERATING STYLES" + ENDS
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

if __name__ == '__main__':
    if len(sys.argv) == 2:
        run()
    else:
        print 'Usage: python populate.py /path/to/config.py'
