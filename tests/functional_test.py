import multiprocessing
import re
from urllib.parse import urljoin

import pytest
from flask import url_for
from selenium import webdriver

LOCALHOST_ROOT_URL = "http://localhost:4000"
DEFAULT_CLUB = {
    "email": "john@simplylift.co",
    "name": "Simply Lift",
}


@pytest.fixture(scope="class")
def browser():
    with webdriver.ChromiumEdge("tests/msedgedriver.exe") as browser:
        yield browser


def run_server():
    import server

    server.app.run("127.0.0.1", port=4000)


@pytest.fixture(scope="session")
def app_server():
    proc = None
    try:
        proc = multiprocessing.Process(
            target=run_server,
        )
        proc.start()
        yield proc
        proc.terminate()
    except Exception as e:
        raise e


class TestFunctional:
    def test_purchase(
        self,
        app_server,
        browser: webdriver.ChromiumEdge,
    ):
        # Access index
        browser.get(urljoin(LOCALHOST_ROOT_URL, url_for("index")))
        form = browser.find_element("tag name", "form")
        email_input = form.find_element("name", "email")
        login_button = form.find_element("tag name", "button")
        # Login using default club
        email_input.send_keys(DEFAULT_CLUB["email"])
        login_button.click()

        # Check redirection
        assert browser.current_url == urljoin(
            LOCALHOST_ROOT_URL, url_for("showSummary")
        ), "Connection failed or not redirected to showSummary"

        # Get the total amount of point from the HTML
        points = int(
            re.search(
                r"Points available: (\d+)",
                browser.find_element("tag name", "body").text,
            ).group(1)
        )
        # While club.points > 0:
        while points > 0:
            competitions = browser.find_elements("tag name", "li")
            for competition in competitions:
                # If competition is available
                if "Book Places" in competition.text:
                    # Reach competition booking page
                    link_booking = competition.find_element("link text", "Book Places")
                    link_booking.click()

                    # Purchase max Places
                    places_input = browser.find_element("id", "places")
                    places_max = int(places_input.get_attribute("max"))
                    places_input.send_keys(str(places_max))
                    points -= places_max
                    browser.find_elements("tag name", "button")[0].click()

                    assert (
                        "Great-booking complete!"
                        in browser.find_element("tag name", "body").text
                    ), "Non validated purchase"
                    break
            html_points = int(
                re.search(
                    r"Points available: (\d+)",
                    browser.find_element("tag name", "body").text,
                ).group(1)
            )
            assert html_points == points, "Invalid points deduction"

        browser.find_element("link text", "Logout").click()

        assert browser.current_url == urljoin(
            LOCALHOST_ROOT_URL, url_for("index")
        ), "Invalid redirection for logout"
