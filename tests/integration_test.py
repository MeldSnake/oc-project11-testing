from flask import url_for
from flask.testing import FlaskClient

import server


class TestIntegration:
    def test_integration(
        self,
        client: FlaskClient,
        first_club: "server.Club",
        first_future_competition: "server.Competition",
    ):
        """Integration test for all routes"""
        # Access index page
        response = client.get(url_for("index"))
        html = response.get_data(True)

        assert (
            response.status_code == 200
        ), "Unable to reach index correctly"
        assert (
            "GUDLFT Registration" in html
            and "Please enter your secretary email to continue:" in html
        ), "Invalid index page provided"

        # View points display

        # Connect to club with email
        response = client.post(
            url_for("showSummary"),
            data={
                "email": first_club["email"],
            },
        )
        html = response.get_data(True)

        assert (
            response.status_code == 200
        ), f"Unable to reach login with email {first_club['email']}"
        assert (
            "Summary | GUDLFT Registration" in html
        ), "Invalid summary page provided"
        assert (
            f"Welcome, {first_club['email']}" in html
        ), "Invalid club welcoming message"

        # View competition page for booking
        response = client.get(
            url_for(
                "book",
                competition=first_future_competition["name"],
                club=first_club["name"],
            ),
        )
        html = response.get_data(True)

        assert (
            response.status_code == 200
        ), "Unable to reach Booking page for competition"
        assert (
            f"Booking for {first_future_competition['name']} || GUDLFT" in html
        ), "Invalid booking page provided"
        assert (
            f"Places available: {first_future_competition['numberOfPlaces']}" in html
        ), "Invalid data within the page"

        # Purchase 1 place from the competition using the current club
        response = client.post(
            url_for("purchasePlaces"),
            data={
                "competition": first_future_competition["name"],
                "club": first_club["name"],
                "places": 1,
            },
        )
        html = response.get_data(True)

        assert (
            response.status_code == 200
        ), "Unable to reach purchase correctly"
        assert (
            "Great-booking complete!" in html
        ), "No purchase validation message found"
        assert (
            f"Welcome, {first_club['email']}"
        ), "Invalid club represented on the purchase result page"

        # Logout
        response = client.get(
            url_for('logout'),
        )

        assert (
            response.status_code == 302
        ), "Invalid logout redirection status"
        assert (
            response.location == url_for("index")
        ), "Invalid logout redirection location"
