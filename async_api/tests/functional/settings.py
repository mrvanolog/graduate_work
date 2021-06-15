import os

REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
REDIS_PORT = os.getenv('REDIS_PORT', 6666)
REDIS_TEST_DB = 2

ELASTIC_HOST = os.getenv('ELASTIC_HOST', '127.0.0.1')
ELASTIC_PORT = os.getenv('ELASTIC_PORT', 9999)

API_HOST = os.getenv('API_HOST', '127.0.0.1')
API_PORT = os.getenv('API_PORT', 8000)

API_V1_PREFIX = 'api/v1'
ENDPOINT_FILM_PREFIX = 'film'
ENDPOINT_PERSON_PREFIX = 'person'
ENDPOINT_GENRE_PREFIX = 'genre'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILM_SCHEMA_PATH = os.path.join(BASE_DIR, 'test_data/elastic/schemas/film_schema.json')
PERSON_SCHEMA_PATH = os.path.join(BASE_DIR, 'test_data/elastic/schemas/person_schema.json')
GENRE_SCHEMA_PATH = os.path.join(BASE_DIR, 'test_data/elastic/schemas/genre_schema.json')

FILM_SCHEMA_DATA_PATH = os.path.join(BASE_DIR, 'test_data/elastic/data/film_data.txt')
GENRE_SCHEMA_DATA_PATH = os.path.join(BASE_DIR, 'test_data/elastic/data/genre_data.txt')
PERSON_SCHEMA_DATA_PATH = os.path.join(BASE_DIR, 'test_data/elastic/data/person_data.txt')
PERSON_FILM_SCHEMA_DATA_PATH = os.path.join(BASE_DIR, 'test_data/elastic/data/person_film_data.txt')

ES_FILM_INDEX = 'movies'
ES_PERSON_INDEX = 'person'
ES_GENRE_INDEX = 'genre'
