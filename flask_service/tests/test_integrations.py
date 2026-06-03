import httpx
import pytest

from flask_service.integrations import check_movie_exists


class FakeResponse:
    def __init__(self, status_code):
        self.status_code = status_code


def test_check_movie_exists_returns_true_when_django_returns_200(monkeypatch):
    called = {}

    def fake_get(url, timeout):
        called["url"] = url
        called["timeout"] = timeout
        return FakeResponse(200)

    monkeypatch.setenv("DJANGO_SERVICE_URL", "http://django:8000")
    monkeypatch.setattr("flask_service.integrations.httpx.get", fake_get)

    exists, django_available = check_movie_exists(10)

    assert exists is True
    assert django_available is True
    assert called["url"] == "http://django:8000/api/movies/10/"
    assert called["timeout"] == 2.0


def test_check_movie_exists_returns_false_true_when_movie_not_found(monkeypatch):
    def fake_get(url, timeout):
        return FakeResponse(404)

    monkeypatch.setattr("flask_service.integrations.httpx.get", fake_get)

    exists, django_available = check_movie_exists(999)

    assert exists is False
    assert django_available is True


def test_check_movie_exists_returns_false_false_when_django_returns_500(monkeypatch):
    def fake_get(url, timeout):
        return FakeResponse(500)

    monkeypatch.setattr("flask_service.integrations.httpx.get", fake_get)

    exists, django_available = check_movie_exists(1)

    assert exists is False
    assert django_available is False


def test_check_movie_exists_returns_false_false_on_timeout(monkeypatch):
    def fake_get(url, timeout):
        raise httpx.TimeoutException("Django timeout")

    monkeypatch.setattr("flask_service.integrations.httpx.get", fake_get)

    exists, django_available = check_movie_exists(1)

    assert exists is False
    assert django_available is False


def test_check_movie_exists_returns_false_false_on_request_error(monkeypatch):
    def fake_get(url, timeout):
        raise httpx.RequestError("Django unavailable")

    monkeypatch.setattr("flask_service.integrations.httpx.get", fake_get)

    exists, django_available = check_movie_exists(1)

    assert exists is False
    assert django_available is False


def test_check_movie_exists_strips_trailing_slash_from_django_url(monkeypatch):
    called = {}

    def fake_get(url, timeout):
        called["url"] = url
        return FakeResponse(200)

    monkeypatch.setenv("DJANGO_SERVICE_URL", "http://django:8000/")
    monkeypatch.setattr("flask_service.integrations.httpx.get", fake_get)

    check_movie_exists(5)

    assert called["url"] == "http://django:8000/api/movies/5/"