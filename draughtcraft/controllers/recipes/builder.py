from datetime import timedelta
from json import loads

from elixir import entities
from pecan import (expose, request, abort, redirect)
from pecan.rest import RestController


class RecipeBuilderController(RestController):

    _custom_actions = {
        'publish': ['POST']
    }

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

    @expose('json')
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

        recipe = request.context['recipe']
        self.save_name(recipe, kw.get('name'))
        self.save_volume(recipe, kw.get('volume'))
        recipe.touch()
        return dict()

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

    def save_name(self, recipe, name):
        if recipe.name != name:
            recipe.slugs.append(
                entities.RecipeSlug(name=name)
            )
        recipe.name = name

    def save_volume(self, recipe, gallons):
        recipe.gallons = gallons

    def save_style(self, recipe, style):
        recipe.style = entities.RecipeStyle.get(style)

    @expose(generic=True)
    def publish(self):
        pass  # pragma: nocover

    @publish.when(method='POST')
    def do_publish(self):
        recipe = request.context['recipe']
        recipe.publish()
        redirect('/profile/%s' % recipe.author.username)
