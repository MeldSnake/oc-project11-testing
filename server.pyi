from flask import Flask, Response
from typing import TypedDict


class Competition(TypedDict):
    name: str
    date: str
    numberOfPlaces: str


class Club(TypedDict):
    name: str
    email: str
    points: str


app: Flask
clubs: list[Club]
competitions: list[Competition]


def loadClubs() -> list[Club]: ...
def loadCompetitions() -> list[Competition]: ...
def index() -> str: ...
def showSummary() -> str: ...
def book(competition: str, club: str) -> str: ...
def purchasePlaces() -> str: ...
def logout() -> Response: ...
