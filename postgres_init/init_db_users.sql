CREATE DATABASE users;
ALTER DATABASE users OWNER TO postgres;

\c users;


CREATE SCHEMA users;
ALTER SCHEMA users OWNER TO postgres;

CREATE TABLE users.users (
    id uuid NOT NULL,
    login text NOT NULL,
    password text NOT NULL,
    creation_date timestamp with time zone
);

ALTER TABLE users.users OWNER TO postgres;