include deploy/.env

ETL_IMAGE=cr.yandex/crpeniun2041jirjgthk/etl:latest
ES_INITIALIZER_IMAGE=cr.yandex/crpeniun2041jirjgthk/es_initializer:latest
ASYNC_API_IMAGE=cr.yandex/crpeniun2041jirjgthk/asyncapi:latest
RS_IMAGE=cr.yandex/crpeniun2041jirjgthk/rs_inner_api:latest
RS_ETL_IMAGE=cr.yandex/crpeniun2041jirjgthk/rs_etl

ifndef ENV
ENV = dev
endif

SECRETS_DIR=secrets/${ENV}

include $(SECRETS_DIR)/.env

ifeq (${ENV}, dev)
COMPOSE_FILES=-f docker-compose.yml
else
COMPOSE_FILES=-f docker-compose.prod.yml
REDIS_HOST=$(shell redis-cli -h rc1a-f3ms9phcasixnqw8.mdb.yandexcloud.net -p 26379 sentinel get-master-addr-by-name redis106 | head -n 1)
endif


build-n-run: RUN_DOCKER=docker-compose ${COMPOSE_FILES} up --build
run: RUN_DOCKER=docker-compose ${COMPOSE_FILES} up

run build-n-run:
	POSTGRES_PREDICTIONS_DB=${POSTGRES_PREDICTIONS_DB} \
	POSTGRES_PREDICTIONS_HOST=${POSTGRES_PREDICTIONS_HOST} \
	POSTGRES_PREDICTIONS_PORT=${POSTGRES_PREDICTIONS_PORT} \
	POSTGRES_PREDICTIONS_USER=${POSTGRES_PREDICTIONS_USER} \
	POSTGRES_PREDICTIONS_PASSWORD=${POSTGRES_PREDICTIONS_PASSWORD} \
	POSTGRES_MOVIES_DB=${POSTGRES_MOVIES_DB} \
	POSTGRES_MOVIES_HOST=${POSTGRES_MOVIES_HOST} \
	POSTGRES_MOVIES_PORT=${POSTGRES_MOVIES_PORT} \
	POSTGRES_MOVIES_USER=${POSTGRES_MOVIES_USER} \
	POSTGRES_MOVIES_PASSWORD=${POSTGRES_MOVIES_PASSWORD} \
	POSTGRES_UGC_DB=${POSTGRES_UGC_DB} \
	POSTGRES_UGC_HOST=${POSTGRES_UGC_HOST} \
	POSTGRES_UGC_PORT=${POSTGRES_UGC_PORT} \
	POSTGRES_UGC_USER=${POSTGRES_UGC_USER} \
	POSTGRES_UGC_PASSWORD=${POSTGRES_UGC_PASSWORD} \
	POSTGRES_DATA_DB=${POSTGRES_DATA_DB} \
	POSTGRES_DATA_HOST=${POSTGRES_DATA_HOST} \
	POSTGRES_DATA_PORT=${POSTGRES_DATA_PORT} \
	POSTGRES_DATA_USER=${POSTGRES_DATA_USER} \
	POSTGRES_DATA_PASSWORD=${POSTGRES_DATA_PASSWORD} \
	POSTGRES_USERS_DB=${POSTGRES_USERS_DB} \
	REDIS_HOST=${REDIS_HOST} \
	REDIS_PASSWORD=${REDIS_PASSWORD} \
	REQUIREMENTS_FILE=requirements.txt \
	TIMEZONE=${TIMEZONE} \
	ETL_IMAGE=${ETL_IMAGE} \
	ASYNC_API_IMAGE=${ASYNC_API_IMAGE} \
	ES_INITIALIZER_IMAGE=${ES_INITIALIZER_IMAGE} \
	RS_IMAGE=${RS_IMAGE} \
	RS_ETL_IMAGE=${RS_ETL_IMAGE} \
	SSL_MODE=${SSL_MODE} \
	SECRET_KEY=${SECRET_KEY} \
	$(RUN_DOCKER)


upload-etl:
	docker push ${ETL_IMAGE}

sync-remote:
	rsync -r remote/buffer/ platondmitriev@84.252.143.15:/home/platondmitriev/srv

stop:
	docker stop $(shell docker ps -f network=etl_net -aq)

rerun: stop run