from fastapi import APIRouter

from api.v1.endpoints.film import film_router
from api.v1.endpoints.genre import genre_router
from api.v1.endpoints.person import person_router

api_router = APIRouter()
api_router.include_router(film_router, prefix='/film', tags=['Movies'])
api_router.include_router(person_router, prefix='/person', tags=['Person'])
api_router.include_router(genre_router, prefix='/genre', tags=['Genre'])
