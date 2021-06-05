CREATE SCHEMA IF NOT EXISTS auth;

CREATE TABLE IF NOT EXISTS auth.users (
    id uuid NOT NULL,
    login text NOT NULL,
    password text NOT NULL,
    creation_date timestamp with time zone
);