CREATE DATABASE movies;
ALTER DATABASE movies OWNER TO postgres;

\c movies;

CREATE SCHEMA content;
ALTER SCHEMA content OWNER TO postgres;

CREATE TABLE content.film_work (
    id uuid NOT NULL,
    title text NOT NULL,
    description text,
    creation_date date,
    certificate text,
    file_path text,
    rating double precision,
    type text NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);

ALTER TABLE content.film_work OWNER TO postgres;

CREATE TABLE content.genre (
    id uuid NOT NULL,
    name text NOT NULL,
    description text,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);

ALTER TABLE content.genre OWNER TO postgres;

CREATE TABLE content.genre_film_work (
    id uuid NOT NULL,
    film_work_id uuid NOT NULL,
    genre_id uuid NOT NULL,
    created_at timestamp with time zone
);

ALTER TABLE content.genre_film_work OWNER TO postgres;

CREATE TABLE content.person (
    id uuid NOT NULL,
    full_name text NOT NULL,
    birth_date date,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);

ALTER TABLE content.person OWNER TO postgres;

CREATE TABLE content.person_film_work (
    id uuid NOT NULL,
    film_work_id uuid NOT NULL,
    person_id uuid NOT NULL,
    role text NOT NULL,
    created_at timestamp with time zone
);

ALTER TABLE content.person_film_work OWNER TO postgres;