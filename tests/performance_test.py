from locust import HttpUser, task

from server import loadClubs, loadCompetitions


class PerformanceTest(HttpUser):
    """
    locust -f tests/performance_test.py
    url: http://192.168.1.64:8089/
    host: http://127.0.0.1:5000
    """

    club = loadClubs()[0]
    competition = loadCompetitions()[1]

    def on_start(self):
        self.client.post(
            "/showSummary",
            {
                "email": self.club["email"],
            },
        )

    @task
    def reconnect(self):
        self.client.post(
            "/showSummary",
            {
                "email": self.club["email"],
            },
        )

    @task
    def index(self):
        self.client.get("/")

    @task
    def book(self):
        self.client.get("/book/" + self.competition["name"] + "/" + self.club["name"])

    @task
    def purchase_places(self):
        self.client.post(
            "/purchasePlaces",
            {
                "club": self.club["name"],
                "competition": self.competition["name"],
                "places": "1",
            },
        )

    @task
    def on_stop(self):
        self.client.get("/logout")