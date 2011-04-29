from pecan import expose


class RootController(object):

    @expose('index.html')
    def index(self):
        return dict()
