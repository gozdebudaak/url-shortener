def create(client, url="https://example.com/some/long/path"):
    return client.post("/api/links", json={"target_url": url})


def test_create_link(client):
    response = create(client)
    assert response.status_code == 201
    body = response.json()
    assert len(body["code"]) == 7
    assert body["target_url"] == "https://example.com/some/long/path"
    assert body["clicks"] == 0


def test_create_link_rejects_invalid_url(client):
    response = create(client, url="not-a-url")
    assert response.status_code == 422


def test_create_link_codes_are_unique(client):
    codes = {create(client).json()["code"] for _ in range(20)}
    assert len(codes) == 20


def test_redirect_and_count_clicks(client):
    code = create(client).json()["code"]

    for _ in range(3):
        response = client.get(f"/r/{code}", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "https://example.com/some/long/path"

    links = client.get("/api/links").json()
    assert links[0]["clicks"] == 3


def test_redirect_unknown_code(client):
    response = client.get("/r/nope123", follow_redirects=False)
    assert response.status_code == 404


def test_list_links_newest_first(client):
    first = create(client, "https://example.com/1").json()["code"]
    second = create(client, "https://example.com/2").json()["code"]

    codes = [link["code"] for link in client.get("/api/links").json()]
    assert codes == [second, first]


def test_list_links_limit(client):
    for i in range(5):
        create(client, f"https://example.com/{i}")
    assert len(client.get("/api/links?limit=2").json()) == 2
