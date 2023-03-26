import pytest
from flask import url_for
from flask.testing import FlaskClient
import server
import datetime
from urllib.parse import urlparse


def compare_clubs(
    left: list["server.Club"],
    right: list["server.Club"],
):
    if len(left) != len(right):
        return False
    for i in range(len(left)):
        a = left[i]
        b = right[i]
        if a != b or not (
            a["name"] == b["name"]
            and a["email"] == b["email"]
            and a["points"] == b["points"]
        ):
            return False
    return True


def compare_competitions(
    left: list["server.Competition"],
    right: list["server.Competition"],
):
    if len(left) != len(right):
        return False
    for i in range(len(left)):
        a = left[i]
        b = right[i]
        if a != b or not (
            a["name"] == b["name"]
            and a["date"] == b["date"]
            and int(a["numberOfPlaces"]) == int(b["numberOfPlaces"])
        ):
            return False
    return True


def compare_list(
    left,
    right,
):
    if "points" in left[0] and "points" in right[0]:
        return compare_clubs(left, right)
    return compare_competitions(left, right)


class TestDatabase:
    """Test the basic operations for the database, loading and saving"""

    def test_load_clubs(self, default_clubs: list["server.Club"]):
        """Test wether the loading function does work and obtain the expected results"""
        clubs = server.loadClubs()

        assert compare_list(
            clubs, default_clubs
        ), "Invalid clubs data loaded in the server"

    def test_load_competitions(self, default_competitions: list["server.Competition"]):
        """Test wether the loading function does work and obtain the expected results"""
        comps = server.loadCompetitions()

        assert compare_list(
            comps,
            default_competitions,
        ), "Invalid competitions data loaded in the server"

    def test_competition_data(self, competition: "server.Competition"):
        assert isinstance(
            competition["numberOfPlaces"], (str, int)
        ), "Invalid type of numberOfPlaces, shall be either an int or a str"
        if isinstance(competition["numberOfPlaces"], str):
            assert competition[
                "numberOfPlaces"
            ].isdecimal(), (
                "Invalid value of numberOfPlaces, shall be digits only or an int"
            )
        try:
            date_dt = datetime.datetime.strptime(
                competition["date"],
                server.DATETIME_FORMAT,
            )
        except ValueError:
            raise AssertionError("The date value does not match the expected format")


class TestIndexRoute:
    """Test the /index route"""

    def test_index(self, client: FlaskClient):
        """Test the status code of the index route"""
        response = client.get(url_for("index"))
        html = response.get_data(True)

        assert response.status_code == 200, "Invalid status code for index"
        assert "Welcome to the GUDLFT Registration Portal!" in html
        assert "Please enter your secretary email to continue:" in html


class TestPointsDisplayRoute:
    """Test the /pointsDisplay route"""

    def test_points_display(self, client: FlaskClient):
        """Test the status of the pointsDisplay route"""
        response = client.get(url_for("pointsDisplay"))
        html = response.get_data(True)

        assert response.status_code == 200, "Invalid status code for points display"
        assert "Clubs list | GUDLFT" in html


class TestShowSummaryRoute:
    """Test the /showSummary route"""

    def test_show_summary_login(self, client: FlaskClient, first_club: "server.Club"):
        """Test that a user can access it's summary"""
        response = client.post(
            url_for("showSummary"),
            data={
                "email": first_club["email"],
            },
        )
        html = response.get_data(True)

        assert (
            response.status_code == 200
        ), "Unable to access summary using a valid email"
        assert (
            f"Welcome, {first_club['email']}" in html
        ), "Invalid summary shown, missing welcome club"
        assert (
            f"Points available: {first_club['points']}"
        ), "Invalid number of points shown"

    def test_show_summary_no_post(self, client: FlaskClient):
        """Test the route with no data in the POST body"""
        response = client.post(
            url_for("showSummary"),
        )

        assert (
            response.status_code == 400
        ), "Invalid redirection status code, this sould be 302"

    def test_show_summary_invalid_mail(
        self,
        client: FlaskClient,
        invalid_mail: str,
    ):
        """Test the route with a mail that does not exists within the DB"""
        response = client.post(
            url_for("showSummary"),
            data={
                "email": invalid_mail,
            },
        )

        assert (
            response.status_code == 302
        ), "Invalid redirection status code, this sould be 302"
        assert urlparse(response.location).path == url_for(
            "index"
        ), "Invalid redirection URL, should redirect to index url"


def check_competition_date(competition: "server.Competition"):
    """
    Determine wether the competition is in the future or past from now
    Return -1 on past, 1 on future
    """
    date_dt = datetime.datetime.strptime(
        competition["date"],
        server.DATETIME_FORMAT,
    )
    if date_dt <= datetime.datetime.now():
        return -1
    return 1


