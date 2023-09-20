import http.server
import json
from urllib.parse import parse_qs


class MachineLarningModelHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, model, *a, **kw):
        self.model = model
        super().__init__(*a, **kw)

    def respond(self, status_code, content_type, response_data):
        self.send_response(status_code)
        self.send_header("Content-type", content_type)
        self.end_headers()
        self.wfile.write(response_data.encode())

    def do_GET(self):
        query_params = parse_qs(self.path.split("?")[1])
        response_message = f"GET request received with query parameters: {query_params}"
        self.respond(200, "text/plain", response_message)

    def do_POST(self):
        content_type = self.headers.get("Content-Type")
        content_length = int(self.headers.get("Content-Length", 0))

        if content_type == "application/json":
            data = self.rfile.read(content_length)
            try:
                json_data = json.loads(data.decode("utf-8"))
                response_data = json.dumps(json_data)
                self.respond(200, "application/json", response_data)
            except json.JSONDecodeError:
                self.respond(400, "text/plain", "Invalid JSON data")
        else:
            post_data = self.rfile.read(content_length)
            response_message = f"POST request received with standard form data: {post_data.decode('utf-8')}"
            self.respond(200, "text/plain", response_message)


class MachineLarningModelServer:
    def __init__(self, server_address: str, port: int):
        self.server_address = server_address
        self.port = port

    def serve_forever(self, model):
        handler = lambda *args, **kwargs: MachineLarningModelHandler(model, *args, **kwargs)
        with http.server.HTTPServer((self.server_address, self.port), handler) as httpd:
            httpd.serve_forever()
