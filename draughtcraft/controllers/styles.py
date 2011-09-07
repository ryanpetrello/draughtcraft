from pecan                  import expose, abort
from pecan.rest             import RestController
from draughtcraft           import model


class StylesController(RestController):

    @expose('styles/index.html')
    def get_one(self, styleID):
        style = model.Style.get(int(styleID))
        if style is None:
            abort(404)
        return dict(style=style)
