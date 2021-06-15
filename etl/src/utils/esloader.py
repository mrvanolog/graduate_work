import json
import logging
from typing import Dict, List
from urllib.parse import urljoin
from uuid import uuid4

import requests


class ESLoader:
    def __init__(self, url: str):
        self.url = url
        self.logger = logging.getLogger('esloader')

    def _get_es_bulk_query(self, rows: List[dict], index_name: str) -> List[str]:
        """Prepares bulk-request to Elasticsearch.
        """
        prepared_query = []
        for row in rows:
            prepared_query.extend(
                [
                    json.dumps({'index': {'_index': index_name, '_id': str(uuid4())}}),
                    json.dumps(row),
                ]
            )
        return prepared_query

    def _prepare_update_query(self, record: dict) -> str:
        """Returns prepared query for doc update in ES.
        """
        list_source: list = []
        for key in record:
            line = f'ctx._source.{key} = params.{key}'
            list_source.append(line)
        str_source = ';'.join(list_source)

        script = {
            'source': str_source,
            'params': record,
        }

        query = {
            'query': {
                'term': {
                    'uuid': {'value': record['uuid']}
                }
            },
            'script': script,
        }
        return json.dumps(query)

    def _prepare_check_query(self, record: dict) -> str:
        """Returns prepared query for doc check in ES.
        """
        query = {
            'query': {
                'term': {
                    'uuid': {'value': record['uuid']}
                }
            },
            '_source': False,
        }
        return json.dumps(query)

    def load_to_es(self, records: List[dict], index_name: str):
        """Loads new data to ES and handles errors with doc saving.
        """
        prepared_query = self._get_es_bulk_query(records, index_name)
        str_query = '\n'.join(prepared_query) + '\n'

        response = requests.post(
            urljoin(self.url, '_bulk'),
            data=str_query,
            headers={'Content-Type': 'application/x-ndjson'},
        )

        json_response = json.loads(response.content.decode())
        try:
            for item in json_response['items']:
                error_message = item['index'].get('error')
                if error_message:
                    self.logger.error(error_message)
        except KeyError:
            pass

    def update_in_es(self, records: List[dict], index_name: str):
        """Updates existing docs in ES and handles errors with doc updates.
        """
        for record in records:
            query = self._prepare_update_query(record)

            response = requests.post(
                f'{urljoin(self.url, index_name)}/_update_by_query',
                data=query,
                headers={'Content-Type': 'application/x-ndjson'},
            )

            json_response = json.loads(response.content.decode())
            try:
                for item in json_response['items']:
                    error_message = item['index'].get('error')
                    if error_message:
                        self.logger.error(error_message)
            except KeyError:
                pass

    def check_for_docs(self, records: List[dict], index_name: str) -> Dict[str, List[dict]]:
        """Checks if doc is in ES and creates dictionary with docs to update and docs to insert.
        Return dictionary has two keys: 'present' and 'not_present'.
        """
        list_present: List[dict] = []
        list_not_present: List[dict] = []
        for record in records:
            query = self._prepare_check_query(record)
            response = requests.get(
                f'{urljoin(self.url, index_name)}/_search',
                data=query,
                headers={'Content-Type': 'application/x-ndjson'},
            )
            try:
                res = response.json()
            except TypeError:
                continue

            _id = None
            if response and res['hits']['total']['value']:
                _id = res['hits']['hits'][0].get('_id', None)
            if _id is not None:
                list_present.append(record)
            else:
                list_not_present.append(record)

        return {
            "present": list_present,
            "not_present": list_not_present,
        }
