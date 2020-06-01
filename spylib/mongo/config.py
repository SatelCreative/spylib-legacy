from typing import Optional
from pydantic import BaseSettings


class Configuration(BaseSettings):
    host: str = 'mongo'
    port: int = 27017
    dbname: str = 'sbpim'
    username: Optional[str] = None
    password: Optional[str] = None
    ssl: bool = False
    ssl_ca_cert: Optional[str] = None

    class Config:
        env_prefix = 'MONGO_'


conf = Configuration()
