from dataclasses import dataclass
from typing import List

from multidict import CIMultiDictProxy
from pydantic import BaseModel


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int


class Person(BaseModel):
    uuid: str
    full_name: str
    actor: List[str]
    writer: List[str]
    director: List[str]


class FilmPerson(BaseModel):
    uuid: str
    full_name: str


class Genre(BaseModel):
    uuid: str
    name: str


class Film(BaseModel):
    uuid: str
    title: str
    description: str
    imdb_rating: float
    genres: List[Genre]
    actors: List[FilmPerson]
    writers: List[FilmPerson]
    directors: List[FilmPerson]
