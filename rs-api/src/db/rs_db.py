import abc

from fastapi import Depends
from sqlalchemy.orm import Session

from db import models
from db.postgres_database import get_db


class BaseRSDatabase(abc.ABC):
    @abc.abstractmethod
    def get_predictions_for_user(self, user_id: str):
        pass

    @abc.abstractmethod
    def get_predictions_for_movie(self, movie_id: str):
        pass


class RSDatabase(BaseRSDatabase):
    def __init__(self, db: Session):
        self.db = db

    def get_predictions_for_user(self, user_id: str):
        return self.db.query(models.UserPrediction).filter(models.UserPrediction.user_id == user_id).first()

    def get_predictions_for_movie(self, movie_id: str):
        return self.db.query(models.MoviePrediction).filter(models.MoviePrediction.movie_id == movie_id).first()


def get_rs_database(postgres_database: Session = Depends(get_db)) -> RSDatabase:
    db = RSDatabase(db=postgres_database)
    return db
