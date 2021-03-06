from json import loads
from datetime import timedelta

from elixir import entities
from pecan import (expose, request, abort, redirect)
from pecan.rest import RestController


class RecipePublishController(object):

    @expose(generic=True)
    def index(self):
        pass  # pragma: nocover

    @index.when(method='POST')
    def do_index(self):
        recipe = request.context['recipe']
        recipe.publish()
        redirect('/profile/%s' % recipe.author.username)


class RecipeBuilderController(RestController):

    publish = RecipePublishController()

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
    def get_all(self):
        return dict(
            recipe=request.context['recipe'],
            editable=True
        )

    @expose('json', content_type='application/json')
    def post(self):
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

        # recipe metadata
        self.save_name(recipe, kw.get('name'))
        self.save_volume(recipe, kw.get('gallons'))
        self.save_style(recipe, kw.get('style'))
        self.save_mash_settings(recipe, **kw)
        self.save_boil_settings(recipe, **kw)
        self.save_fermentation_schedule(
            recipe,
            kw.get('fermentation_steps', [])
        )
        recipe.notes = kw.get('notes')

        # additions
        recipe.additions = []
        self.save_mash(recipe, kw.get('mash', {}).get('additions', []))
        self.save_boil(recipe, kw.get('boil', {}).get('additions', []))
        self.save_fermentation(
            recipe,
            kw.get('fermentation', {}).get('additions', [])
        )

        recipe.touch()

        # adjust the metric setting (if necessary)
        if request.context['user'] is None:
            session = request.environ['beaker.session']
            session['metric'] = kw.get('metric')
            session.save()

        return dict()

    def save_name(self, recipe, name):
        if recipe.name != name:
            recipe.slugs.append(
                entities.RecipeSlug(name=name)
            )
        recipe.name = name

    def save_volume(self, recipe, gallons):
        recipe.gallons = gallons

    def save_style(self, recipe, style):
        recipe.style = entities.Style.get(style) if style else None

    def save_mash_settings(self, recipe, **kw):
        recipe.mash_method = kw.get('mash_method')
        recipe.mash_instructions = kw.get('mash_instructions')

    def save_boil_settings(self, recipe, **kw):
        recipe.boil_minutes = kw.get('boil_minutes')

    def save_fermentation_schedule(self, recipe, steps):
        recipe.fermentation_steps = []
        for step in steps:
            recipe.fermentation_steps.append(
                entities.FermentationStep(
                    step=step['step'],
                    days=step['days'],
                    fahrenheit=step['fahrenheit']
                )
            )

    def save_step(self, recipe, additions):
        for a in additions:
            if not a['amount']:
                continue

            # Look up the ingredient
            ingredient = a.pop('ingredient')
            cls = {'Hop': entities.HopAddition}.get(
                ingredient['class'],
                entities.RecipeAddition
            )
            ingredient = getattr(entities, ingredient['class']).get(
                ingredient['id']
            )

            # Handle boil durations
            if 'use' in a and 'duration' in a:
                if a['use'] == 'FIRST WORT':
                    a['duration'] = timedelta(minutes=int(recipe.boil_minutes))
                elif a['use'] == 'FLAME OUT':
                    a['duration'] = timedelta(minutes=0)
                else:
                    a['duration'] = timedelta(minutes=int(a['duration']))

            # Create a new RecipeAddition
            entity = cls(
                recipe=recipe,
                **a
            )

            # Assign the ingredient
            setattr(entity, ingredient.row_type, ingredient)

    save_mash = save_step
    save_boil = save_step
    save_fermentation = save_step
