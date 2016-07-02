from math import ceil
from hashlib import md5

from pecan import expose, request, abort, response, redirect
from pecan.secure import secure
from pecan.ext.wtforms import with_form
from sqlalchemy import select, and_, or_, asc, desc, func, case, literal

from draughtcraft import model
from draughtcraft.lib.beerxml import export
from draughtcraft.lib.forms.recipes.browse import RecipeSearchForm
from create import RecipeCreationController
from builder import RecipeBuilderController


class SlugController(object):

    def __init__(self, slug):
        self.slug = slug

        # Make sure the provided slug is valid
        if not slug:
            redirect(request.context['recipe'].slugs[0].slug)

        if slug not in [slug.slug for slug in request.context['recipe'].slugs]:
            abort(404)

    @expose('recipes/builder/index.html')
    @expose('json', content_type='application/json')
    def index(self):
        recipe = request.context['recipe']
        if recipe.state == "DRAFT":
            if recipe.author and recipe.author != request.context['user']:
                abort(404)
            if not recipe.author and recipe != request.context['trial_recipe']:
                abort(404)

        # Log a view for the recipe (if the viewer *is not* the author)
        if recipe.author != request.context['user'] and \
                request.pecan.get('content_type') == 'application/json':
            model.RecipeView(recipe=recipe)

        return dict(
            recipe=recipe,
            editable=False
        )

    @expose(content_type='application/xml')
    def xml(self):
        recipe = request.context['recipe']
        if recipe.state == "DRAFT":
            if recipe.author and recipe.author != request.context['user']:
                abort(404)

        response.headers['Content-Disposition'] = \
            'attachment; filename="%s.xml"' % self.slug
        return export.to_xml([request.context['recipe']])

    @expose(generic=True)
    def draft(self):
        abort(405)

    @draft.when(method="POST")
    def do_draft(self):
        source = request.context['recipe']
        if source.author is None or source.author != request.context['user']:
            abort(401)
        if source.state != "PUBLISHED":
            abort(401)

        draft = source.draft()
        draft.flush()
        redirect("%sbuilder" % draft.url())

    @expose(generic=True)
    def copy(self):
        abort(405)

    @copy.when(method="POST")
    def do_copy(self):
        source = request.context['recipe']
        if request.context['user'] is None:
            redirect("/signup")
        if source.author is None:
            abort(401)

        diff_user = source.author != request.context['user']

        name = source.name if diff_user else "%s (Duplicate)" % source.name
        copy = source.duplicate({
            'name': name,
            'author': request.context['user']
        })

        if diff_user:
            copy.copied_from = source

        redirect("/")

    @expose(generic=True)
    def delete(self):
        abort(405)

    @delete.when(method="POST")
    def do_delete(self):
        source = request.context['recipe']
        if source.author is None or source.author != request.context['user']:
            abort(401)

        source.delete()
        redirect("/")

    builder = secure(
        RecipeBuilderController(),
        RecipeBuilderController.check_permissions
    )


class RecipeController(object):

    @expose()
    def _lookup(self, slug, *remainder):
        return SlugController(slug), remainder

    def __init__(self, recipeID):
        try:
            primary_key = int(str(recipeID), 16)
        except ValueError:
            abort(404)
        recipe = model.Recipe.get(primary_key)
        if recipe is None:
            abort(404)

        request.context['recipe'] = recipe


