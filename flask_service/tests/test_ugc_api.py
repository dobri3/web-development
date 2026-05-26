import pytest
from jose import jwt

from flask_service.app import create_app, db, UGC


@pytest.fixture()
def app(monkeypatch, tmp_path):
    test_db_path = tmp_path / "test_ugc.sqlite3"

    monkeypatch.setenv("FLASK_DATABASE_URL", f"sqlite:///{test_db_path}")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret")
    monkeypatch.setenv("ALGORITHM", "HS256")

    app = create_app()
    app.config["TESTING"] = True

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def make_token(user_id=1, email="user@example.com", role="user"):
    return jwt.encode(
        {
            "sub": email,
            "user_id": user_id,
            "role": role,
            "type": "access",
        },
        "test-secret",
        algorithm="HS256",
    )


def auth_headers(user_id=1, email="user@example.com", role="user"):
    token = make_token(user_id=user_id, email=email, role=role)
    return {
        "Authorization": f"Bearer {token}",
    }


def test_create_review_success(client, monkeypatch):
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

    data = response.get_json()["data"]
    assert data["type"] == "review"
    assert data["text"] == "Good movie"
    assert data["rating"] == 8
    assert data["movie_id"] == 1
    assert data["user_id"] == 10
    assert data["status"] == "pending"


def test_create_ugc_requires_auth(client):
    response = client.post(
        "/ugc/",
        json={
            "type": "review",
            "text": "Good movie",
            "rating": 8,
            "movie_id": 1,
        },
    )

    assert response.status_code == 401
    assert response.get_json()["error"] == "AUTHENTICATION_FAILED"


def test_create_ugc_returns_404_when_movie_not_found(client, monkeypatch):
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

    assert response.status_code == 404
    assert response.get_json()["error"] == "MOVIE_NOT_FOUND"


def test_create_ugc_returns_503_when_django_unavailable(client, monkeypatch):
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

    assert response.status_code == 503
    assert response.get_json()["error"] == "DJANGO_SERVICE_UNAVAILABLE"


def test_comment_must_not_contain_rating(client, monkeypatch):
    monkeypatch.setattr(
        "flask_service.app.check_movie_exists",
        lambda movie_id: (True, True),
    )

    response = client.post(
        "/ugc/",
        json={
            "type": "comment",
            "text": "Just comment",
            "rating": 8,
            "movie_id": 1,
        },
        headers=auth_headers(user_id=1),
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "VALIDATION_ERROR"


def test_rating_must_not_contain_text(client, monkeypatch):
    monkeypatch.setattr(
        "flask_service.app.check_movie_exists",
        lambda movie_id: (True, True),
    )

    response = client.post(
        "/ugc/",
        json={
            "type": "rating",
            "text": "Text is not allowed here",
            "rating": 8,
            "movie_id": 1,
        },
        headers=auth_headers(user_id=1),
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "VALIDATION_ERROR"


def test_list_active_ugc_returns_only_active_items(client, app):
    with app.app_context():
        active_ugc = UGC(
            type="review",
            text="Visible review",
            rating=9,
            movie_id=1,
            user_id=1,
            status="active",
        )
        pending_ugc = UGC(
            type="review",
            text="Pending review",
            rating=8,
            movie_id=1,
            user_id=1,
            status="pending",
        )

        db.session.add(active_ugc)
        db.session.add(pending_ugc)
        db.session.commit()

    response = client.get("/ugc/?movie_id=1")

    assert response.status_code == 200

    data = response.get_json()["data"]
    assert len(data) == 1
    assert data[0]["text"] == "Visible review"
    assert data[0]["status"] == "active"


def test_moderator_can_update_ugc_status(client, app):
    with app.app_context():
        ugc = UGC(
            type="review",
            text="Review for moderation",
            rating=7,
            movie_id=1,
            user_id=1,
            status="pending",
        )
        db.session.add(ugc)
        db.session.commit()
        ugc_id = ugc.id

    response = client.patch(
        f"/ugc/{ugc_id}/status",
        json={"status": "active"},
        headers=auth_headers(user_id=2, role="moderator"),
    )

    assert response.status_code == 200

    data = response.get_json()["data"]
    assert data["status"] == "active"


def test_regular_user_cannot_update_ugc_status(client, app):
    with app.app_context():
        ugc = UGC(
            type="review",
            text="Review for moderation",
            rating=7,
            movie_id=1,
            user_id=1,
            status="pending",
        )
        db.session.add(ugc)
        db.session.commit()
        ugc_id = ugc.id

    response = client.patch(
        f"/ugc/{ugc_id}/status",
        json={"status": "active"},
        headers=auth_headers(user_id=1, role="user"),
    )

    assert response.status_code == 403
    assert response.get_json()["error"] == "FORBIDDEN"


def test_user_can_hide_own_ugc(client, app):
    with app.app_context():
        ugc = UGC(
            type="review",
            text="My review",
            rating=7,
            movie_id=1,
            user_id=1,
            status="active",
        )
        db.session.add(ugc)
        db.session.commit()
        ugc_id = ugc.id

    response = client.patch(
        f"/ugc/{ugc_id}/hide",
        headers=auth_headers(user_id=1, role="user"),
    )

    assert response.status_code == 200

    data = response.get_json()["data"]
    assert data["status"] == "hidden"


def test_user_cannot_hide_other_users_ugc(client, app):
    with app.app_context():
        ugc = UGC(
            type="review",
            text="Other user review",
            rating=7,
            movie_id=1,
            user_id=2,
            status="active",
        )
        db.session.add(ugc)
        db.session.commit()
        ugc_id = ugc.id

    response = client.patch(
        f"/ugc/{ugc_id}/hide",
        headers=auth_headers(user_id=1, role="user"),
    )

    assert response.status_code == 403
    assert response.get_json()["error"] == "FORBIDDEN"