import random

import pytest

from settings import (ENDPOINT_FILM_PREFIX, ES_FILM_INDEX,
                      FILM_SCHEMA_DATA_PATH, FILM_SCHEMA_PATH)
from utils.helpers import extract_obj


@pytest.fixture(scope='session')
def endpoint_film_url(api_base_url):
    return f'{api_base_url}/{ENDPOINT_FILM_PREFIX}'


@pytest.fixture(scope='session')
def create_es_doc(es_client):
    async def inner(uuid):
        doc = {
            'uuid': uuid,
            'title': 'film',
            'description': 'foo',
            'imdb_rating': 7.9,
            'genres': [{'uuid': 'guid1', 'name': 'comedy'}, {'uuid': 'guid2', 'name': 'action'}],
            'actors': [{'uuid': 'auuid1', 'full_name': 'Eggs Man'}],
            'directors': [{'uuid': 'diuid1', 'full_name': 'Bazz Bar'}],
            'writers': [],
        }
        resp = await es_client.index(index=ES_FILM_INDEX, body=doc)
        await es_client.indices.refresh(ES_FILM_INDEX)
        return resp

    return inner


@pytest.fixture(scope='session')
def film_data():
    with open(FILM_SCHEMA_DATA_PATH) as f:
        data = f.read()
    yield data


# /film/ tests

@pytest.mark.asyncio
async def test_imdb_film_asc_sorting_order(bulk_data_to_es, make_get_request, cleaner, film_data, endpoint_film_url):
    await bulk_data_to_es(film_data, ES_FILM_INDEX)

    params = {
        'sort': 'imdb_rating'
    }
    r = await make_get_request('', endpoint_film_url, params)
    assert r.status == 200

    rating = [item['imdb_rating'] for item in r.body]
    assert len(rating) == 50

    idx = 1
    while idx < len(rating):
        assert rating[idx - 1] <= rating[idx]
        idx += 1

    await cleaner(ES_FILM_INDEX)


@pytest.mark.asyncio
async def test_imdb_film_desc_sorting_order(bulk_data_to_es, make_get_request, cleaner, film_data, endpoint_film_url):
    await bulk_data_to_es(film_data, ES_FILM_INDEX)

    params = {
        'sort': '-imdb_rating'
    }
    r = await make_get_request('', endpoint_film_url, params)

    assert r.status == 200

    rating = [item['imdb_rating'] for item in r.body]
    assert len(rating) == 50

    idx = 1
    while idx < len(rating):
        assert rating[idx - 1] >= rating[idx]
        idx += 1

    await cleaner(ES_FILM_INDEX)


@pytest.mark.asyncio
async def test_sort_regexp_mismatch(make_get_request, endpoint_film_url):
    params = {
        'sort': '--'
    }
    r = await make_get_request('', endpoint_film_url, params)
    assert r.status == 422


@pytest.mark.asyncio
async def test_sort_regexp_mismatch_wrong_first_char(make_get_request, endpoint_film_url):
    params = {
        'sort': '+'
    }
    r = await make_get_request('', endpoint_film_url, params)
    assert r.status == 422


@pytest.mark.asyncio
async def test_sort_lower_than_min_length(make_get_request, endpoint_film_url):
    params = {
        'sort': ''
    }
    r = await make_get_request('', endpoint_film_url, params)
    assert r.status == 422


@pytest.mark.asyncio
async def test_sort_greater_than_max_length(make_get_request, endpoint_film_url):
    test_data = ''.join(chr(random.choice(range(100, 115))) for _ in range(21))
    params = {
        'sort': test_data
    }
    r = await make_get_request('', endpoint_film_url, params)
    assert r.status == 422


@pytest.mark.asyncio
async def test_page_less_than_bound(make_get_request, endpoint_film_url):
    params = {
        'sort': '-imdb_rating',
        'page': '-1'
    }
    r = await make_get_request('', endpoint_film_url, params)
    assert r.status == 422


@pytest.mark.asyncio
async def test_page_greater_than_bound(make_get_request, endpoint_film_url):
    params = {
        'sort': '-imdb_rating',
        'page': '100000'
    }
    r = await make_get_request('', endpoint_film_url, params)
    assert r.status == 422


@pytest.mark.asyncio
async def test_page_size_less_than_bound(make_get_request, endpoint_film_url):
    params = {
        'sort': '-imdb_rating',
        'page_size': 0
    }
    r = await make_get_request('', endpoint_film_url, params)
    assert r.status == 422


@pytest.mark.asyncio
async def test_page_size_greater_than_bound(make_get_request, endpoint_film_url):
    params = {
        'sort': '-imdb_rating',
        'page_size': 101
    }
    r = await make_get_request('', endpoint_film_url, params)
    assert r.status == 422


@pytest.mark.asyncio
async def test_film_genre_less_than_min_length(make_get_request, endpoint_film_url):
    params = {
        'sort': '-imdb_rating',
        'genre': ''
    }
    r = await make_get_request('', endpoint_film_url, params)
    assert r.status == 422


@pytest.mark.asyncio
async def test_film_genre_greater_than_max_length(make_get_request, endpoint_film_url):
    test_data = ''.join(chr(random.choice(range(100, 115))) for _ in range(21))
    params = {
        'sort': '-imdb_rating',
        'genre': test_data
    }
    r = await make_get_request('', endpoint_film_url, params)
    assert r.status == 422


