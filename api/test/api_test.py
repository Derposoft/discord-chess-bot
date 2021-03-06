import pytest
import os, http
from api.lib.api import create_app
import logging

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def app(pytestconfig):
    args = vars(pytestconfig.option)
    if "db" not in args:
        filename = "unit-test.db"
        if os.path.exists(filename):
            os.remove(filename)
        args["db"] = f"sqlite:///{filename}"

    app = create_app(args)
    app.config.update(
        {
            "TESTING": True,
        }
    )

    # other setup can go here

    yield app

    # clean up / reset resources here


@pytest.fixture()
def client(app):
    return app.test_client()


def test_signup(client):
    response = client.post("/signup?user=1&guild=1")
    logger.info(f"Response: {response.get_data(as_text=True)}")
    assert response.status_code == http.HTTPStatus.CREATED.value


def test_signup_update(client):
    response = client.post("/signup?user=2&guild=4")
    logger.info(f"Response: {response.get_data(as_text=True)}")
    assert response.status_code == http.HTTPStatus.CREATED.value

    response = client.post("/change-user?user=2&guild=3")
    logger.info(f"Response: {response.get_data(as_text=True)}")
    assert response.status_code == http.HTTPStatus.ACCEPTED.value

    response = client.post("/change-user?user=2&guild=2")
    logger.info(f"Response: {response.get_data(as_text=True)}")
    assert response.status_code == http.HTTPStatus.ACCEPTED.value


def test_signup_get(client):
    response = client.post("/signup?user=3&guild=10")
    logger.info(f"Response: {response.get_data(as_text=True)}")
    assert response.status_code == http.HTTPStatus.CREATED.value

    response = client.get("/get-user?user=3")
    assert response.status_code == http.HTTPStatus.OK.value
    assert response.get_data(as_text=True) == "10"


def test_stockfish_game(client):
    discordID = 5
    response = client.post(f"/signup?user={discordID}&guild=12")
    logger.info(f"Response: {response.get_data(as_text=True)}")
    assert response.status_code == http.HTTPStatus.CREATED.value

    response = client.post(f"/new-game/ai?author={discordID}&elo=1500&side=white")
    logger.info(f"Response: {response.get_data(as_text=True)}")
    assert response.status_code == http.HTTPStatus.CREATED.value

    response = client.post(f"/move?self={discordID}&ai=true&move=e2e3")
    logger.info(f"Response: {response.get_data(as_text=True)}")
    assert response.status_code == http.HTTPStatus.ACCEPTED.value

    response = client.post(f"/move?self={discordID}&ai=true&move=f2f3")
    logger.info(f"Response: {response.get_data(as_text=True)}")
    assert response.status_code == http.HTTPStatus.ACCEPTED.value

    response = client.post(f"/move?self={discordID}&ai=true&move=g2g3")
    logger.info(f"Response: {response.get_data(as_text=True)}")
    assert response.status_code == http.HTTPStatus.ACCEPTED.value

    response = client.post(f"/ff?self={discordID}")
    logger.info(f"Response: {response.get_data(as_text=True)}")
    assert response.status_code == http.HTTPStatus.ACCEPTED.value


def test_pvp_game(client):
    player1_discordID = 6
    response = client.post(f"/signup?user={player1_discordID}&guild=ABC")
    logger.info(f"Response: {response.get_data(as_text=True)}")
    assert response.status_code == http.HTTPStatus.CREATED.value

    player2_discordID = 7
    player2_discordGuildID = "DEF"
    response = client.post(
        f"/signup?user={player2_discordID}&guild={player2_discordGuildID}"
    )
    logger.info(f"Response: {response.get_data(as_text=True)}")
    assert response.status_code == http.HTTPStatus.CREATED.value

    response = client.post(
        f"/new-game/pvp?author={player1_discordID}&invitee={player2_discordID}&side=black"
    )
    logger.info(f"Response: {response.get_data(as_text=True)}")
    assert response.status_code == http.HTTPStatus.CREATED.value

    response = client.post(f"/move?self={player2_discordID}&move=e2e3")
    logger.info(f"Response: {response.get_data(as_text=True)}")
    assert response.status_code == http.HTTPStatus.ACCEPTED.value

    response = client.post(f"/move?self={player2_discordID}&move=e2e3")
    logger.info(f"Response: {response.get_data(as_text=True)}")
    assert response.status_code == http.HTTPStatus.BAD_REQUEST.value

    response = client.post(f"/move?self={player1_discordID}&move=e2e3")
    logger.info(f"Response: {response.get_data(as_text=True)}")
    assert response.status_code == http.HTTPStatus.BAD_REQUEST.value

    response = client.post(f"/move?self={player1_discordID}&move=e7e6")
    logger.info(f"Response: {response.get_data(as_text=True)}")
    assert response.status_code == http.HTTPStatus.ACCEPTED.value

    response = client.post(f"/move?self={player1_discordID}&move=g2g3")
    logger.info(f"Response: {response.get_data(as_text=True)}")
    assert response.status_code == http.HTTPStatus.BAD_REQUEST.value

    response = client.post(f"/move?self={player2_discordGuildID}&move=f2f3")
    logger.info(f"Response: {response.get_data(as_text=True)}")
    assert response.status_code == http.HTTPStatus.ACCEPTED.value

    response = client.post(f"/move?self={player1_discordID}&move=b8c6")
    logger.info(f"Response: {response.get_data(as_text=True)}")
    assert response.status_code == http.HTTPStatus.ACCEPTED.value

    response = client.post(f"/ff?self={player2_discordID}")
    logger.info(f"Response: {response.get_data(as_text=True)}")
    assert response.status_code == http.HTTPStatus.ACCEPTED.value


