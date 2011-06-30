from pecan import expose

class SignupController(object):

    @expose('signup/index.html')
    def index(self):
        return dict()
