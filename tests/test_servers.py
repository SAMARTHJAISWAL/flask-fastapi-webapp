import pytest
from fastapi.testclient import TestClient

import server1
import server2

FAKE = {"finished": [2020], "failed": []}


@pytest.fixture(autouse=True)
def no_network(monkeypatch, tmp_path):
    calls = []

    def fake_run(start_year=None, years_ago=0):
        calls.append((start_year, years_ago))
        if years_ago < 0:
            raise ValueError("years_ago must be a non-negative integer")
        return FAKE

    monkeypatch.setattr(server1, "scrape_runner", fake_run)
    monkeypatch.setattr(server2, "scrape_runner", fake_run)
    monkeypatch.setattr("logger.log_dir", str(tmp_path))
    return calls


def test_flask_routes(no_network):
    client = server1.app.test_client()
    assert client.get("/").status_code == 200
    r = client.post("/box-office-mojo-scraper", json={"start_year": 2020, "years_ago": 1})
    assert r.get_json() == FAKE
    assert no_network == [(2020, 1)]
    assert client.post("/box-office-mojo-scraper", json={"years_ago": -1}).status_code == 400


def test_flask_scraper_without_body(no_network):
    r = server1.app.test_client().post("/box-office-mojo-scraper")
    assert r.status_code == 200
    assert no_network == [(None, 0)]


def test_fastapi_routes(no_network):
    client = TestClient(server2.app)
    assert client.get("/").json() == {"hello": "world"}
    assert client.post("/box-office-mojo-scraper", json={"start_year": 2020}).json() == FAKE
    assert client.post("/box-office-mojo-scraper").status_code == 200
    assert client.post("/box-office-mojo-scraper", json={"years_ago": -1}).status_code == 400
