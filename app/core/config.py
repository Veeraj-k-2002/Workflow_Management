from pydantic_settings import BaseSettings
import os
class Settings(BaseSettings):
    PG_USERNAME: str 
    PG_PASSWORD: str 
    PG_HOST: str 
    PG_PORT: str 
    DATABASE_NAME: str 
    SECRET_KEY: str 
    ALGORITHM: str 
    ACCESS_TOKEN_EXPIRE_MINUTES: int 
    REFRESH_TOKEN_EXPIRE_DAYS : int
    


    class Config:
        env_file = ".env"
settings = Settings()

class CustomAPIException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail