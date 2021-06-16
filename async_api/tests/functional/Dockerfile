FROM python:3.8
ENV ELASTIC_HOST=elasticsearch \
    ELASTIC_PORT=9200 \
    REDIS_HOST=redis \
    REDIS_PORT=6379 \
    API_HOST=api \
    API_PORT=80
WORKDIR /tests
COPY requirements.txt /tests
RUN python -m pip install --upgrade pip && python -m pip install -r requirements.txt
COPY . /tests
CMD python3 wait_for_es.py && python3 wait_for_redis.py && python3 -m pytest -r src/