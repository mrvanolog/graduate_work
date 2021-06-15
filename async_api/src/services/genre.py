from functools import lru_cache
from typing import List

from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from models.genre import Genre
from services.base import BaseService


class GenreService(BaseService):
    index = 'genre'
    model = Genre
    max_size = 1000

    async def list_genres(self) -> List[Genre]:
        """Get all genres.
        """
        body = {
            'size': self.max_size,
            'query': {
                'match_all': {}
            }
        }
        doc = await self.elastic.search(index=self.index, body=body)
        return [self.model(**hit['_source']) for hit in doc['hits']['hits']]


@lru_cache()
def get_genre_service(
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(elastic)
