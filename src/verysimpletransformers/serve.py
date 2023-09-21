from __future__ import annotations

import http.server
import json
import typing
from urllib.parse import parse_qs

import numpy

if typing.TYPE_CHECKING:
    from .types import AllSimpletransformersModels


class MachineLearningModelHandler(http.server.SimpleHTTPRequestHandler):
    model: AllSimpletransformersModels

    def __init__(self, model: AllSimpletransformersModels, *a: typing.Any, **kw: typing.Any) -> None:
        self.model = model
        super().__init__(*a, **kw)

    def _predict(self, inputs: list[str]) -> list[str | int]:
        predictions, _ = self.model.predict(inputs)

        if isinstance(predictions, numpy.ndarray):
            predictions = predictions.tolist()

        return typing.cast(list[str | int], predictions)

    def respond(
        self, response_data: typing.Any, content_type: str = "application/json", status_code: int = 200
    ) -> None:
        if not isinstance(response_data, str):
            if content_type == "application/json":
                response_data = json.dumps(response_data)
            else:
                # todo: support more content types?
                content_type = "text/plain"
                response_data = str(response_data)

        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.end_headers()
        self.wfile.write(response_data.encode())

    def do_GET(self) -> None:
        if "?" not in self.path:
            return self.respond("Please include a ?query=... in your GET-request.")

        query_params = parse_qs(self.path.split("?")[1])

        if "query" not in query_params:
            return self.respond("Please include a ?query=... in your GET-request.")

        response_message = self._predict(query_params["query"])
        self.respond(response_message)

    def do_POST(self) -> None:
        content_type = self.headers.get("Content-Type")
        content_length = int(self.headers.get("Content-Length", 0))

        if content_type == "application/json":
            data = self.rfile.read(content_length)
            try:
                json_data = json.loads(data.decode("utf-8"))
                if not isinstance(json_data, list):
                    json_data = [json_data]
                response_data = self._predict(json_data)
                self.respond(response_data)
            except json.JSONDecodeError:
                self.respond("Invalid JSON data", status_code=400)
        else:
            post_data = self.rfile.read(content_length)
            response_message = self._predict([post_data.decode("utf-8")])
            self.respond(response_message)

    @classmethod
    def bind(cls, model: "AllSimpletransformersModels") -> typing.Callable[..., "MachineLearningModelHandler"]:
        def wrapper(*args: typing.Any, **kwargs: typing.Any) -> "MachineLearningModelHandler":
            return MachineLearningModelHandler(model, *args, **kwargs)

        return wrapper


class MachineLearningModelServer:
    def __init__(self, server_address: str, port: int) -> None:
        self.server_address = server_address
        self.port = port

    def serve_forever(self, model: "AllSimpletransformersModels") -> None:
        with http.server.HTTPServer((self.server_address, self.port), MachineLearningModelHandler.bind(model)) as httpd:
            httpd.serve_forever()
