import random

import pytest

from settings import (ENDPOINT_GENRE_PREFIX, ES_GENRE_INDEX,
                      GENRE_SCHEMA_DATA_PATH)
from utils.helpers import extract_obj


@pytest.fixture(scope='session')
def endpoint_genre_url(api_base_url):
    return f'{api_base_url}/{ENDPOINT_GENRE_PREFIX}'


@pytest.fixture(scope='session')
def genre_data():
    with open(GENRE_SCHEMA_DATA_PATH) as f:
        data = f.read()
    yield data


@pytest.fixture(scope='session')
def create_es_doc(es_client):
    async def inner(uuid):
        doc = {
            'uuid': uuid,
            'name': 'test genre'
        }
        resp = await es_client.index(index=ES_GENRE_INDEX, body=doc)
        await es_client.indices.refresh(ES_GENRE_INDEX)
        return resp

    return inner


@pytest.mark.asyncio
async def test_genre_list_returns_data(make_get_request, bulk_data_to_es, genre_data, cleaner, endpoint_genre_url):
    await bulk_data_to_es(genre_data, ES_GENRE_INDEX)
    r = await make_get_request('', endpoint_genre_url)
    assert r.status != 404
    assert r.status == 200
    await cleaner(ES_GENRE_INDEX)


@pytest.mark.asyncio
async def test_genre_list_cache(make_get_request, bulk_data_to_es, genre_data, cleaner, redis_client,
                                endpoint_genre_url):
    await redis_client.flushall()
    await bulk_data_to_es(genre_data, ES_GENRE_INDEX)
    r = await make_get_request('', endpoint_genre_url)
    assert r.status != 404
    assert r.status == 200

    keys = await redis_client.keys('*')
    assert len(keys) == 1

    bytes_key = keys[0]
    compressed_data = await redis_client.get(bytes_key)
    data = extract_obj(compressed_data)
    assert len(r.body) == len(data)
    assert r.body == data
    await cleaner(ES_GENRE_INDEX)


@pytest.mark.asyncio
async def test_genre_details_find_correct_doc(create_es_doc, make_get_request, cleaner, endpoint_genre_url):
    test_uuid = 'fo123'
    await create_es_doc(test_uuid)
    r = await make_get_request(test_uuid, endpoint_genre_url)
    assert r.status == 200
    assert r.body['uuid'] == test_uuid
    await cleaner(ES_GENRE_INDEX)


@pytest.mark.asyncio
async def test_genre_details_not_find_correct_doc(create_es_doc, make_get_request, cleaner, endpoint_genre_url):
    test_uuid = 'fo123'
    await create_es_doc(test_uuid)
    r = await make_get_request('fo123353', endpoint_genre_url)
    assert r.status == 404
    await cleaner(ES_GENRE_INDEX)


@pytest.mark.asyncio
async def test_genre_details_id_less_than_minimum(make_get_request, endpoint_genre_url):
    test_uuid = 'f'
    r = await make_get_request(test_uuid, endpoint_genre_url)
    assert r.status == 422


@pytest.mark.asyncio
async def test_genre_details_id_greater_than_max_length(make_get_request, endpoint_genre_url):
    test_data = ''.join(chr(random.choice(range(100, 115))) for _ in range(256))
    r = await make_get_request(test_data, endpoint_genre_url)
    assert r.status == 422


@pytest.mark.asyncio
async def test_genre_details_cache(create_es_doc, make_get_request, cleaner, redis_client, endpoint_genre_url):
    await redis_client.flushall()
    test_uuid = 'fo123'
    await create_es_doc(test_uuid)
    r = await make_get_request(test_uuid, endpoint_genre_url)
    assert r.status == 200

    keys = await redis_client.keys('*')
    assert len(keys) == 1

    bytes_key = keys[0]
    compressed_data = await redis_client.get(bytes_key)
    data = extract_obj(compressed_data)
    assert r.body['uuid'] == test_uuid == data['uuid']
    await cleaner(ES_GENRE_INDEX)
