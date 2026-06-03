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


@pytest.fixture()
def auth_headers():
    def _auth_headers(user_id=1, email="user@example.com", role="user"):
        token = jwt.encode(
            {
                "sub": email,
                "user_id": user_id,
                "role": role,
                "type": "access",
            },
            "test-secret",
            algorithm="HS256",
        )

        return {
            "Authorization": f"Bearer {token}",
        }

    return _auth_headers


@pytest.fixture()
def assert_error_response():
    def _assert_error_response(response, expected_code, expected_status_code):
        body = response.get_json()

        assert response.status_code == expected_status_code
        assert body["success"] is False
        assert body["error"]["code"] == expected_code
        assert body["error"]["status_code"] == expected_status_code
        assert "detail" in body["error"]

        return body["error"]

    return _assert_error_response


@pytest.fixture()
def make_ugc(app):
    def _make_ugc(
        type="review",
        text="Test review",
        rating=8,
        movie_id=1,
        user_id=1,
        status="active",
    ):
        ugc = UGC(
            type=type,
            text=text,
            rating=rating,
            movie_id=movie_id,
            user_id=user_id,
            status=status,
        )
        db.session.add(ugc)
        db.session.commit()
        return ugc

    return _make_ugc