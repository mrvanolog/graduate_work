from fastapi import APIRouter, Depends, Security

from api.v1.schemas import (MoviePredictionsRequestData,
                            UserPredictionsRequestData, MoviePredictions,
                            UserPredictions)
from api.v1.utils import auth
from services.rs_service import (RecommendationSystemService,
                                 get_recommendation_service)

router = APIRouter()


@router.get('/user', response_model=UserPredictions)
async def user_predictions(
        request_data: UserPredictionsRequestData,
        rs_service: RecommendationSystemService = Depends(
            get_recommendation_service),
        user_id: str = Security(auth)) -> UserPredictions:
    predictions = await rs_service.get_predictions_for_user(
        request_data.user_id)
    response_predictions = UserPredictions(**predictions.dict())
    return response_predictions


@router.post('/movie', response_model=MoviePredictions)
async def movie_predictions(request_data: MoviePredictionsRequestData,
                            rs_service: RecommendationSystemService =
                            Depends(get_recommendation_service),
                            user_id: str = Security(auth)):
    predictions = await rs_service.get_predictions_for_movie(
        request_data.movie_id)
    response_predictions = MoviePredictions(**predictions.dict())
    return response_predictions