def test_cheat(client):
    player1_discordID = 8
    response = client.post(f"/signup?user={player1_discordID}&guild=DERP")
    logger.info(f"Response: {response.get_data(as_text=True)}")
    assert response.status_code == http.HTTPStatus.CREATED.value

    player2_discordID = 9
    response = client.post(f"/signup?user={player2_discordID}&guild=DERP2")
    logger.info(f"Response: {response.get_data(as_text=True)}")
    assert response.status_code == http.HTTPStatus.CREATED.value

    response = client.post(
        f"/new-game/pvp?author={player1_discordID}&invitee={player2_discordID}&side=white"
    )
    logger.info(f"Response: {response.get_data(as_text=True)}")
    assert response.status_code == http.HTTPStatus.CREATED.value

    response = client.post(f"/move?self={player1_discordID}&move=b1c3")
    logger.info(f"Response: {response.get_data(as_text=True)}")
    assert response.status_code == http.HTTPStatus.ACCEPTED.value

    response = client.post(f"/move?self={player2_discordID}&move=b8c6")
    logger.info(f"Response: {response.get_data(as_text=True)}")
    assert response.status_code == http.HTTPStatus.ACCEPTED.value

    response = client.post(f"/move?self={player1_discordID}&move=f2f4")
    logger.info(f"Response: {response.get_data(as_text=True)}")
    assert response.status_code == http.HTTPStatus.ACCEPTED.value

    response = client.post(f"/move?self={player2_discordID}&move=e7e6")
    logger.info(f"Response: {response.get_data(as_text=True)}")
    assert response.status_code == http.HTTPStatus.ACCEPTED.value

    response = client.get(f"/cheat?self={player1_discordID}")
    logger.info(f"Response: {response.get_data(as_text=True)}")
    assert response.status_code == http.HTTPStatus.OK.value


def test_pvp_game_no_signup(client):
    player1_discordID = 240
    player2_discordID = 241
    response = client.post(
        f"/new-game/pvp?author={player1_discordID}&invitee={player2_discordID}&side=white"
    )
    logger.info(f"Response: {response.get_data(as_text=True)}")
    assert response.status_code == http.HTTPStatus.CREATED.value

    response = client.post(f"/move?self={player1_discordID}&move=e2e4")
    logger.info(f"Response: {response.get_data(as_text=True)}")
    assert response.status_code == http.HTTPStatus.ACCEPTED.value

    response = client.post(f"/move?self={player2_discordID}&move=e7e5")
    logger.info(f"Response: {response.get_data(as_text=True)}")
    assert response.status_code == http.HTTPStatus.ACCEPTED.value

    response = client.post(f"/move?self={player1_discordID}&move=f1c4")
    logger.info(f"Response: {response.get_data(as_text=True)}")
    assert response.status_code == http.HTTPStatus.ACCEPTED.value

    response = client.post(f"/move?self={player2_discordID}&move=d7d6")
    logger.info(f"Response: {response.get_data(as_text=True)}")
    assert response.status_code == http.HTTPStatus.ACCEPTED.value

    response = client.post(f"/move?self={player1_discordID}&move=d1f3")
    logger.info(f"Response: {response.get_data(as_text=True)}")
    assert response.status_code == http.HTTPStatus.ACCEPTED.value

    response = client.post(f"/move?self={player2_discordID}&move=b8c6")
    logger.info(f"Response: {response.get_data(as_text=True)}")
    assert response.status_code == http.HTTPStatus.ACCEPTED.value

    response = client.post(f"/move?self={player1_discordID}&move=f3f7")
    logger.info(f"Response: {response.get_data(as_text=True)}")
    assert response.status_code == http.HTTPStatus.ACCEPTED.value

    response = client.post(f"/move?self={player2_discordID}&move=a7a6")
    logger.info(f"Response: {response.get_data(as_text=True)}")
    assert response.status_code == http.HTTPStatus.BAD_REQUEST.value
