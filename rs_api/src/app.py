from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from settings import settings

from api.v1 import views

app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)

app.include_router(views.router, prefix='/v1/predictions')
