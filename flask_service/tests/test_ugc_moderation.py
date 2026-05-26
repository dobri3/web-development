def test_moderator_can_update_ugc_status(
    client,
    auth_headers,
    make_ugc,
):
    ugc = make_ugc(
        text="Review for moderation",
        rating=7,
        movie_id=1,
        user_id=1,
        status="pending",
    )

    response = client.patch(
        f"/ugc/{ugc.id}/status",
        json={"status": "active"},
        headers=auth_headers(user_id=2, role="moderator"),
    )

    body = response.get_json()

    assert response.status_code == 200
    assert body["success"] is True
    assert body["data"]["status"] == "active"


def test_regular_user_cannot_update_ugc_status(
    client,
    auth_headers,
    assert_error_response,
    make_ugc,
):
    ugc = make_ugc(
        text="Review for moderation",
        rating=7,
        movie_id=1,
        user_id=1,
        status="pending",
    )

    response = client.patch(
        f"/ugc/{ugc.id}/status",
        json={"status": "active"},
        headers=auth_headers(user_id=1, role="user"),
    )

    assert_error_response(response, "FORBIDDEN", 403)


def test_moderator_can_list_ugc_with_any_status_by_movie(
    client,
    auth_headers,
    make_ugc,
):
    make_ugc(text="Active movie 1", rating=9, movie_id=1, user_id=1, status="active")
    make_ugc(text="Pending movie 1", rating=8, movie_id=1, user_id=2, status="pending")
    make_ugc(text="Hidden movie 1", rating=7, movie_id=1, user_id=3, status="hidden")
    make_ugc(text="Active movie 2", rating=6, movie_id=2, user_id=1, status="active")

    response = client.get(
        "/ugc/moderation/?movie_id=1",
        headers=auth_headers(user_id=99, role="moderator"),
    )

    body = response.get_json()

    assert response.status_code == 200
    assert body["success"] is True

    data = body["data"]
    assert len(data) == 3
    assert {item["status"] for item in data} == {
        "active",
        "pending",
        "hidden",
    }
    assert {item["movie_id"] for item in data} == {1}


def test_moderator_can_filter_ugc_by_user_and_status(
    client,
    auth_headers,
    make_ugc,
):
    make_ugc(text="User 1 active", rating=9, movie_id=1, user_id=1, status="active")
    make_ugc(text="User 1 hidden", rating=8, movie_id=2, user_id=1, status="hidden")
    make_ugc(text="User 2 hidden", rating=7, movie_id=1, user_id=2, status="hidden")

    response = client.get(
        "/ugc/moderation/?user_id=1&status=hidden",
        headers=auth_headers(user_id=99, role="admin"),
    )

    body = response.get_json()

    assert response.status_code == 200
    assert body["success"] is True

    data = body["data"]
    assert len(data) == 1
    assert data[0]["user_id"] == 1
    assert data[0]["status"] == "hidden"
    assert data[0]["text"] == "User 1 hidden"


def test_regular_user_cannot_list_ugc_for_moderation(
    client,
    auth_headers,
    assert_error_response,
):
    response = client.get(
        "/ugc/moderation/",
        headers=auth_headers(user_id=1, role="user"),
    )

    assert_error_response(response, "FORBIDDEN", 403)