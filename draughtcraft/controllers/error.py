from pecan import expose


class ErrorController(object):

    default_status = (
        "An Error Occurred",
        """
        Sorry, something seems to have gone wrong in handling your request.
        """
    )
    status = {
        401: ("Unauthorized", "Sorry, you don't have permission to access this page."),
        403: ("Unauthorized", "Sorry, you don't have permission to access this page."),
        404: ("Not Found", "Sorry, we couldn't find the page you were looking for.  This might be a temporary issue, or the result of a bad link.")
    }

    @expose('error.html')
    def _default(self, code):
        error, msg = self.status.get(int(code), self.default_status)
        return dict(
            error=error,
            msg=msg
        )
