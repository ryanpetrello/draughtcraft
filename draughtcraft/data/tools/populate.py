from pecan.commands.base            import BaseCommand
from elixir                         import entities
from sqlalchemy.ext.sqlsoup         import SqlSoup

from draughtcraft                   import model, data

import os

BLUE = '\033[94m'
DARKBLUE = '\033[90m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
ENDS = '\033[0m'


def ne(x, y, tolerance=0.01):
    if type(x) is float and type(y) is float:
        return abs(x - y) <= 0.5 * tolerance * (x + y)
    return x == y


class PopulateCommand(BaseCommand):
    """
    Load a pecan environment and initializate the database.
    """

    def run(self, args):
        super(PopulateCommand, self).run(args)
        self.load_app()

        print "=" * 80
        print BLUE + "LOADING ENVIRONMENT" + ENDS
        print "=" * 80

        print BLUE + "BUILDING SCHEMA" + ENDS
        print "=" * 80
        try:
            print "STARTING A TRANSACTION..."
            print "=" * 80
            model.start()
            model.metadata.create_all()

            print BLUE + "GENERATING INGREDIENTS" + ENDS
            print "=" * 80
            populate()
        except:
            model.rollback()
            print "=" * 80
            print "%s ROLLING BACK... %s" % (RED, ENDS)
            print "=" * 80
            raise
        else:
            print "=" * 80
            print "%s COMMITING... %s" % (GREEN, ENDS)
            print "=" * 80
            model.commit()


def populate():

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
        print "-" * 80
        print DARKBLUE + table.upper() + ENDS
        print "-" * 80
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
            uid = kwargs['uid']
            ingredient = getattr(entities, cls).get_by(uid=uid)

            # If the entity doesn't already exist, create it
            new = False
            changed = False

            if ingredient is None:
                new = True
                ingredient = getattr(entities, cls)()

            # Update necessary columns
            for k, v in kwargs.items():
                if not ne(getattr(ingredient, k), v):
                    changed = True

                if k == 'liquid':
                    v = True if v == 1 else False

                setattr(ingredient, k, v)

            if new is True:
                print "%s (%s)" % (
                    ingredient.printed_name.encode('utf-8', 'ignore'),
                    '%s New %s' % (GREEN, ENDS)
                )
            elif changed is True:
                print "%s (%s)" % (
                    ingredient.printed_name.encode('utf-8', 'ignore'),
                    '%s Updated %s' % (YELLOW, ENDS)
                )
            else:
                print "%s (No Changes)" % ingredient.printed_name.encode(
                    'utf-8', 'ignore'
                )

    print "=" * 80
    print BLUE + "GENERATING STYLES" + ENDS
    print "=" * 80

    handle = SqlSoup(
        'sqlite:///%s' % os.path.join(path, 'styles.db')
    )
    for style in handle.styles.all():
        # Coerce the data mapping into a dictionary
        kwargs = dict(
            (
                k,
                getattr(style, k, '')
            )
            for k in style.c.keys()
        )

        # Attempt to look up the entity first
        uid = kwargs['uid']
        style = entities.Style.get_by(uid=uid)

        # If the entity doesn't already exist, create it
        new = False
        changed = False

        if style is None:
            new = True
            style = entities.Style()

        # Update necessary columns
        for k, v in kwargs.items():
            if not ne(getattr(style, k), v):
                changed = True
            setattr(style, k, v)

        if new is True:
            print "%s (%s)" % (
                style.name.encode('utf-8', 'ignore'),
                '%s New %s' % (GREEN, ENDS)
            )
        elif changed is True:
            print "%s (%s)" % (
                style.name.encode('utf-8', 'ignore'),
                '%s Updated %s' % (YELLOW, ENDS)
            )
        else:
            print "%s (No Changes)" % style.name.encode('utf-8', 'ignore')

    model.commit()
