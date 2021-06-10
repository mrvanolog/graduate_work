from typing import List

from pydantic import BaseModel


class UserPredictionsRequestData(BaseModel):
    user_id: str


class MoviePredictionsRequestData(BaseModel):
    movie_id: str


class UserPredictions(BaseModel):
    user_id: str
    rec_movie_id: List[str]


class MoviePredictions(BaseModel):
    movie_id: str
    rec_movie_id: List[str]
