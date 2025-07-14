from sqlalchemy import create_engine
from typing import Any

POSTGRES_HOST = 'localhost'
POSTGRES_PORT = 5432

# Configuration for PostgreSQL in the movie data pipeline project
POSTGRES_DB = 'movie_db'
POSTGRES_USER = 'postgres'
POSTGRES_PASSWORD = '141124'

class PostgresConnection:
    def __init__(self,
                 db: str, user: str, pwd: str,
                 host: str = "localhost", port: int = 5432):
        self.url = f"postgresql://{user}:{pwd}@{host}:{port}/{db}"
        self.engine = create_engine(self.url)

    def dispose(self) -> None:
        self.engine.dispose()