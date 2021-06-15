from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, status

from api.v1.models.genre import GenreShort
from core.caching import cache
from services.genre import GenreService, get_genre_service

genre_router = APIRouter()


@genre_router.get(
    '/',
    response_model=List[GenreShort],
    summary='All genres',
    description='All genres',
    response_description='Genre name',
)
@cache(prefix='list_genre')
async def genre_list(
        genre_service: GenreService = Depends(get_genre_service)
) -> List[GenreShort]:
    """Get all genres.
    """
    genres = await genre_service.list_genres()

    if not genres:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='genres not found')

    return [GenreShort(**genre.dict()) for genre in genres]


@genre_router.get(
    '/{genre_id}',
    response_model=GenreShort,
    summary='Information about a genre',
    description='Full information about a genre',
    response_description='Genre name',
)
@cache(prefix='genre_details')
async def genre_details(
        genre_id: str = Path(..., title='The id of genre to get.', min_length=2, max_length=255),
        genre_service: GenreService = Depends(get_genre_service)
) -> GenreShort:
    """Get datailed info about a particular genre.
    """
    genre = await genre_service.get_by_id(genre_id)

    if not genre:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='genre not found')

    return GenreShort(**genre.dict())
