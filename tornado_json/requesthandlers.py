from tornado.web import RequestHandler
from jsonschema import ValidationError
from exceptions import APIError


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


class APIHandler(BaseHandler):
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

    def write_error(self, status_code, **kwargs):
        """Override of RequestHandler.write_error
        Calls ``error()`` or ``fail()`` from JSendMixin depending on which
        exception was raised with provided reason and status code.
        :type  status_code: int
        :param status_code: HTTP status code
        """
        def get_exc_message(exception):
            return exception.log_message if \
                hasattr(exception, "log_message") else str(exception)

        self.clear()
        self.set_status(status_code)

        # Any APIError exceptions raised will result in a JSend fail written
        # back with the log_message as data. Hence, log_message should NEVER
        # expose internals. Since log_message is proprietary to HTTPError
        # class exceptions, all exceptions without it will return their
        # __str__ representation.
        # All other exceptions result in a JSend error being written back,
        # with log_message only written if debug mode is enabled
        exception = kwargs["exc_info"][1]
        if any(isinstance(exception, c) for c in [APIError, ValidationError]):
            # ValidationError is always due to a malformed request
            if isinstance(exception, ValidationError):
                self.set_status(400)
                self.error(error={
                    "code": 100,
                    "message": get_exc_message(exception)
                })
        else:
            self.error(
                error={
                    "code": 101,
                    "message": self._reason
                },
                http_code=status_code
            )


    def success(self, data):
        """When an API call is successful, the JSend object is used as a simple
        envelope for the results, using the data key.
        :type  data: A JSON-serializable object
        :param data: Acts as the wrapper for any data returned by the API
            call. If the call returns no data, data should be set to null.
        """
        self.write({'status': 'success', 'data': data})
        self.finish()


    def error(self, error, http_code=400):
        """An error occurred in processing the request, i.e. an exception was
        thrown.
        """

        self.set_status(http_code)
        result = {'status': 'failed', 'error': error}

        self.write(result)
        self.finish()
