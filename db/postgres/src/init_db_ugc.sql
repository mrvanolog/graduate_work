CREATE SCHEMA IF NOT EXISTS user_content;

CREATE TABLE IF NOT EXISTS user_content.ratings (
    user_id uuid NOT NULL,
    movie_id uuid NOT NULL,
    rating double precision,
    created_at timestamp with time zone
);