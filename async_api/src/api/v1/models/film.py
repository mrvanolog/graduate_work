from typing import List

from pydantic import BaseModel

from models.film import FilmPerson, Genre


class FilmShort(BaseModel):
    """Used in:
    - Popular films on the main page
    - Genre and popular movies in it
    - Search by movies
    - Films by person
    """
    uuid: str
    title: str
    imdb_rating: float


class FilmDetail(BaseModel):
    """Used by:
    - Detailed information about a movie
    """
    uuid: str
    title: str
    imdb_rating: float
    description: str
    genres: List[Genre]
    actors: List[FilmPerson]
    writers: List[FilmPerson]
    directors: List[FilmPerson]