class TestBookRoute:
    """Test the /book route"""

    def test_book_future_competition(
        self,
        client: FlaskClient,
        first_future_competition: "server.Competition",
        first_club: "server.Club",
    ):
        """Test if the route for a futur competition return the correct html"""
        response = client.get(
            url_for(
                "book",
                competition=first_future_competition["name"],
                club=first_club["name"],
            ),
        )

        assert response.status_code == 200
        assert (
            f"Places available: {first_future_competition['numberOfPlaces']}"
            in response.get_data(True)
        ), "Invalid html content returned when reaching the booking page"


class TestPurchasePlacesRoute:
    """Test the /purchasePlaces route"""

    def test_purchase_valid(
        self,
        client: FlaskClient,
        first_club: "server.Club",
        first_future_competition: "server.Competition",
    ):
        """Test if a club can purchase places using it's point,
        if the purchase is validated and the value deducted from it's points"""
        quantity = 1
        club_points = int(first_club["points"])
        competition_places = int(first_future_competition["numberOfPlaces"])
        new_points = club_points - quantity
        response = client.post(
            url_for("purchasePlaces"),
            data={
                "competition": first_future_competition["name"],
                "club": first_club["name"],
                "places": quantity,
            },
        )
        html = response.get_data(True)
        server_club = [x for x in server.clubs if x["name"] == first_club["name"]][0]
        server_competition = [x for x in server.competitions if x["name"] == first_future_competition["name"]][0]

        assert response.status_code == 200, "Invalid code response"
        assert "Great-booking complete!" in html, "Booking not validated"
        assert int(server_club["points"]) == new_points, "Invalid, points not deducted on club"
        assert int(server_competition["numberOfPlaces"]) == competition_places, "Invalid, points not deducted on competition"

    def test_purchase_negative(
        self,
        client: FlaskClient,
        first_club: "server.Club",
        first_future_competition: "server.Competition",
    ):
        """Test if a negative purchase influence a purchase"""
        club_points = int(first_club["points"])
        competition_places = int(first_future_competition["numberOfPlaces"])
        quantity = -1
        response = client.post(
            url_for("purchasePlaces"),
            data={
                "competition": first_future_competition["name"],
                "club": first_club["name"],
                "places": quantity,
            },
        )
        server_club = [x for x in server.clubs if x["name"] == first_club["name"]][0]
        server_competition = [x for x in server.competitions if x["name"] == first_future_competition["name"]][0]

        assert int(server_club["points"]) == club_points, "Invalid, points have been changed on club"
        assert int(server_competition["numberOfPlaces"]) == competition_places, "Invalid, points have been changed on competition"

    def test_purchase_more_than_twleve(
        self,
        client: FlaskClient,
        first_club: "server.Club",
        first_future_competition: "server.Competition",
    ):
        """Test if a user can use more than twelve points"""
        club_points = int(first_club["points"])
        quantity = 13
        _ = client.post(
            url_for("purchasePlaces"),
            data={
                "competition": first_future_competition["name"],
                "club": first_club["name"],
                "places": quantity,
            },
        )
        server_club = [x for x in server.clubs if x["name"] == first_club["name"]][0]
        server_competition = [x for x in server.competitions if x["name"] == first_future_competition["name"]][0]

        assert int(server_club["points"]) == club_points, "Invalid, points have been changed on club"
        assert int(server_competition["numberOfPlaces"]) == competition_places, "Invalid, points have been changed on competition"

    def test_purchase_invalid_club(
        self,
        client: FlaskClient,
        first_future_competition: "server.Competition",
    ):
        competition_places = int(first_future_competition["numberOfPlaces"])
        _ = client.post(
            url_for("purchasePlaces"),
            data={
                "competition": first_future_competition["name"],
                "club": "noname",
                "places": 1,
            },
        )
        server_competition = [x for x in server.competitions if x["name"] == first_future_competition["name"]][0]

        assert int(server_competition["numberOfPlaces"]) == competition_places, "Invalid, points have been changed on competition"

    def test_purchase_invalid_competition(
        self,
        client: FlaskClient,
        first_club: "server.Club",
    ):
        club_points = int(first_club["points"])
        _ = client.post(
            url_for("purchasePlaces"),
            data={
                "competition": "noname",
                "club": first_club["name"],
                "places": 1,
            },
        )
        server_club = [x for x in server.clubs if x["name"] == first_club["name"]][0]

        assert server_club["points"] == club_points, "Invalid, points have been changed"


class TestLogout:
    """Test the /logout route"""

    def test_logout(self, client: FlaskClient):
        response = client.get(url_for("logout"))

        assert response.status_code == 302, "Logout not redirecting"
        assert urlparse(response.location).path == url_for(
            "index"
        ), "Not redirecting to index"
