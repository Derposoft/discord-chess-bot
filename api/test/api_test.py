import pytest
import os, http
from api.lib.api import command_line_parse, create_app

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


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


def test_signup(client):
    response = client.post("/signup?user=1&guild=1")
    assert response.status == http.HTTPStatus.CREATED