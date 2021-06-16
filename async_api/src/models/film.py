from typing import List, Optional

import orjson
from pydantic import BaseModel


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
    type: Optional[str]
    genres: List[Genre]
    actors: List[FilmPerson]
    writers: List[FilmPerson]
    directors: List[FilmPerson]

    class Config:
        # replacing standard json process by a faster one
        json_loads = orjson.loads
        json_dumps = orjson.dumps
