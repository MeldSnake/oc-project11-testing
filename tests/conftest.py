import pytest
import flask
import json
import os
from tempfile import gettempdir
from datetime import datetime, timedelta
from typing import Generator, Any

import server


DEFAULT_CLUBS_DATA: dict[str, list["server.Club"]] = {
    "clubs": [
        {
            "name": "Simply Lift",
            "email": "john@simplylift.co",
            "points": "13",
        },
        {
            "name": "Iron Temple",
            "email": "admin@irontemple.com",
            "points": "25",
        },
        {
            "name": "She Lifts",
            "email": "kate@shelifts.co.uk",
            "points": "12",
        },
    ]
}
DEFAULT_COMPETITIONS_DATA: dict[str, list["server.Competition"]] = {
    "competitions": [
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
        {
            "name": "Late Competition",
            "date": (datetime.now() - timedelta(days=2)).strftime(
                server.DATETIME_FORMAT
            ),
            "numberOfPlaces": "15",
        },
        {
            "name": "Futur Competition",
            "date": (datetime.now() + timedelta(days=2)).strftime(
                server.DATETIME_FORMAT
            ),
            "numberOfPlaces": "2",
        },
        {
            "name": "Futur Competition 2",
            "date": (datetime.now() + timedelta(days=3)).strftime(
                server.DATETIME_FORMAT
            ),
            "numberOfPlaces": "0",
        },
        {
            "name": "Futur Competition 3",
            "date": (datetime.now() + timedelta(days=4)).strftime(
                server.DATETIME_FORMAT
            ),
            "numberOfPlaces": "100",
        },
    ]
}


# "session", "package", "module", "class", "function"
@pytest.fixture(autouse=True)
def patch_database(app, monkeypatch: pytest.MonkeyPatch):
    with monkeypatch.context() as m:
        clubs_file = os.path.join(
            gettempdir(),
            f"clubs_{os.urandom(24).hex()}.json",
        )
        comps_file = os.path.join(
            gettempdir(),
            f"comps_{os.urandom(24).hex()}.json",
        )
        try:
            with open(clubs_file, "w") as fd:
                json.dump(DEFAULT_CLUBS_DATA, fd)
            with open(comps_file, "w") as fd:
                json.dump(DEFAULT_COMPETITIONS_DATA, fd)
            m.setattr(server, "CLUBS_DATA_FILE", clubs_file)
            m.setattr(server, "COMPETITIONS_DATA_FILE", comps_file)
            server.clubs = server.loadClubs()
            server.competitions = server.loadCompetitions()
            yield
        finally:
            os.remove(clubs_file)
            os.remove(comps_file)


@pytest.fixture(scope="session")
def app():
    with server.app.app_context() as app_ctx:
        app_ctx.push()
        yield server.app
        app_ctx.pop()


@pytest.fixture(scope="function")
def client(app: flask.Flask):
    with app.test_client() as client:
        yield client


@pytest.fixture()
def default_clubs():
    return DEFAULT_CLUBS_DATA["clubs"]


@pytest.fixture()
def default_competitions():
    return DEFAULT_COMPETITIONS_DATA["competitions"]


@pytest.fixture()
def clubs():
    return server.clubs


@pytest.fixture()
def first_club(clubs: list["server.Club"]):
    return clubs[0]


@pytest.fixture(params=DEFAULT_CLUBS_DATA["clubs"])
def club(request: pytest.FixtureRequest) -> "server.Club":
    return [x for x in server.clubs if x["email"] == request.param["email"]][0]


@pytest.fixture()
def competitions():
    return server.competitions


@pytest.fixture()
def first_competition(competitions: list["server.Competition"]):
    return competitions[0]


@pytest.fixture(params=DEFAULT_COMPETITIONS_DATA["competitions"])
def competition(request: pytest.FixtureRequest):
    return [x for x in server.competitions if x["name"] == request.param["name"]][0]


@pytest.fixture()
def future_competitions(competitions: list["server.Competition"]):
    return [
        x
        for x in competitions
        if datetime.strptime(x["date"], server.DATETIME_FORMAT) > datetime.now()
    ]


@pytest.fixture(params=DEFAULT_COMPETITIONS_DATA["competitions"][3:])
def future_competition_list(request: pytest.FixtureRequest):
    return [x for x in server.competitions if x["name"] == request.param["name"]][0]


@pytest.fixture()
def first_future_competition(
    future_competitions: list["server.Competition"],
) -> "server.Competition":
    return future_competitions[0]


@pytest.fixture()
def past_competitions(competitions: list["server.Competition"]):
    return [
        x
        for x in competitions
        if datetime.strptime(x["date"], server.DATETIME_FORMAT) <= datetime.now()
    ]


@pytest.fixture(params=DEFAULT_COMPETITIONS_DATA["competitions"][:3])
def past_competition_list(request: pytest.FixtureRequest):
    return [x for x in server.competitions if x["name"] == request.param["name"]][0]


@pytest.fixture()
def first_past_competition(
    past_competitions: list["server.Competition"],
) -> "server.Competition":
    return past_competitions[0]


@pytest.fixture(params=["alice", "", "test@example.com"])
def invalid_mail(request: pytest.FixtureRequest) -> str:
    return request.param
