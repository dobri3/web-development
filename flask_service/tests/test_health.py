def test_health_returns_unified_success_response(client):
    response = client.get("/health")
    body = response.get_json()

    assert response.status_code == 200
    assert body["success"] is True
    assert body["data"] == {"status": "ok"}


def test_unknown_route_returns_unified_error_response(client, assert_error_response):
    response = client.get("/unknown-route")

    assert_error_response(response, "NOT_FOUND", 404)
