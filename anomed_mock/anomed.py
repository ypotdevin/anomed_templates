import json
import logging
from typing import Any

import falcon
import falcon.request

logging.basicConfig(
    format="{asctime} - {levelname} - {name}.{funcName}: {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.DEBUG,
)


class StaticJSONResource:
    """Any JSON serializable object, representing a "static" resource (i.e. a
    resource that does not depend on request parameters).

    The object will be represented as a plain JSON string, when a GET request is
    invoked."""

    def __init__(self, obj: Any):
        """
        Parameters
        ----------
        obj : Any
            A JSON serializable object, i.e. is should be compatible with
            `json.dumps`.
        """
        self._obj = obj

    def on_get(self, _, resp: falcon.Response):
        resp.text = json.dumps(self._obj)


class MirrorJSONResource:
    def on_post(self, req: falcon.Request, resp: falcon.Response):
        resp.status = falcon.HTTP_CREATED
        resp.text = json.dumps(req.get_media())


application = falcon.App()
application.add_route(
    "/", StaticJSONResource(dict(message="AnoMed mock server is alive!"))
)
application.add_route(
    "/submissions/anonymizer-evaluation-results", MirrorJSONResource()
)
application.add_route(
    "/submissions/deanonymizer-evaluation-results", MirrorJSONResource()
)
