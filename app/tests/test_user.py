from services.user_service import create_access_token


def test_registration(test_app):
    payload = {'username': 'test_user_0', 'password': '123'}
    test_app.post("/register", data=payload)
    response = test_app.post("/register", data=payload)
    assert response.status_code == 400


def test_login(test_app):
    payload = {'username': 'test_user', 'password': '123'}
    test_app.post("/register", data=payload)
    response = test_app.get("/login", data=payload)
    assert response.status_code == 200


def test_subscription(test_app):
    access_token = create_access_token(data={"sub": "test_user"})
    print(access_token)
    headers = {'Authorisation': 'Bearer {}'.format(access_token)}
    payload = {'feed_url': 'https://feeds.feedburner.com/tweakers/mixed'}
    test_app.post("/follow-rss", headers=headers, data=payload)
    response = test_app.get("/list-feeds", headers=headers, data=payload)
    assert response.status_code == 200
