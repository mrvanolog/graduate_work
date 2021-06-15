from functools import lru_cache
from typing import List, Optional

from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from models.film import Film
from models.misc import SortOrder
from services.base import BaseService


class FilmService(BaseService):
    index = 'movies'
    model = Film

    async def get_sorted(
            self,
            sort_by: str,
            page: int,
            page_size: int,
            genre: Optional[str]
    ) -> Optional[List[Film]]:
        """Get list of films sorted by a parameter.
        """
        return await self._get_sorted_films_from_elastic(sort_by, page, page_size, genre)


    async def _get_sorted_films_from_elastic(
            self,
            sort_by: str,
            page: int,
            page_size: int,
            genre: Optional[str]
    ) -> Optional[List[Film]]:

        sort_type, sort_by = SortOrder.get_sort_params(sort_by)
        body = {
            'size': page_size,
            'from': (page - 1) * page_size,
            'sort': [
                {
                    sort_by: sort_type
                }
            ]
        }
        if genre is not None:
            query = {
                'query': {
                    'bool': {
                        'must': [
                            {
                                'match_all': {}
                            },
                            {
                                'nested': {
                                    'path': 'genres',
                                    'query': {
                                        'bool': {
                                            'must': [
                                                {
                                                    'match': {
                                                        'genres.name': genre
                                                    }
                                                }
                                            ]
                                        }
                                    }
                                }
                            }
                        ]
                    }
                }
            }
            body.update(query)

        doc = await self.elastic.search(index=self.index, body=body)
        return [self.model(**hit['_source']) for hit in doc['hits']['hits']]

    async def get_search(
            self,
            query: str,
            page: int,
            page_size: int
    ) -> Optional[List[Film]]:
        """Get list of films that have query phrase in either title or description.
        """
        return await self._get_film_search_from_elastic(query, page, page_size)

    async def _get_film_search_from_elastic(
            self,
            query: str,
            page: int,
            page_size: int
    ) -> Optional[List[Film]]:

        body = {
            'size': page_size,
            'from': (page - 1) * page_size,
            'query': {
                'multi_match': {
                    'query': query,
                    'fuzziness': 'auto',
                    'fields': [
                        'title^5',
                        'description^4'
                    ],
                }
            }
        }

        doc = await self.elastic.search(index=self.index, body=body)
        return [self.model(**hit['_source']) for hit in doc['hits']['hits']]



@lru_cache()
def get_film_service(
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(elastic)
