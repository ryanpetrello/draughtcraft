from pecan import request
from pecan.hooks import PecanHook
from draughtcraft import model


class AuthenticationHook(PecanHook):
    """
    Stores the currently logged-in user in the request context.
    """

    def _get_current_user(self, session):
        if 'user_id' in session:
            return model.User.get(session['user_id'])
        else:
            return None

    def _get_trial_recipe(self, session):
        if 'trial_recipe_id' in session:
            return model.Recipe.get(session['trial_recipe_id'])
        else:
            return None

    def _get_metric(self, session):
        user = self._get_current_user(session)
        if user is not None:
            return user.settings.get('unit_system', 'US') == 'METRIC'
        elif 'metric' in session:
            return session['metric']
        return False

    def on_route(self, state):
        session = state.request.environ['beaker.session']
        request.context['user'] = self._get_current_user(session)
        request.context['trial_recipe'] = self._get_trial_recipe(session)
        request.context['metric'] = self._get_metric(session)


def save_user_session(user):
    session = request.environ['beaker.session']
    session['user_id'] = user.id
    session.save()


def remove_user_session():
    session = request.environ['beaker.session']
    session.delete()


def save_trial_recipe(recipe):
    session = request.environ['beaker.session']
    session['trial_recipe_id'] = recipe.id
    session.save()


def remove_trial_recipe():
    session = request.environ['beaker.session']
    del session['trial_recipe_id']
    session.save()
