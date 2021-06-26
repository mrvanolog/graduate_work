CREATE DATABASE "rs-data";
ALTER DATABASE "rs-data" OWNER TO postgres;

\c "rs-data";

CREATE SCHEMA "rs-data";
ALTER SCHEMA "rs-data" OWNER TO postgres;

CREATE TABLE "rs-data".ratings (
    user_id uuid NOT NULL,
    movie_id uuid NOT NULL,
    rating double precision,
    created_at timestamp with time zone
);

ALTER TABLE "rs-data".ratings OWNER TO postgres;


CREATE TABLE "rs-data".movies (
    id uuid NOT NULL,
    title text NOT NULL,
    rating double precision,
    type text NOT NULL,
    genres text[],
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


ALTER TABLE "rs-data".movies OWNER TO postgres;

