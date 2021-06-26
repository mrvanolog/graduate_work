CREATE DATABASE "rs-predictions";
ALTER DATABASE "rs-predictions" OWNER TO postgres;

\c "rs-predictions";

CREATE SCHEMA "rs-predictions";
ALTER SCHEMA "rs-predictions" OWNER TO postgres;

CREATE TABLE "rs-predictions".users (
    user_id uuid NOT NULL,
    rec_movie_id text[]
);

ALTER TABLE "rs-predictions".users OWNER TO postgres;

CREATE TABLE "rs-predictions".movies (
    movie_id uuid NOT NULL,
    rec_movie_id text[]
);

ALTER TABLE "rs-predictions".movies OWNER TO postgres;