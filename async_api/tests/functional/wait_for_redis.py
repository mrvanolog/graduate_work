import asyncio

import aioredis

from settings import REDIS_HOST, REDIS_PORT, REDIS_TEST_DB


async def main():
    redis_client = await aioredis.create_redis((REDIS_HOST, REDIS_PORT), db=REDIS_TEST_DB)
    ping = bytes()

    while not ping == b'PONG':
        ping = await redis_client.ping()

    redis_client.close()
    await redis_client.wait_closed()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
