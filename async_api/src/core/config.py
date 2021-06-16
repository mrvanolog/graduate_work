import os
from logging import config as logging_config

from core.logger import LOGGING

# apply logging settings
logging_config.dictConfig(LOGGING)

# project name. Use it in swagger docs
PROJECT_NAME = os.getenv('PROJECT_NAME', 'movies')

# redis
REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')
CACHE_TTL = 60  # 1 min
CACHE_COMPRESS_LEVEL = 1
CACHE_REDIS_DB = 2

# elastic
ELASTIC_HOST = os.getenv('ELASTIC_HOST', '127.0.0.1')
ELASTIC_PORT = int(os.getenv('ELASTIC_PORT', 9200))
ELASTIC_MAX_RESULT_WINDOW = 9500
# root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# api settings
API_V1_PREFIX = '/api/v1'
PER_PAGE = 50
MAX_PER_PAGE = 100
DEFAULT_PAGE = 1