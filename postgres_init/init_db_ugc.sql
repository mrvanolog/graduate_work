CREATE DATABASE ugc;
ALTER DATABASE ugc OWNER TO postgres;

\c ugc;

CREATE SCHEMA user_content;
ALTER SCHEMA user_content OWNER to postgres;

CREATE TABLE user_content.ratings (
    user_id uuid NOT NULL,
    movie_id uuid NOT NULL,
    rating double precision,
    created_at timestamp with time zone
);

ALTER TABLE user_content.ratings OWNER TO postgres;