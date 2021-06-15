from fastapi import Depends
from db.rs_db import BaseRSDatabase, RSDatabase, get_rs_database
from db.models import MoviePrediction, UserPrediction


class RecommendationSystemService:
    def __init__(self, db: BaseRSDatabase):
        self.db = db

    async def get_predictions_for_user(self, user_id: str) -> UserPrediction:
        return self.db.get_predictions_for_user(user_id)

    async def get_predictions_for_movie(self, movie_id: str) -> MoviePrediction:
        return self.db.get_predictions_for_movie(movie_id)


def get_recommendation_service(rs_database: RSDatabase = Depends(get_rs_database)) -> RecommendationSystemService:
    return RecommendationSystemService(rs_database)
