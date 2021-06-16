import pytest

from settings import (ENDPOINT_PERSON_PREFIX, ES_FILM_INDEX, ES_PERSON_INDEX,
                      FILM_SCHEMA_PATH, PERSON_FILM_SCHEMA_DATA_PATH,
                      PERSON_SCHEMA_DATA_PATH, PERSON_SCHEMA_PATH)
from utils.helpers import extract_obj


@pytest.fixture(scope='session')
def endpoint_person_url(api_base_url):
    yield f'{api_base_url}/{ENDPOINT_PERSON_PREFIX}'


@pytest.fixture(scope='session')
def create_person_doc(es_client):
    async def inner(uuid):
        doc = {
            'uuid': uuid,
            'full_name': 'Harrison Ford',
            'actor': [
                '707eed57-5834-4be8-9a5c-800d3daa227c',
                '949c3cfe-021a-4731-846b-5b9dca5e102d',
                '8c121fdb-216b-4f8f-bae7-ce77c4fd6803'],
            'writer': [],
            'director': [],
        }
        resp = await es_client.index(index=ES_PERSON_INDEX, body=doc)
        await es_client.indices.refresh(ES_PERSON_INDEX)
        return resp

    return inner


@pytest.fixture
def person_data():
    with open(PERSON_SCHEMA_DATA_PATH) as f:
        data = f.read()
    yield data


@pytest.fixture
def person_film_data():
    with open(PERSON_FILM_SCHEMA_DATA_PATH) as f:
        data = f.read()
    yield data


# /person/search/ tests

@pytest.mark.asyncio
async def test_person_search_doc_single(
        create_index, make_get_request, bulk_data_to_es, person_data, cleaner, endpoint_person_url
):
    await create_index(ES_PERSON_INDEX, PERSON_SCHEMA_PATH)
    await bulk_data_to_es(person_data, ES_PERSON_INDEX)

    params = {
        'query': 'Harrison Ford',
        'page': 1,
        'page_size': 1,
    }

    r = await make_get_request('search', endpoint_person_url, params)
    assert r.status == 200
    assert len(r.body) == 1
    assert r.body[0]['full_name'] == 'Harrison Ford'

    await cleaner(ES_PERSON_INDEX)


@pytest.mark.asyncio
@pytest.mark.parametrize('page_size', [5, 10])
async def test_person_search_doc_multiple(
        create_index, make_get_request, bulk_data_to_es, person_data, cleaner, page_size, endpoint_person_url
):
    await create_index(ES_PERSON_INDEX, PERSON_SCHEMA_PATH)
    await bulk_data_to_es(person_data, ES_PERSON_INDEX)

    params = {
        'query': 'Harrison Ford',
        'page': 1,
        'page_size': page_size,
    }

    r = await make_get_request('search', endpoint_person_url, params)
    assert r.status == 200
    assert len(r.body) == 5

    await cleaner(ES_PERSON_INDEX)


@pytest.mark.asyncio
@pytest.mark.parametrize('page_size', [999, 0, -1])
async def test_person_search_incorrect_page_size(page_size, make_get_request, endpoint_person_url):
    params = {
        'query': 'Harrison Ford',
        'page': 1,
        'page_size': page_size,
    }

    r = await make_get_request('search', endpoint_person_url, params)
    assert r.status == 422


@pytest.mark.asyncio
async def test_person_search_incorrect_query(make_get_request, endpoint_person_url):
    params = {
        'query': '',
        'page': 1,
        'page_size': 50,
    }

    r = await make_get_request('search', endpoint_person_url, params)
    assert r.status == 422


@pytest.mark.asyncio
@pytest.mark.parametrize('page', [9600, 0, -1])
async def test_person_search_incorrect_page(page, make_get_request, endpoint_person_url):
    params = {
        'query': 'Harrison Ford',
        'page': page,
        'page_size': 50,
    }

    r = await make_get_request('search', endpoint_person_url, params)
    assert r.status == 422


