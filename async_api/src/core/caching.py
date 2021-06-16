import gzip
import pickle
from functools import wraps

import aioredis

from core.config import (CACHE_COMPRESS_LEVEL, CACHE_REDIS_DB, CACHE_TTL,
                         REDIS_HOST, REDIS_PORT, REDIS_PASSWORD)


def make_hash_str(*args, cache_type='query'):
    return 'api_cache_{}_{}'.format(cache_type, '_'.join([str(x) for x in args]))


async def set_cache_value(key, value):
    redis = await aioredis.create_redis((REDIS_HOST, REDIS_PORT),
                                         password=REDIS_PASSWORD,
                                        db=CACHE_REDIS_DB)
    await redis.set(key, value, expire=CACHE_TTL)
    redis.close()
    await redis.wait_closed()


async def get_cache_value(key):
    redis = await aioredis.create_redis((REDIS_HOST, REDIS_PORT),
                                         password=REDIS_PASSWORD,
                                        db=CACHE_REDIS_DB)
    res = await redis.get(key)
    redis.close()
    await redis.wait_closed()
    return res


def stringify_endpoint_params_as_list(**kwargs):
    return [str(val) for param_pair in [(key_param, param) for key_param, param in kwargs.items()] for val in param_pair]


def compress_obj(obj):
    picked_data = pickle.dumps(obj)
    compressed_data = gzip.compress(picked_data, compresslevel=CACHE_COMPRESS_LEVEL)
    return compressed_data


def extract_obj(compressed_data):
    pickled_data = gzip.decompress(compressed_data)
    obj = pickle.loads(pickled_data)
    return obj


def prepare_res(res):
    if isinstance(res, list):
        return [x.dict() for x in res]
    return res.dict()


def cache(prefix):
    def wrapper(coroutine):

        @wraps(coroutine)
        async def inner(*args, **kwargs):
            stringified_params = stringify_endpoint_params_as_list(**kwargs)
            key = make_hash_str(prefix, *args, *stringified_params)
            res = await get_cache_value(key)

            if res is None:
                res = await coroutine(*args, **kwargs)
                res = prepare_res(res)
                compressed_obj = compress_obj(res)
                await set_cache_value(key, compressed_obj)
            else:
                res = extract_obj(res)

            return res

        return inner

    return wrapper
