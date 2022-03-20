import pytest
import os, http
from api.lib.api import create_app

@pytest.fixture(scope='session')
def app(pytestconfig):
    args = vars(pytestconfig.option)
    if 'db' not in args:
        filename = 'unit-test.db'
        if os.path.exists(filename):
            os.remove(filename)
        args['db'] = f"sqlite:///{filename}"

    app = create_app(args)
    app.config.update({
        "TESTING": True,
    })

    # other setup can go here

    yield app

    # clean up / reset resources here
    


@pytest.fixture()
def client(app):
    return app.test_client()


def test_signup(client):
    response = client.post("/signup?user=1&guild=1")
    assert response.status_code == http.HTTPStatus.CREATED.value

def test_signup_update(client):
    response = client.post("/signup?user=2&guild=4")
    assert response.status_code == http.HTTPStatus.CREATED.value

    response = client.post("/change-user?user=2&guild=3")
    assert response.status_code == http.HTTPStatus.ACCEPTED.value

    response = client.post("/change-user?user=2&guild=2")
    assert response.status_code == http.HTTPStatus.ACCEPTED.value

def test_signup_get(client):
    response = client.post("/signup?user=3&guild=10")
    assert response.status_code == http.HTTPStatus.CREATED.value

    response = client.get("/get-user?user=3")
    assert response.status_code == http.HTTPStatus.OK.value
    assert response.get_data(as_text=True) == '10'

def test_stockfish_game(client):
    discordID = 5
    response = client.post(f"/signup?user={discordID}&guild=12")
    assert response.status_code == http.HTTPStatus.CREATED.value
    
    response = client.post(f"/new-game/ai?author={discordID}&elo=1500&side=white")
    assert response.status_code == http.HTTPStatus.CREATED.value

    response = client.post(f"/move?self={discordID}&ai=true&move=e2e3")
    assert response.status_code == http.HTTPStatus.ACCEPTED.value

    response = client.post(f"/move?self={discordID}&ai=true&move=f2f3")
    assert response.status_code == http.HTTPStatus.ACCEPTED.value

    response = client.post(f"/move?self={discordID}&ai=true&move=g2g3")
    assert response.status_code == http.HTTPStatus.ACCEPTED.value

    response = client.post(f"/ff?self={discordID}")
    assert response.status_code == http.HTTPStatus.ACCEPTED.value
