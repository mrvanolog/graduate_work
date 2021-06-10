from pydantic import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = 'recommendation system api'

    postgres_db: str
    postgres_host: str
    postgres_port: str
    postgres_username: str
    postgres_password: str


settings = Settings()