@pytest.mark.asyncio
async def test_person_search_cache(
        bulk_data_to_es, make_get_request, cleaner, person_data, redis_client, endpoint_person_url
):
    await redis_client.flushall()
    await bulk_data_to_es(person_data, ES_PERSON_INDEX)

    params = {
        'query': 'Harrison Ford',
        'page': 1,
        'page_size': 5,
    }
    r = await make_get_request('search', endpoint_person_url, params)
    assert r.status == 200

    test_uuids = [item['uuid'] for item in r.body]
    assert len(test_uuids) == 5

    keys = await redis_client.keys('*')
    assert len(keys) == 1

    bytes_key = keys[0]
    compressed_data = await redis_client.get(bytes_key)
    data = extract_obj(compressed_data)
    control_uuids = [f['uuid'] for f in data]
    assert len(control_uuids) == 5
    assert test_uuids == control_uuids

    await cleaner(ES_PERSON_INDEX)


# /{person_id}}/ tests

@pytest.mark.asyncio
async def test_person_detail(
        create_index, make_get_request, bulk_data_to_es, person_data, cleaner, endpoint_person_url
):
    await create_index(ES_PERSON_INDEX, PERSON_SCHEMA_PATH)
    await bulk_data_to_es(person_data, ES_PERSON_INDEX)

    doc = {
        'uuid': '12c68e9e-607e-4624-ae6a-5104a3d04ee0',
        'full_name': 'Harrison Ford',
        'actor': [
            '707eed57-5834-4be8-9a5c-800d3daa227c',
            '949c3cfe-021a-4731-846b-5b9dca5e102d',
            '8c121fdb-216b-4f8f-bae7-ce77c4fd6803',
        ],
        'writer': [],
        'director': []
    }

    r = await make_get_request(doc['uuid'], endpoint_person_url)
    assert r.status == 200
    assert r.body == doc

    await cleaner(ES_PERSON_INDEX)


@pytest.mark.asyncio
async def test_person_detail_uuid_doesnt_exist(
        create_index, make_get_request, bulk_data_to_es, person_data, cleaner, endpoint_person_url
):
    await create_index(ES_PERSON_INDEX, PERSON_SCHEMA_PATH)
    await bulk_data_to_es(person_data, ES_PERSON_INDEX)

    uuid = 'some-random-uuid'

    r = await make_get_request(uuid, endpoint_person_url)
    assert r.status == 404

    await cleaner(ES_PERSON_INDEX)


@pytest.mark.asyncio
async def test_person_detail_cache(
        create_index, make_get_request, create_person_doc, redis_client, cleaner, endpoint_person_url
):
    await redis_client.flushall()
    await create_index(ES_PERSON_INDEX, PERSON_SCHEMA_PATH)

    test_uuid = '12c68e9e-607e-4624-ae6a-5104a3d04ee0'
    await create_person_doc(test_uuid)

    r = await make_get_request(test_uuid, endpoint_person_url)
    keys = await redis_client.keys('*')
    assert len(keys) == 1

    bytes_key = keys[0]
    compressed_data = await redis_client.get(bytes_key)
    data = extract_obj(compressed_data)
    control_uuid = data['uuid']

    assert test_uuid == control_uuid == r.body['uuid']
    await cleaner(ES_PERSON_INDEX)


# /{person_id}/film tests

@pytest.mark.asyncio
async def test_person_films(
        create_index, make_get_request, bulk_data_to_es, person_data, person_film_data, cleaner, endpoint_person_url
):
    await create_index(ES_PERSON_INDEX, PERSON_SCHEMA_PATH)
    await create_index(ES_FILM_INDEX, FILM_SCHEMA_PATH)

    await bulk_data_to_es(person_data, ES_PERSON_INDEX)
    await bulk_data_to_es(person_film_data, ES_FILM_INDEX)

    uuid = '12c68e9e-607e-4624-ae6a-5104a3d04ee0'

    r = await make_get_request(f'{uuid}/film', endpoint_person_url)
    assert r.status == 200
    assert len(r.body) == 3

    await cleaner(ES_PERSON_INDEX)
    await cleaner(ES_FILM_INDEX)


@pytest.mark.asyncio
async def test_person_films_uuid_doesnt_exist(
        create_index, make_get_request, bulk_data_to_es, person_data, cleaner, endpoint_person_url
):
    """Check that API returns full data about a person by it's uuid.
    """
    await create_index(ES_PERSON_INDEX, PERSON_SCHEMA_PATH)
    await bulk_data_to_es(person_data, ES_PERSON_INDEX)

    uuid = 'some-random-uuid'

    r = await make_get_request(f'{uuid}/film', endpoint_person_url)
    assert r.status == 404

    await cleaner(ES_PERSON_INDEX)
