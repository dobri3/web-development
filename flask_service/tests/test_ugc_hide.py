def test_user_can_hide_own_ugc(
    client,
    auth_headers,
    make_ugc,
):
    ugc = make_ugc(
        text="My review",
        rating=7,
        movie_id=1,
        user_id=1,
        status="active",
    )

    response = client.patch(
        f"/ugc/{ugc.id}/hide",
        headers=auth_headers(user_id=1, role="user"),
    )

    body = response.get_json()

    assert response.status_code == 200
    assert body["success"] is True
    assert body["data"]["status"] == "hidden"


def test_user_cannot_hide_other_users_ugc(
    client,
    auth_headers,
    assert_error_response,
    make_ugc,
):
    ugc = make_ugc(
        text="Other user review",
        rating=7,
        movie_id=1,
        user_id=2,
        status="active",
    )

    response = client.patch(
        f"/ugc/{ugc.id}/hide",
        headers=auth_headers(user_id=1, role="user"),
    )

    assert_error_response(response, "FORBIDDEN", 403)