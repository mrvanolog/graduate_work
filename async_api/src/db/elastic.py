from elasticsearch import AsyncElasticsearch

es: AsyncElasticsearch


# use it for dependency injection
async def get_elastic() -> AsyncElasticsearch:
    return es
