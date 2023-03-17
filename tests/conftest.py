import pytest
from flask import Flask
import server


@pytest.fixture()
def patch_clubs(monkeypatch: pytest.MonkeyPatch):
    def loadClubs():
        return [
            {
                "name": "Simply Lift",
                "email": "john@simplylift.co",
                "points": "13",
            },
            {
                "name": "Iron Temple",
                "email": "admin@irontemple.com",
                "points": "4",
            },
            {
                "name": "She Lifts",
                "email": "kate@shelifts.co.uk",
                "points": "12",
            },
        ]
    with monkeypatch.context() as m:
        m.setattr("server.loadClubs", loadClubs)
        yield


@pytest.fixture()
def patch_competitions(monkeypatch: pytest.MonkeyPatch):
    def loadCompetitions():
        return [
            {
                "name": "Spring Festival",
                "date": "2020-03-27 10:00:00",
                "numberOfPlaces": "25",
            },
            {
                "name": "Fall Classic",
                "date": "2020-10-22 13:30:00",
                "numberOfPlaces": "13",
            },
        ]
    with monkeypatch.context() as m:
        m.setattr("server.loadClubs", loadCompetitions)
        yield


@pytest.mark.usefixtures('patch_clubs')
@pytest.mark.usefixtures('patch_competitions')
@pytest.fixture()
def app():
    return server.app


@pytest.fixture()
def client(app: Flask):
    return app.test_client()


@pytest.fixture()
def client_runner(app: Flask):
    return app.test_cli_runner()
