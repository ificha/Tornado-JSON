from tornado.web import RequestHandler
from jsonschema import ValidationError

from tornado_json.jsend import JSendMixin
from tornado_json.exceptions import APIError


class BaseHandler(RequestHandler):
    """BaseHandler for all other RequestHandlers"""

    __url_names__ = ["__self__"]
    __urls__ = []

    @property
    def db_conn(self):
        """Returns database connection abstraction

        If no database connection is available, raises an AttributeError
        """
        db_conn = self.application.db_conn
        if not db_conn:
            raise AttributeError("No database connection was provided.")
        return db_conn


class APIHandler(BaseHandler, JSendMixin):
    """RequestHandler for API calls

    - Sets header as ``application/json``
    - Provides custom write_error that writes error back as JSON \
    rather than as the standard HTML template
    """

    def initialize(self):
        """
        - Set Content-type for JSON
        """
        self.set_header("Content-Type", "application/json")


    def error(self, error, http_code):

        self.write({'status': 'failed', 'error': error})
        self.set_status(http_code)
        self.finish()


    def success(self, data):

        self.write({'status': 'success', 'data': data})
        self.finish()

