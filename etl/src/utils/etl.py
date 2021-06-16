import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

import yaml
from psycopg2.extensions import connection as _connection
from utils.esloader import ESLoader
from utils.models import FilmRow, GenreRow, PersonRow
from utils.state import BaseStorage, State
from utils.utils import coroutine


class ETL:
    """ETL class object can initialise process that will update data in ElasticSearch (ES)
    index in case if data in PostgreSQL data base was modified.

    Parameters
    ----------
    pg_conn : psycopg2.extensions.connection
        Conection to postgres db
    es_url : str
        URL to ES index
    storage : BaseStorage
        Storage for state
    """
    def __init__(self, pg_conn: _connection, es_url: str, storage: BaseStorage):
        self.pg_conn = pg_conn
        self.loader = ESLoader(es_url)
        self.state = State(storage)

        self.switch_offset: bool = False
        self.film_work_update: bool = False

        self.person_key: str
        self.genre_key: str
        self.film_work_key: str

        path_sql = Path(__file__).parent.joinpath('sql_templates.yaml')
        with path_sql.open('r') as f:
            r = f.read()
            self.sql_templates = yaml.safe_load(r)

        self.logger = logging.getLogger('etl')

    def _generate_state_key(self, type_: str, time_modified: datetime) -> str:
        """Generates state key for entity type and time modified.
        """
        timestamp = int(time_modified.timestamp())

        return f'{type_}_{timestamp}'

    def _check_state(self, state_key: str) -> bool:
        if self.state.get_state(state_key) is None:
            return False

        return True

    def _set_initial_state(self, state_key: str):
        """Sets initial state for etl process and returns the key of the state.
        """
        state_value = {'offset_1': 0, 'offset_2': 0}
        self.state.set_state(state_key, state_value)

    def _update_offset(self, state_key: str, offset: int):
        """Adds an increment of 100 to chosen offset of the state.
        """
        current_state = self.state.get_state(state_key)
        current_state[f'offset_{offset}'] += 100

        self.state.set_state(state_key, current_state)

    def _reset_offset(self, state_key: str, offset: int):
        """Resests chosen offset back to 0.
        """
        current_state = self.state.get_state(state_key)
        current_state[f'offset_{offset}'] = 0

        self.state.set_state(state_key, current_state)

    def _get_offset(self, state_key: str, offset: int) -> Tuple[int]:
        """Returns limit and offset of the current state.
        """
        current_state = self.state.get_state(state_key)

        return current_state[f'offset_{offset}']

    def _get_ids_list(self, data: List[tuple]) -> List[str]:
        """Creates list of ids from a tuple that Postgres returns.
        """
        return [row[0] for row in data]

    def _get_ids_str(self, list_ids: List[str]) -> str:
        """Converts ids from a list of string to a string appropriate for postgres query.
        Example: "'id1', 'id2', ..., 'id999'"
        """
        return "'" + "', '".join(list_ids) + "'"

    def _add_movie_data(
        self, dict_movie_data: Dict[str, dict], row: FilmRow
    ) -> Dict[str, dict]:
        """Adds information to movie dictionary from a postgres row.
        """
        dict_movie_data[row.fw_id]['genres'].add(
            (row.g_id, row.name)
        )
        if row.role == 'director':
            dict_movie_data[row.fw_id]['directors'].add(
                (row.p_id, row.full_name)
            )
        elif row.role == 'actor':
            dict_movie_data[row.fw_id]['actors'].add(
                (row.p_id, row.full_name)
            )
        elif row.role == 'writer':
            dict_movie_data[row.fw_id]['writers'].add(
                (row.p_id, row.full_name)
            )

        return dict_movie_data

    def _transform_movie(self, movie: Dict[str, Any]) -> Dict[str, Any]:
        """Converts fields genres, directors, actors and writers from set of tuples
        to list of dicts.
        """
        genres = [
            {'uuid': val[0], 'name': val[1]} for val in movie['genres'] if val[0] is not None
        ]
        directors = [
            {
                'uuid': val[0],
                'full_name': val[1],
            } for val in movie['directors'] if val[0] is not None
        ]
        actors = [
            {'uuid': val[0], 'full_name': val[1]} for val in movie['actors'] if val[0] is not None
        ]
        writers = [
            {'uuid': val[0], 'full_name': val[1]} for val in movie['writers'] if val[0] is not None
        ]

        transformed_movie = {
            'uuid': movie['uuid'],
            'title': movie['title'],
            'imdb_rating': movie['imdb_rating'],
            'description': movie['description'] or '',
            'genres': genres,
            'directors': directors,
            'actors': actors,
            'writers': writers,
        }

        return transformed_movie

    @coroutine
    def postgres_producer(
        self, target, state_key: str, sql_template: str, time_modified: datetime
    ) -> List[str]:
        """Coroutine process that finds ids of records that were updated.
        Entities that could be updated:
        - Person
        - Genre
        - Film_work

        Parameters
        ----------
        target : [type]
            Next coroutine process
        state_key : str
            Key of the state record with information about the current offset
        sql_template : str
            Query to download data from postgres
        time_modified : datetime
            If record in postgres was updated after this time it will be synchronised with ES

        Returns
        -------
        List[str]
            List of ids of records that were updated

        Raises
        ------
        GeneratorExit
            When no more updated records could be found, coroutine stops
        """
        while True:
            offset = self._get_offset(state_key, 1)
            sql = sql_template.format(time_modified, offset)
            with self.pg_conn.cursor() as cur:
                cur.execute(sql)
                data = cur.fetchall()

            list_id = self._get_ids_list(data)
            if not list_id:
                raise GeneratorExit

            target.send(list_id)

    @coroutine
    def postgres_enricher(
        self, target, state_key: str, sql_template: str, time_modified: datetime
    ) -> List[str]:
        """Coroutine process that finds film_work ids associated with recods that were updated.

        Parameters
        ----------
        target : [type]
            Next coroutine process
        state_key : str
            Key of the state record with information about the current offset
        sql_template : str
            Query to download data from postgres
        time_modified : datetime
            If record in postgres was updated after this time it will be synchronised with ES

        Returns
        -------
        List[str]
            List of ids of film_works that were updated

        Raises
        ------
        GeneratorExit
            When no more updated records could be found, coroutine stops
        """
        while True:
            offset = self._get_offset(state_key, 2)
            list_ids = (yield)
            str_ids = self._get_ids_str(list_ids)
            sql = sql_template.format(time_modified, str_ids, offset)
            with self.pg_conn.cursor() as cur:
                cur.execute(sql)
                data = cur.fetchall()

            list_id = self._get_ids_list(data)
            if not list_id and offset == 0:
                raise GeneratorExit
            elif not list_id and offset > 0:
                list_id = ['00000000-0000-0000-0000-000000000000']
                self.switch_offset = True

            target.send(list_id)

    @coroutine
    def postgres_merger(self, target, sql_template: str) -> List[tuple]:
        """Coroutine process that extracts all film_work data
        for ids found by postgres_enricher.

        Parameters
        ----------
        target : [type]
            Next coroutine process
        sql_template : str
            Query to download data from postgres

        Returns
        -------
        List[tuple]
            All data about updated movies
        """
        while True:
            list_ids = (yield)
            str_ids = self._get_ids_str(list_ids)
            sql = sql_template.format(str_ids)
            with self.pg_conn.cursor() as cur:
                cur.execute(sql)
                data = cur.fetchall()

            target.send(data)

    @coroutine
    def transform_film(self, target) -> List[dict]:
        """Coroutine process that transforms film data from postgres_merger
        to the format acceptable for ES.

        Parameters
        ----------
        target : [type]
            Next coroutine process

        Returns
        -------
        List[dict]
            Data ready for upload to ES
        """
        while True:
            data = (yield)
            unique_films: Set = set()
            dict_movie_data: Dict[str, dict] = {}

            for tuple_row in data:
                # creating dataclass from tuple, that was received from psycopg2
                row = FilmRow(*tuple_row)

                # check if this is the first time the movie is processed
                if row.fw_id not in unique_films:
                    # if it's the first time, add id to the set and create new movie dict
                    unique_films.add(row.fw_id)
                    dict_movie_data[row.fw_id] = {
                        'uuid': row.fw_id,
                        'title': row.title,
                        'description': row.description,
                        'imdb_rating': row.rating,
                        'genres': set(),
                        'directors': set(),
                        'actors': set(),
                        'writers': set(),
                    }

                dict_movie_data = self._add_movie_data(dict_movie_data, row)

            # transform dict of movie dicts to list of movie dicts
            # so that data can be uploaded to ElasticSearch
            list_movie_data: List[dict] = []
            for movie in dict_movie_data.values():
                transformed_movie = self._transform_movie(movie)
                list_movie_data.append(transformed_movie)

            target.send(list_movie_data)

    @coroutine
    def transform_genre(self, target) -> List[dict]:
        """Coroutine process that transforms genre data from postgres_merger
        to the format acceptable for ES.

        Parameters
        ----------
        target : [type]
            Next coroutine process

        Returns
        -------
        List[dict]
            Data ready for upload to ES
        """
        while True:
            data = (yield)
            unique_genre: Set = set()
            list_genre_data: List[dict] = []

            for tuple_row in data:
                # creating dataclass from tuple, that was received from psycopg2
                row = GenreRow(*tuple_row)

                # check if this is the first time the genre is processed
                if row.g_id not in unique_genre:
                    # if it's the first time, add id to the set and add data to list of genres
                    unique_genre.add(row.g_id)
                    list_genre_data.append(
                        {'uuid': row.g_id, 'name': row.name}
                    )

            target.send(list_genre_data)

    @coroutine
    def transform_person(self, target) -> List[dict]:
        """Coroutine process that transforms person data from postgres_merger
        to the format acceptable for ES.

        Parameters
        ----------
        target : [type]
            Next coroutine process

        Returns
        -------
        List[dict]
            Data ready for upload to ES
        """
        while True:
            data = (yield)
            unique_person: Set = set()
            dict_person_data: Dict[str, dict] = {}

            for tuple_row in data:
                # creating dataclass from tuple, that was received from psycopg2
                row = PersonRow(*tuple_row)

                # check if this is the first time the person is processed
                if row.p_id not in unique_person:
                    # if it's the first time, add id to the set and create new person dict
                    unique_person.add(row.p_id)
                    dict_person_data[row.p_id] = {
                        'uuid': row.p_id,
                        'full_name': row.full_name,
                        'actor': [],
                        'writer': [],
                        'director': [],
                    }

                # add data about film to person dict
                dict_person_data[row.p_id][row.role].append(row.f_id)

            # transform dict of person dicts to list of person dicts
            # so that data can be uploaded to ElasticSearch
            list_person_data: List[dict] = []
            for person in dict_person_data.values():
                list_person_data.append(person)

            target.send(list_person_data)

    @coroutine
    def load(self, state_key: str, index: str):
        """Coroutine process that loads data to ES.

        Parameters
        ----------
        state_key : str
            Key of the state record with information about the current offset
        index : str
            Name of the index in ES
        """
        while True:
            data = (yield)
            dict_insert_update = self.loader.check_for_docs(data, index)
            self.logger.info(f"Number to insert: {len(dict_insert_update['not_present'])}")
            self.logger.info(f"Number to update: {len(dict_insert_update['present'])}")
            self.loader.load_to_es(dict_insert_update['not_present'], index)
            self.loader.update_in_es(dict_insert_update['present'], index)
            self._update_offset(state_key, 2)
            if self.switch_offset or self.film_work_update:
                self._reset_offset(state_key, 2)
                self._update_offset(state_key, 1)
                self.switch_offset = False
            self.logger.debug(f'-- Updated {len(data)} {index} rows')

    def etl_movies_person_updated(self, time_modified: datetime):
        """ETL process that updates data in ElasticSearch for 'movie' index if any records in
        person table were modified.

        Parameters
        ----------
        time_modified : datetime
            If record in postgres was updated after this time it will be synchronised with ES
        """
        self.logger.info('ETL movies: started updating for person')
        state_key = self._generate_state_key('etl_movies_person', time_modified)
        state_exists = self._check_state(state_key)
        if not state_exists:
            self._set_initial_state(state_key)

        try:
            data_load = self.load(state_key, 'movies')
            data_transform = self.transform_film(data_load)
            data_extract_merge = self.postgres_merger(
                data_transform,
                self.sql_templates['film_work_for_es']
            )
            data_extract_enrich = self.postgres_enricher(
                data_extract_merge,
                state_key,
                self.sql_templates['film_work_for_updated_person'],
                time_modified
            )
            self.postgres_producer(
                data_extract_enrich,
                state_key,
                self.sql_templates['updated_person'],
                time_modified
            )
        except GeneratorExit:
            self.logger.info('ETL movies: finished updating for person')

    def etl_movies_genre_updated(self, time_modified: datetime):
        """ETL process that updates data in ElasticSearch for 'movie' index if any records in
        genre table were modified.

        Parameters
        ----------
        time_modified : datetime
            If record in postgres was updated after this time it will be synchronised with ES
        """
        self.logger.info('ETL movies: started updating for genre')
        state_key = self._generate_state_key('etl_movies_genre', time_modified)
        state_exists = self._check_state(state_key)
        if not state_exists:
            self._set_initial_state(state_key)

        try:
            data_load = self.load(state_key, 'movies')
            data_transform = self.transform_film(data_load)
            data_extract_merge = self.postgres_merger(
                data_transform,
                self.sql_templates['film_work_for_es']
            )
            data_extract_enrich = self.postgres_enricher(
                data_extract_merge,
                state_key,
                self.sql_templates['film_work_for_updated_genre'],
                time_modified
            )
            self.postgres_producer(
                data_extract_enrich,
                state_key,
                self.sql_templates['updated_genre'],
                time_modified
            )
        except GeneratorExit:
            self.logger.info('ETL movies: finished updating for genre')

    def etl_movies_film_work_updated(self, time_modified: datetime):
        """ETL process that updates data in ElasticSearch for 'movie' index if any records in
        film_work table were modified.

        Parameters
        ----------
        time_modified : datetime
            If record in postgres was updated after this time it will be synchronised with ES
        """
        self.logger.info('ETL movies: started updating for film_work')
        state_key = self._generate_state_key('etl_movies_film_work', time_modified)
        state_exists = self._check_state(state_key)
        if not state_exists:
            self._set_initial_state(state_key)

        self.film_work_update = True
        try:
            data_load = self.load(state_key, 'movies')
            data_transform = self.transform_film(data_load)
            data_extract_merge = self.postgres_merger(
                data_transform,
                self.sql_templates['film_work_for_es']
            )
            self.postgres_producer(
                data_extract_merge,
                state_key,
                self.sql_templates['updated_film_work'],
                time_modified
            )
        except GeneratorExit:
            self.logger.info('ETL movies: finished updating for film_work')

    def etl_genre(self, time_modified: datetime):
        """ETL process that updates data in ElasticSearch for 'genre' index if any records in
        genre table were modified.

        Parameters
        ----------
        time_modified : datetime
            If record in postgres was updated after this time it will be synchronised with ES
        """
        self.logger.info('ETL genre: started updating')
        state_key = self._generate_state_key('etl_genre', time_modified)
        state_exists = self._check_state(state_key)
        if not state_exists:
            self._set_initial_state(state_key)

        self.film_work_update = True
        try:
            data_load = self.load(state_key, 'genre')
            data_transform = self.transform_genre(data_load)
            data_extract_merge = self.postgres_merger(
                data_transform,
                self.sql_templates['genre_for_es']
            )
            self.postgres_producer(
                data_extract_merge,
                state_key,
                self.sql_templates['updated_genre'],
                time_modified
            )
        except GeneratorExit:
            self.logger.info('ETL genre: finished updating')

    def etl_person(self, time_modified: datetime):
        """ETL process that updates data in ElasticSearch for 'person' index if any records in
        genre table were modified.

        Parameters
        ----------
        time_modified : datetime
            If record in postgres was updated after this time it will be synchronised with ES
        """
        self.logger.info('ETL person: started updating')
        state_key = self._generate_state_key('etl_person', time_modified)
        state_exists = self._check_state(state_key)
        if not state_exists:
            self._set_initial_state(state_key)

        self.film_work_update = True
        try:
            data_load = self.load(state_key, 'person')
            data_transform = self.transform_person(data_load)
            data_extract_merge = self.postgres_merger(
                data_transform,
                self.sql_templates['person_for_es']
            )
            self.postgres_producer(
                data_extract_merge,
                state_key,
                self.sql_templates['updated_person'],
                time_modified
            )
        except GeneratorExit:
            self.logger.info('ETL person: finished updating')
