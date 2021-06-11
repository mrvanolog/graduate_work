ETL_IMAGE = cr.yandex/crpeniun2041jirjgthk/etl:latest
ES_INITIALIZER_IMAGE = cr.yandex/crpeniun2041jirjgthk/es_initializer:latest
ASYNC_API_IMAGE = cr.yandex/crpeniun2041jirjgthk/asyncapi:latest
RS_IMAGE = cr.yandex/crpeniun2041jirjgthk/rs_inner_api:latest

ENV = prod

SECRETS_DIR=secrets/${ENV}

include $(SECRETS_DIR)/.env

COMPOSE_FILES=-f docker-compose.prod.yml
REDIS_HOST=$(shell redis-cli -h rc1a-f3ms9phcasixnqw8.mdb.yandexcloud.net -p 26379 sentinel get-master-addr-by-name redis106 | head -n 1)


build-n-run: RUN_DOCKER=docker-compose ${COMPOSE_FILES} up --build
run: RUN_DOCKER=docker-compose ${COMPOSE_FILES} up

run build-n-run:
	RS_POSTGRES_PASSWORD=${RS_POSTGRES_PASSWORD} \
	RS_POSTGRES_USER=${RS_POSTGRES_USER} \
	RS_PREDICTIONS_POSTGRES_DB=${RS_PREDICTIONS_POSTGRES_DB} \
	RS_DATA_POSTGRES_DB=${RS_DATA_POSTGRES_DB} \
	RS_POSTGRES_PORT=${RS_POSTGRES_PORT} \
	RS_POSTGRES_HOST=${RS_POSTGRES_HOST} \
	POSTGRES_PASSWORD=${POSTGRES_PASSWORD} \
	POSTGRES_USER=${POSTGRES_USER} \
	POSTGRES_DB=${POSTGRES_DB} \
	POSTGRES_PORT=${POSTGRES_PORT} \
	POSTGRES_HOST=${POSTGRES_HOST} \
	REDIS_HOST=${REDIS_HOST} \
	REDIS_PASSWORD=${REDIS_PASSWORD} \
	REQUIREMENTS_FILE=requirements.txt \
	TIMEZONE=${TIMEZONE} \
	ETL_IMAGE=${ETL_IMAGE} \
	ASYNC_API_IMAGE=${ASYNC_API_IMAGE} \
	ES_INITIALIZER_IMAGE=${ES_INITIALIZER_IMAGE} \
	$(RUN_DOCKER)


upload-etl:
	docker push ${ETL_IMAGE}

upload-rs:
    docker push ${RS_IMAGE}

sync-remote:
	rm -rf remote/buffer && \
	mkdir -p remote/buffer && \
	cp docker-compose.prod.yml Makefile secrets/prod/.env remote/buffer
# 	rsync -r remote/buffer/ platondmitriev@84.252.143.15:/home/platondmitriev/srv

stop:
	docker stop $(shell docker ps -f network=etl_net -aq)

rerun: stop run