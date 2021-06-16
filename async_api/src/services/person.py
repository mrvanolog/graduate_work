from functools import lru_cache
from typing import List, Optional

from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from models.person import Person
from services.base import BaseService


class PersonService(BaseService):
    index = 'person'
    model = Person

    async def search(
            self,
            query: str,
            page: int,
            page_size: int
    ) -> Optional[List[Person]]:
        """Get list of person that have query phrase in full_name.
        """
        return await self._get_person_search_from_elastic(query, page, page_size)

    async def _get_person_search_from_elastic(
            self,
            query: str,
            page: int,
            page_size: int
    ) -> Optional[List[Person]]:
        """Use 'match' query to get persons data.
        """
        body = {
            'size': page_size,
            'from': (page - 1) * page_size,
            'query': {
                'match': {
                    'full_name': {
                        'query': query,
                        'fuzziness': 'auto'
                    }
                }
            }
        }
        doc = await self.elastic.search(index=self.index, body=body)
        return [self.model(**hit['_source']) for hit in doc['hits']['hits']]


@lru_cache()
def get_person_service(
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(elastic)
