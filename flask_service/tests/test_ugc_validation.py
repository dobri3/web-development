def test_comment_must_not_contain_rating(
    client,
    auth_headers,
    assert_error_response,
):
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

    error = assert_error_response(response, "VALIDATION_ERROR", 400)
    assert error["detail"] == "comment must not contain rating"


def test_rating_must_not_contain_text(
    client,
    auth_headers,
    assert_error_response,
):
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

    error = assert_error_response(response, "VALIDATION_ERROR", 400)
    assert error["detail"] == "rating must not contain text"


def test_create_ugc_rejects_invalid_type(
    client,
    auth_headers,
    assert_error_response,
):
    response = client.post(
        "/ugc/",
        json={
            "type": "invalid",
            "text": "Good movie",
            "rating": 8,
            "movie_id": 1,
        },
        headers=auth_headers(user_id=1),
    )

    error = assert_error_response(response, "VALIDATION_ERROR", 400)
    assert error["detail"] == "type must be one of: review, comment, rating"


def test_create_ugc_rejects_empty_text(
    client,
    auth_headers,
    assert_error_response,
):
    response = client.post(
        "/ugc/",
        json={
            "type": "review",
            "text": "   ",
            "rating": 8,
            "movie_id": 1,
        },
        headers=auth_headers(user_id=1),
    )

    error = assert_error_response(response, "VALIDATION_ERROR", 400)
    assert error["detail"] == "text cannot be empty"


def test_create_ugc_rejects_invalid_rating_type(
    client,
    auth_headers,
    assert_error_response,
):
    response = client.post(
        "/ugc/",
        json={
            "type": "review",
            "text": "Good movie",
            "rating": "bad",
            "movie_id": 1,
        },
        headers=auth_headers(user_id=1),
    )

    error = assert_error_response(response, "VALIDATION_ERROR", 400)
    assert error["detail"] == "rating must be a number from 1 to 10"


def test_create_ugc_rejects_rating_out_of_range(
    client,
    auth_headers,
    assert_error_response,
):
    response = client.post(
        "/ugc/",
        json={
            "type": "review",
            "text": "Good movie",
            "rating": 11,
            "movie_id": 1,
        },
        headers=auth_headers(user_id=1),
    )

    error = assert_error_response(response, "VALIDATION_ERROR", 400)
    assert error["detail"] == "rating must be a number from 1 to 10"


def test_create_ugc_rejects_missing_movie_id(
    client,
    auth_headers,
    assert_error_response,
):
    response = client.post(
        "/ugc/",
        json={
            "type": "review",
            "text": "Good movie",
            "rating": 8,
        },
        headers=auth_headers(user_id=1),
    )

    error = assert_error_response(response, "VALIDATION_ERROR", 400)
    assert error["detail"] == "movie_id is required"


def test_create_ugc_rejects_invalid_movie_id(
    client,
    auth_headers,
    assert_error_response,
):
    response = client.post(
        "/ugc/",
        json={
            "type": "review",
            "text": "Good movie",
            "rating": 8,
            "movie_id": "abc",
        },
        headers=auth_headers(user_id=1),
    )

    error = assert_error_response(response, "VALIDATION_ERROR", 400)
    assert error["detail"] == "movie_id must be a number"


def test_public_ugc_list_requires_movie_id(
    client,
    assert_error_response,
):
    response = client.get("/ugc/")

    error = assert_error_response(response, "VALIDATION_ERROR", 400)
    assert error["detail"] == "movie_id is required"


def test_public_ugc_list_rejects_invalid_movie_id(
    client,
    assert_error_response,
):
    response = client.get("/ugc/?movie_id=abc")

    error = assert_error_response(response, "VALIDATION_ERROR", 400)
    assert error["detail"] == "movie_id must be a number"


def test_public_ugc_list_rejects_negative_movie_id(
    client,
    assert_error_response,
):
    response = client.get("/ugc/?movie_id=-1")

    error = assert_error_response(response, "VALIDATION_ERROR", 400)
    assert error["detail"] == "movie_id must be a positive number"


def test_moderation_list_validates_status(
    client,
    auth_headers,
    assert_error_response,
):
    response = client.get(
        "/ugc/moderation/?status=deleted",
        headers=auth_headers(user_id=99, role="moderator"),
    )

    error = assert_error_response(response, "VALIDATION_ERROR", 400)
    assert error["detail"] == "status must be one of: active, hidden, pending"


def test_moderation_list_rejects_invalid_movie_id(
    client,
    auth_headers,
    assert_error_response,
):
    response = client.get(
        "/ugc/moderation/?movie_id=abc",
        headers=auth_headers(user_id=99, role="moderator"),
    )

    error = assert_error_response(response, "VALIDATION_ERROR", 400)
    assert error["detail"] == "movie_id must be a number"


def test_moderation_list_rejects_negative_movie_id(
    client,
    auth_headers,
    assert_error_response,
):
    response = client.get(
        "/ugc/moderation/?movie_id=-1",
        headers=auth_headers(user_id=99, role="moderator"),
    )

    error = assert_error_response(response, "VALIDATION_ERROR", 400)
    assert error["detail"] == "movie_id must be a positive number"


def test_moderation_list_rejects_invalid_user_id(
    client,
    auth_headers,
    assert_error_response,
):
    response = client.get(
        "/ugc/moderation/?user_id=abc",
        headers=auth_headers(user_id=99, role="moderator"),
    )

    error = assert_error_response(response, "VALIDATION_ERROR", 400)
    assert error["detail"] == "user_id must be a number"


def test_moderation_list_rejects_zero_user_id(
    client,
    auth_headers,
    assert_error_response,
):
    response = client.get(
        "/ugc/moderation/?user_id=0",
        headers=auth_headers(user_id=99, role="moderator"),
    )

    error = assert_error_response(response, "VALIDATION_ERROR", 400)
    assert error["detail"] == "user_id must be a positive number"