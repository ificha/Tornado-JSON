from tornado.web import HTTPError


class APIError(HTTPError):
    """Equivalent to ``RequestHandler.HTTPError`` except for in name"""
