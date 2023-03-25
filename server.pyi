from flask import Flask, Response
from typing import TypedDict
import os


class Competition(TypedDict):
    name: str
    date: str
    numberOfPlaces: str | int


class Club(TypedDict):
    name: str
    email: str
    points: str | int


CLUBS_DATA_FILE: str | bytes | os.PathLike
COMPETITIONS_DATA_FILE: str | bytes | os.PathLike
DATETIME_FORMAT: str

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
