import asyncio

from elasticsearch import AsyncElasticsearch

from settings import ELASTIC_HOST, ELASTIC_PORT


async def main():
    es_client = AsyncElasticsearch(hosts=f'{ELASTIC_HOST}:{ELASTIC_PORT}')
    ping = False

    while not ping:
        await asyncio.sleep(2)
        ping = await es_client.ping()

    await es_client.close()

if __name__ == '__main__':
    # instead of asyncio.run
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
