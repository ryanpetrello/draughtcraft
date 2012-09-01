from datetime import timedelta
from json import loads

from pecan import (expose, request, abort, redirect)
from pecan.rest import RestController
from pecan.secure import SecureController


class RecipeBuilderController(RestController, SecureController):

    @classmethod
    def check_permissions(cls):
        recipe = request.context['recipe']
        if recipe.state != 'DRAFT':
            return False
        if recipe.author:
            return recipe.author == request.context['user']
        if recipe == request.context['trial_recipe']:
            return True
        return False

    @expose('recipes/builder/index.html')
    @expose('json', content_type='application/json')
    def get_all(self):
        return dict(
            recipe=request.context['recipe'],
            editable=True
        )

    @expose()
    def put(self, **kw):
        """
        Used to update the ingredients in the recipe.
        Contains a list of `additions` for which updated information is
        available.
        """
        try:
            kw = loads(kw.get('recipe'))
        except:
            abort(400)
        import pdb; pdb.set_trace()

        keys = ('mash_additions', 'boil_additions', 'fermentation_additions')
        for addition_class in keys:
            additions = kw.get(addition_class)
            for row in additions:
                # Clean up the hash a bit
                row.pop('type')

                # Grab the addition record
                addition = row.pop('addition')

                #
                # Apply the amount and unit
                # (if a valid amount/unit combination
                # can be parsed from the user's entry)
                #
                if 'amount' in row:
                    pair = row.pop('amount')
                    if pair:
                        amount, unit = pair
                        addition.amount = amount
                        addition.unit = unit or \
                            addition.ingredient.default_unit

                #
                # For "First Wort" additions,
                # change the duration to the full length of the boil
                #
                # For "Flame Out" additions,
                # change the duration to 0 minutes.
                #
                if 'use' in row:
                    if row['use'] == 'FIRST WORT':
                        row['duration'] = timedelta(
                            minutes=addition.recipe.boil_minutes
                        )
                    elif row['use'] == 'FLAME OUT':
                        row['duration'] = timedelta(minutes=0)
                    elif not row['duration']:
                        row['duration'] = timedelta(
                            minutes=addition.recipe.boil_minutes
                        )

                for k, v in row.items():
                    if v is not None:
                        setattr(addition, k, v)

        request.context['recipe'].touch()

    @expose(generic=True)
    def publish(self):
        abort(405)

    @publish.when(method='POST')
    def do_publish(self):
        recipe = request.context['recipe']
        recipe.publish()
        redirect('/profile/%s' % recipe.author.username)
