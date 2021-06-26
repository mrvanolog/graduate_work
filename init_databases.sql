CREATE DATABASE content;
GRANT ALL PRIVILEGES ON DATABASE content TO postgres;

CREATE DATABASE ugc;
GRANT ALL PRIVILEGES ON DATABASE ugc TO postgres;

CREATE DATABASE "rs-data";
GRANT ALL PRIVILEGES ON DATABASE "rs-data" TO postgres;
CREATE TABLE IF NOT EXISTS "rs-data.ratings" (
    user_id uuid NOT NULL,
    movie_id uuid NOT NULL,
    rating double precision,
    created_at timestamp with time zone
);


CREATE TABLE IF NOT EXISTS "rs-data.movies" (
    id uuid NOT NULL,
    title text NOT NULL,
    rating double precision,
    type text NOT NULL,
    genres text[],
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);



CREATE DATABASE users;
GRANT ALL PRIVILEGES ON DATABASE users TO postgres;
CREATE DATABASE "rs-predictions";
GRANT ALL PRIVILEGES ON DATABASE "rs-predictions" TO postgres;

CREATE TABLE IF NOT EXISTS "rs-predictions.users" (
    user_id uuid NOT NULL,
    rec_movie_id text[]
);

CREATE TABLE IF NOT EXISTS "rs-predictions.movies" (
    movie_id uuid NOT NULL,
    rec_movie_id text[]
);
