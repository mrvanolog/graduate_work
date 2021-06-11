import logging
from fastapi import FastAPI, Depends

from conf.log import set_up_logging
from services.predictor import Predictor, get_predictor


app = FastAPI(title='RS Predicitor API', docs_url='/rs/docs')


@app.on_event('startup')
async def startup_event():
    set_up_logging()

logger = logging.getLogger('main')


@app.get('rs/healthcheck', status_code=200)
async def health_check():
    return "I'm alive"


@app.post('/rs/users')
async def predict_for_users(predictor: Predictor = Depends(get_predictor)):
    predictor.predict_for_users()


@app.post('/rs/movies')
async def predict_for_movies(predictor: Predictor = Depends(get_predictor)):
    predictor.predict_for_movies()
