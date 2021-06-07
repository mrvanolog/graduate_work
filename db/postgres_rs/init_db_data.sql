CREATE SCHEMA IF NOT EXISTS rs_data;

CREATE TABLE IF NOT EXISTS rs_data.ratings (
    user_id uuid NOT NULL,
    movie_id uuid NOT NULL,
    rating double precision,
    created_at timestamp with time zone
);


CREATE TABLE IF NOT EXISTS content.film_work (
    id uuid NOT NULL,
    title text NOT NULL,
    rating double precision,
    type text NOT NULL,
    genres text[],
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);

