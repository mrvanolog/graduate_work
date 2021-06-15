from fastapi import APIRouter, Depends

from api.v1.schemas import MoviePredictionsRequestData, UserPredictionsRequestData, MoviePredictions, UserPredictions
from services.rs_service import RecommendationSystemService, get_recommendation_service

router = APIRouter()


@router.get('/user', response_model=UserPredictions)
async def user_predictions(
        request_data: UserPredictionsRequestData,
        rs_service: RecommendationSystemService = Depends(get_recommendation_service)) -> UserPredictions:
    predictions = await rs_service.get_predictions_for_user(request_data.user_id)
    response_predictions = UserPredictions(**predictions.dict())
    return response_predictions


@router.get('/movie', response_model=MoviePredictions)
async def movie_predictions(request_data: MoviePredictionsRequestData,
                            rs_service: RecommendationSystemService = Depends(get_recommendation_service)):
    predictions = await rs_service.get_predictions_for_user(request_data.movie_id)
    response_predictions = MoviePredictions(**predictions.dict())
    return response_predictions
