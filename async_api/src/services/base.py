from elasticsearch import AsyncElasticsearch


class BaseService:
    index: str
    model: callable

    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def get_by_id(self, _id: str):
        data = await self._get_from_elastic(_id)

        if not data:
            return None

        return data

    async def _get_from_elastic(self, _id: str):
        """Get model data using 'term' query.
        """
        query = {
            'query': {
                'term': {
                    'uuid': {
                        'value': _id
                    }
                }
            }
        }
        doc = await self.elastic.search(index=self.index, body=query)
        if doc['hits']['total']['value']:
            return self.model(**doc['hits']['hits'][0]['_source'])

    def __str__(self):
        return '%s' % self.__class__.__name__
