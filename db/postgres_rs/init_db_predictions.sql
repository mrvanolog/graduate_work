CREATE SCHEMA IF NOT EXISTS predictions;

CREATE TABLE IF NOT EXISTS predictions.users (
    user_id uuid NOT NULL,
    rec_movie_id ARRAY
);

CREATE TABLE IF NOT EXISTS predictions.movies (
    movie_id uuid NOT NULL,
    rec_movie_id ARRAY
);