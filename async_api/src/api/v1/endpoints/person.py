from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from api.v1.models.film import FilmShort
from api.v1.models.person import Person
from core.caching import cache
from core.config import DEFAULT_PAGE, MAX_PER_PAGE, PER_PAGE, ELASTIC_MAX_RESULT_WINDOW
from services.film import FilmService, get_film_service
from services.person import PersonService, get_person_service

person_router = APIRouter()


@person_router.get(
    '/search',
    response_model=List[Person],
    summary='Person search',
    description='Text search for persons',
    response_description='Name and movies for a person',
)
@cache(prefix='search_person')
async def person_search(
        query: str = Query(..., min_length=1),
        page: int = Query(DEFAULT_PAGE, gt=0, le=ELASTIC_MAX_RESULT_WINDOW),
        page_size: int = Query(PER_PAGE, gt=0, le=MAX_PER_PAGE),
        person_service: PersonService = Depends(get_person_service)
) -> List[Person]:
    """Get person data matched by 'query' parameter.
    """
    persons = await person_service.search(query, page, page_size)

    if not persons:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='persons not found')

    return [Person(**person.dict()) for person in persons]


@person_router.get(
    '/{person_id}',
    response_model=Person,
    summary='Information about a person',
    description='Full information about a person',
    response_description='Name and movies for a person',
)
@cache(prefix='person_details')
async def person_details(
        person_id: str = Path(..., title='The id of person to get.', min_length=1),
        person_service: PersonService = Depends(get_person_service)
) -> Person:
    """Get person data.
    """
    person = await person_service.get_by_id(person_id)

    if not person:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='person not found')

    return Person(**person.dict())


@person_router.get(
    '/{person_id}/film',
    response_model=List[FilmShort],
    summary='Person movies',
    description='List of movies that a person is a part of',
    response_description='Name and rating of a movie',
)
@cache(prefix='person_films')
async def person_films(
        person_id: str = Path(..., title='The person ID by which we will get all his films.', min_length=1),
        person_service: PersonService = Depends(get_person_service),
        film_service: FilmService = Depends(get_film_service)
) -> List[FilmShort]:
    """Get all movies that person took part.
    """
    person = await person_service.get_by_id(person_id)

    if not person:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='person not found')

    _films = set()
    _films.update(person.actor)
    _films.update(person.writer)
    _films.update(person.director)

    films = [await film_service.get_by_id(f_id) for f_id in _films]
    return [FilmShort(**film.dict()) for film in films]
