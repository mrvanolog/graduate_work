#!/bin/sh
WAIT_SLEEP=4
WAIT_LOOPS=10

is_ready() {
  eval "curl -XPUT http://elasticsearch:9200/movies -H 'Content-Type: application/json' -d @film_schema.json && \
        curl -XPUT http://elasticsearch:9200/person -H 'Content-Type: application/json' -d @person_schema.json && \
        curl -XPUT http://elasticsearch:9200/genre -H 'Content-Type: application/json' -d @genre_schema.json"
}

# wait until is ready
i=0
while ! is_ready; do
  i=$(expr $i + 1)
  if [ $i -ge $WAIT_LOOPS ]; then
    echo "$(date) - still not ready, giving up"
    exit 1
  fi
  echo "$(date) - waiting to be ready"
  sleep $WAIT_SLEEP
done

echo 'Success!!!'
