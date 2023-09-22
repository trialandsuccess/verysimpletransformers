import http.server
from threading import Thread

import pytest
import requests

from src.verysimpletransformers import from_vst
from src.verysimpletransformers.serve import MachineLearningModelHandler


@pytest.fixture(scope="module")
def custom_http_server():
    model = from_vst("pytest0.vst")

    httpd = http.server.HTTPServer(("localhost", 8000), MachineLearningModelHandler.bind(model))

    # Start the server in a separate thread
    server_thread = Thread(target=httpd.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    yield

    httpd.shutdown()
    server_thread.join()


@pytest.mark.usefixtures("custom_http_server")
def test_custom_server_response():
    resp = requests.get("http://localhost:8000", timeout=5)
    assert resp.status_code > 399

    resp = requests.get("http://localhost:8000?something=else", timeout=5)
    assert resp.status_code > 399

    resp = requests.post("http://localhost:8000", timeout=5)
    assert resp.status_code > 399

    resp = requests.post("http://localhost:8000", json=[], timeout=5)
    assert resp.status_code > 399

    resp = requests.post("http://localhost:8000", headers={"Content-Type": "application/json"}, timeout=5)
    assert resp.status_code > 399

    resp = requests.post("http://localhost:8000", data="False", headers={"Content-Type": "application/json"}, timeout=5)
    assert resp.status_code > 399

    resp = requests.get("http://localhost:8000?query=added", timeout=5)
    assert resp.status_code == 200
    assert resp.json()

    resp = requests.post("http://localhost:8000", data="something", timeout=5)
    assert resp.status_code == 200
    assert resp.json()

    resp = requests.post("http://localhost:8000?query=added", json="something", timeout=5)
    assert resp.status_code == 200
    assert resp.json()