class RecipesController(object):

    @expose()
    def _lookup(self, recipeID, *remainder):
        return RecipeController(recipeID), remainder

    @expose('recipes/browse/index.html')
    def index(self):
        return dict(
            styles=model.Style.query.order_by(model.Style.name).all()
        )

    @expose(template='recipes/browse/list.html')
    @with_form(RecipeSearchForm, validate_safe=True)
    def recipes(self, **kw):
        if request.pecan['form'].errors:
            abort(400)

        perpage = 25.0
        offset = int(perpage * (kw['page'] - 1))

        views = func.count(model.RecipeView.id).label('views')
        username = func.lower(model.User.username).label('username')

        sortable_type = case([
            (model.Recipe.type == 'MASH', literal('All Grain')),
            (model.Recipe.type == 'EXTRACT', literal('Extract')),
            (
                model.Recipe.type == 'EXTRACTSTEEP',
                literal('Extract w/ Steeped Grains')
            ),
            (model.Recipe.type == 'MINIMASH', literal('Mini-Mash')),
        ]).label('type')

        # map of columns
        column_map = dict(
            type=(sortable_type,),
            srm=(model.Recipe._srm,),
            name=(model.Recipe.name,),
            author=(username,),
            style=(model.Style.name,),
            last_updated=(model.Recipe.last_updated,),
            views=(views,)
        )

        # determine the sorting direction and column
        order_column = column_map.get(kw['order_by'])
        order_direction = dict(
            ASC=asc,
            DESC=desc
        ).get(kw['direction'])

        where = [
            model.Recipe.state == 'PUBLISHED'
        ]

        # If applicable, filter by style
        if kw['style']:
            query = where.append(model.Recipe.style == kw['style'])

        # If applicable, filter by type (MASH, etc...)
        where.append(or_(
            model.Recipe.id is None,
            model.Recipe.type == 'MASH' if kw['mash'] else None,
            model.Recipe.type == 'MINIMASH' if kw['minimash'] else None,
            model.Recipe.type.in_(('EXTRACTSTEEP', 'EXTRACT'))
                     if kw['extract'] else None,
                     ))

        # If applicable, filter by color
        if kw['color']:
            start, end = {
                'light': (0, 8),
                'amber': (8, 18),
                'brown': (16, 25),
                'dark': (25, 5000)
            }.get(kw['color'])

            where.append(and_(
                model.Recipe._srm >= start,
                model.Recipe._srm <= end,
            ))

        # Join the `recipe`, `recipeview`, `user`, and `style` tables
        from_obj = model.Recipe.table.outerjoin(
            model.RecipeView.table,
            onclause=model.RecipeView.recipe_id == model.Recipe.id
        ).outerjoin(
            model.Style.table,
            onclause=model.Recipe.style_id == model.Style.id
        ).join(
            model.User.table,
            onclause=model.Recipe.author_id == model.User.id
        )

        username_full = model.User.username.label('username')
        email = model.User.email.label('email')
        style_name = model.Style.name.label('style_name')
        style_url = model.Style.url.label('style_url')
        query = select(
            [
                model.Recipe.id,
                model.Recipe.name,
                model.Recipe._srm,
                username_full,
                email,
                sortable_type,
                style_name,
                style_url,
                model.Recipe.last_updated,
                views
            ],
            and_(*where),
            from_obj=[from_obj],
            group_by=model.Recipe.id
        )
        total = select(
            [func.count(model.Recipe.id)],
            and_(*where)
        ).execute().fetchone()[0]

        if views not in order_column:
            query = query.group_by(*order_column)

        query = query.group_by(username_full)
        query = query.group_by(email)
        query = query.group_by(style_name)
        query = query.group_by(style_url)

        recipes = query.order_by(
            *[order_direction(column) for column in order_column]
        ).offset(
            offset
        ).limit(
            perpage
        ).execute().fetchall()

        class RecipeProxy(object):

            def __init__(self, recipe):
                self.id, self.name, self._srm, self.username, self.email, self.printable_type, self.style_name, self.style_url, self.last_updated, self.views = recipe

            @property
            def metric_unit(self):
                return 'EBC' if request.context['metric'] is True else 'SRM'

            @property
            def color(self):
                if self.metric_unit is 'SRM':
                    return self._srm
                round(self._srm * 1.97, 1)

            @property
            def gravatar(self):
                return 'https://www.gravatar.com/avatar/%s?d=https://draughtcraft.com/images/glass-square.png' % (
                    md5(self.email.strip().lower()).hexdigest()
                )

            @property
            def url(self):
                return '/recipes/%s/' % (('%x' % self.id).lower())

        return dict(
            pages=max(1, int(ceil(total / perpage))),
            current_page=kw['page'],
            offset=offset,
            perpage=perpage,
            total=total,
            order_by=kw['order_by'],
            direction=kw['direction'],
            recipes=map(RecipeProxy, recipes)
        )

    create = RecipeCreationController()