@pytest.mark.asyncio
async def test_film_filter_by_exists_genre(create_index, bulk_data_to_es, make_get_request, cleaner, film_data,
                                           endpoint_film_url):
    await create_index(ES_FILM_INDEX, FILM_SCHEMA_PATH)
    await bulk_data_to_es(film_data, ES_FILM_INDEX)

    params = {
        'sort': '-imdb_rating',
        'genre': 'action'
    }
    r = await make_get_request('', endpoint_film_url, params)
    assert r.status == 200
    await cleaner(ES_FILM_INDEX)


@pytest.mark.asyncio
async def test_film_filter_by_not_exists_genre(create_index, bulk_data_to_es, make_get_request, cleaner, film_data,
                                               endpoint_film_url):
    await create_index(ES_FILM_INDEX, FILM_SCHEMA_PATH)
    await bulk_data_to_es(film_data, ES_FILM_INDEX)

    params = {
        'sort': '-imdb_rating',
        'genre': 'notexistsgenre'
    }
    r = await make_get_request('', endpoint_film_url, params)
    assert r.status == 404
    await cleaner(ES_FILM_INDEX)


@pytest.mark.asyncio
async def test_film_cache(bulk_data_to_es, make_get_request, cleaner, film_data, redis_client, endpoint_film_url):
    await redis_client.flushall()
    await bulk_data_to_es(film_data, ES_FILM_INDEX)

    params = {
        'sort': '-imdb_rating',
        'page_size': 100
    }
    r_1 = await make_get_request('', endpoint_film_url, params)
    assert r_1.status == 200

    test_uuids = [item['uuid'] for item in r_1.body]
    assert len(test_uuids) == 100

    keys = await redis_client.keys('*')
    assert len(keys) == 1

    bytes_key = keys[0]
    compressed_data = await redis_client.get(bytes_key)
    data = extract_obj(compressed_data)
    control_uuids = [f['uuid'] for f in data]
    assert len(control_uuids) == 100
    assert test_uuids == control_uuids
    await cleaner(ES_FILM_INDEX)


# /film/{film_id} tests

@pytest.mark.asyncio
async def test_film_details_returns_correct_data(create_es_doc, make_get_request, cleaner, endpoint_film_url):
    film_uuid = 'testfilm1224'
    await create_es_doc(film_uuid)
    r = await make_get_request(film_uuid, endpoint_film_url)
    assert r.status == 200
    assert film_uuid == r.body['uuid']
    await cleaner(ES_FILM_INDEX)


@pytest.mark.asyncio
async def test_film_returns_404(create_es_doc, make_get_request, cleaner, endpoint_film_url):
    film_uuid = 'testfilm199'
    await create_es_doc(film_uuid)
    r = await make_get_request('testfilm2000', endpoint_film_url)
    assert r.status == 404
    await cleaner(ES_FILM_INDEX)


@pytest.mark.asyncio
async def test_film_details_uuid_less_than_min_length(make_get_request, endpoint_film_url):
    r = await make_get_request('', endpoint_film_url)
    assert r.status == 422


@pytest.mark.asyncio
async def test_film_details_uuid_greater_than_max_length(make_get_request, endpoint_film_url):
    test_data = ''.join(chr(random.choice(range(100, 115))) for _ in range(256))
    r = await make_get_request(test_data, endpoint_film_url)
    assert r.status == 422


@pytest.mark.asyncio
async def test_film_details_cache(make_get_request, create_es_doc, redis_client, cleaner, endpoint_film_url):
    await redis_client.flushall()
    test_uuid = 'cachetestuuid'
    await create_es_doc(test_uuid)
    r = await make_get_request(test_uuid, endpoint_film_url)

    keys = await redis_client.keys('*')
    assert len(keys) == 1

    bytes_key = keys[0]
    compressed_data = await redis_client.get(bytes_key)
    data = extract_obj(compressed_data)
    control_uuid = data['uuid']

    assert test_uuid == control_uuid == r.body['uuid']
    await cleaner(ES_FILM_INDEX)


# /film/search


@pytest.mark.asyncio
async def test_search_title_consists_query_word(bulk_data_to_es, make_get_request, cleaner, film_data, create_index,
                                                endpoint_film_url):
    await create_index(ES_FILM_INDEX, FILM_SCHEMA_PATH)
    await bulk_data_to_es(film_data, ES_FILM_INDEX)

    params = {
        'query': 'star',
        'page_size': 10
    }
    r = await make_get_request('search', endpoint_film_url, params)
    assert any(['star' in x['title'].lower() for x in r.body])
    await cleaner(ES_FILM_INDEX)


@pytest.mark.asyncio
async def test_search_query_less_than_min_length(make_get_request, endpoint_film_url):
    params = {
        'query': '',
        'page_size': 10
    }
    r = await make_get_request('search', endpoint_film_url, params)
    assert r.status == 422


@pytest.mark.asyncio
async def test_search_query_greater_than_max_length(make_get_request, endpoint_film_url):
    test_data = ''.join(chr(random.choice(range(100, 115))) for _ in range(256))

    params = {
        'query': test_data,
        'page_size': 10
    }
    r = await make_get_request('search', endpoint_film_url, params)
    assert r.status == 422
