def test_create_review_success(client, auth_headers, monkeypatch):
    monkeypatch.setattr(
        "flask_service.app.check_movie_exists",
        lambda movie_id: (True, True),
    )

    response = client.post(
        "/ugc/",
        json={
            "type": "review",
            "text": "Good movie",
            "rating": 8,
            "movie_id": 1,
        },
        headers=auth_headers(user_id=10),
    )

    assert response.status_code == 201
    assert response.get_json()["success"] is True

    data = response.get_json()["data"]
    assert data["type"] == "review"
    assert data["text"] == "Good movie"
    assert data["rating"] == 8
    assert data["movie_id"] == 1
    assert data["user_id"] == 10
    assert data["status"] == "pending"


def test_create_ugc_requires_auth(client, assert_error_response):
    response = client.post(
        "/ugc/",
        json={
            "type": "review",
            "text": "Good movie",
            "rating": 8,
            "movie_id": 1,
        },
    )

    assert_error_response(response, "AUTHENTICATION_FAILED", 401)


def test_create_ugc_returns_404_when_movie_not_found(
    client,
    auth_headers,
    assert_error_response,
    monkeypatch,
):
    monkeypatch.setattr(
        "flask_service.app.check_movie_exists",
        lambda movie_id: (False, True),
    )

    response = client.post(
        "/ugc/",
        json={
            "type": "review",
            "text": "Good movie",
            "rating": 8,
            "movie_id": 999,
        },
        headers=auth_headers(user_id=1),
    )

    assert_error_response(response, "MOVIE_NOT_FOUND", 404)


def test_create_ugc_returns_503_when_django_unavailable(
    client,
    auth_headers,
    assert_error_response,
    monkeypatch,
):
    monkeypatch.setattr(
        "flask_service.app.check_movie_exists",
        lambda movie_id: (False, False),
    )

    response = client.post(
        "/ugc/",
        json={
            "type": "review",
            "text": "Good movie",
            "rating": 8,
            "movie_id": 1,
        },
        headers=auth_headers(user_id=1),
    )

    assert_error_response(response, "DJANGO_SERVICE_UNAVAILABLE", 503)