from math import ceil

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
        if slug not in [slug.slug for slug in request.context['recipe'].slugs]:
            abort(404)

    @expose('recipes/builder/index.html')
    @expose('json', content_type='application/json')
    def index(self):
        recipe = request.context['recipe']
        if recipe.state == "DRAFT":
            if recipe.author and recipe.author != request.context['user']:
                abort(404)

        # Log a view for the recipe (if the viewer *is not* the author)
        if recipe.author != request.context['user']:
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

        different_user = source.author != request.context['user']

        copy = source.duplicate({
            'name': source.name if different_user else
                                "%s (Duplicate)" % source.name,
            'author': request.context['user']
                                })

        if different_user:
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

        perpage = 15.0
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

        query = select(
            [
                model.Recipe.id,
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

        recipes = model.Recipe.query.from_statement(query.order_by(
            *[order_direction(column) for column in order_column]
        ).offset(
            offset
        ).limit(
            perpage
        )).all()

        return dict(
            pages=max(1, int(ceil(total / perpage))),
            current_page=kw['page'],
            offset=offset,
            perpage=perpage,
            total=total,
            order_by=kw['order_by'],
            direction=kw['direction'],
            recipes=recipes
        )

    create = RecipeCreationController()
