import logging

import uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1.api import api_router
from core import config
from core.logger import LOGGING
from db import elastic

app = FastAPI(
    title='Read-only API для онлайн-кинотеатра',
    description='Информация о фильмах, жанрах и людях, участвовавших в создании произведения',
    version='1.0.0',
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)


@app.on_event('startup')
async def startup():
    elastic.es = AsyncElasticsearch(hosts=[f'{config.ELASTIC_HOST}:{config.ELASTIC_PORT}'])


@app.on_event('shutdown')
async def shutdown():
    await elastic.es.close()


# include routers
app.include_router(api_router, prefix=config.API_V1_PREFIX)


# if __name__ == '__main__':
#     # `uvicorn main:app --host 0.0.0.0 --port 8000`
#     uvicorn.run(
#         'main:app',
#         host='0.0.0.0',
#         port=8001,
#         log_config=LOGGING,
#         log_level=logging.DEBUG,
#     )
