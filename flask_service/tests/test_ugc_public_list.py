def test_list_active_ugc_returns_only_active_items(client, make_ugc):
    make_ugc(
        text="Visible review",
        rating=9,
        movie_id=1,
        user_id=1,
        status="active",
    )
    make_ugc(
        text="Pending review",
        rating=8,
        movie_id=1,
        user_id=1,
        status="pending",
    )

    response = client.get("/ugc/?movie_id=1")
    body = response.get_json()

    assert response.status_code == 200
    assert body["success"] is True

    data = body["data"]
    assert len(data) == 1
    assert data[0]["text"] == "Visible review"
    assert data[0]["status"] == "active"