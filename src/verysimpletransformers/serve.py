"""
Simple HTTP web server.
"""

from __future__ import annotations

import http.server
import json
import typing
from urllib.parse import parse_qs

import numpy

if typing.TYPE_CHECKING:  # pragma: no cover
    from .types import AllSimpletransformersModels


class MachineLearningModelHandler(http.server.SimpleHTTPRequestHandler):
    """
    Handles GET and POST.
    """

    model: AllSimpletransformersModels

    def __init__(self, model: AllSimpletransformersModels, *a: typing.Any, **kw: typing.Any) -> None:
        """
        Store the model when the handler is created for user on request.
        """
        self.model = model
        super().__init__(*a, **kw)

    def _predict(self, inputs: list[str]) -> list[str | int]:
        """
        Shortcut to get the outputs from the model based on the inputs.
        """
        predictions, _ = self.model.predict(inputs)

        if isinstance(predictions, numpy.ndarray):  # pragma: no cover
            # happens if binary/numeric labels
            predictions = predictions.tolist()

        return typing.cast(list[str | int], predictions)

    def respond(
        self, response_data: typing.Any, content_type: str = "application/json", status_code: int = 200
    ) -> None:
        """
        Send a HTTP response.

        Sends json back in most cases, because that's just the easiest.
        """
        if not isinstance(response_data, str):
            if content_type == "application/json":
                response_data = json.dumps(response_data)
            else:  # pragma: no cover
                # todo: support more content types?
                content_type = "text/plain"
                response_data = str(response_data)

        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.end_headers()
        self.wfile.write(response_data.encode())

    def do_GET(self) -> None:
        """
        Parse ?query in GET requests.
        """
        if "?" not in self.path:
            return self.respond(
                "Please include a ?query=... in your GET-request.", content_type="text/plain", status_code=400
            )

        query_params = parse_qs(self.path.split("?")[1])

        if "query" not in query_params:
            return self.respond(
                "Please include a ?query=... in your GET-request.", content_type="text/plain", status_code=400
            )

        response_message = self._predict(query_params["query"])
        self.respond(response_message)

    def do_POST(self) -> None:
        """
        Either parse the JSON body or use the raw data as input.
        """
        content_type = self.headers.get("Content-Type")
        content_length = int(self.headers.get("Content-Length", 0))

        post_data = self.rfile.read(content_length)
        if not post_data:
            return self.respond("Missing POST data!", status_code=400)

        print(content_type, post_data)
        if content_type == "application/json":
            try:
                json_data = json.loads(post_data.decode("utf-8"))
                if not json_data:
                    return self.respond("Missing POST data!", status_code=400)
                if not isinstance(json_data, list):
                    json_data = [json_data]
                response_data = self._predict(json_data)
                self.respond(response_data)
            except json.JSONDecodeError:
                self.respond("Invalid JSON data", status_code=400)
        else:
            response_message = self._predict([post_data.decode("utf-8")])
            self.respond(response_message)

    @classmethod
    def bind(cls, model: "AllSimpletransformersModels") -> typing.Callable[..., "MachineLearningModelHandler"]:
        """
        The http.server.HTTPServer needs a callable that returns an instance, but we also want to pass model.

        `MachineLearningModelHandler.bind(model)` returns exactly what HTTPServer expects as request handler class.
        """

        def wrapper(*args: typing.Any, **kwargs: typing.Any) -> "MachineLearningModelHandler":
            return MachineLearningModelHandler(model, *args, **kwargs)

        return wrapper


class MachineLearningModelServer:  # pragma: no cover
    """
    Shortcut that combines HTTPServer and MachineLearningModelHandler.

    Usage:
        MachineLearningModelServer(host, port).serve_forever(model)
    """

    def __init__(self, server_address: str, port: int) -> None:
        """
        An address (e.g. localhost) and port (e.g. 8000) are required.
        """
        self.server_address = server_address
        self.port = port

    def serve_forever(self, model: "AllSimpletransformersModels") -> None:
        """
        Serve the model!
        """
        with http.server.HTTPServer((self.server_address, self.port), MachineLearningModelHandler.bind(model)) as httpd:
            httpd.serve_forever()
