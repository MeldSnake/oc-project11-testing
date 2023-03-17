from flask.testing import FlaskClient


def test_valid_login(client: FlaskClient, known_email: str):
    response = client.post(
        "/showSummary",
        data={
            "email": known_email,
        },
    )
    assert response.status_code == 200


def test_unknown_login(client: FlaskClient, unknown_email: str):
    response = client.post(
        "/showSummary",
        data={
            "email": unknown_email,
        },
    )
    assert response.status_code == 403


def test_invalid_login(client: FlaskClient, invalid_email: str):
    response = client.post(
        "/showSummary",
        data={
            "email": invalid_email,
        },
    )
    assert response.status_code == 403
