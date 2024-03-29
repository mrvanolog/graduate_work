from pydantic import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = 'recommendation system api'

    postgres_db: str
    postgres_host: str
    postgres_port: str
    postgres_user: str
    postgres_password: str

    secret_key: str
    algorithm: str = 'HS256'


settings = Settings()
