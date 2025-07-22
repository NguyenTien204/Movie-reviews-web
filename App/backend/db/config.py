from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

POSTGRES_HOST = 'localhost'
POSTGRES_PORT = 5432

# Configuration for PostgreSQL in the movie data pipeline project
POSTGRES_DB = 'movie_db'
POSTGRES_USER = 'postgres'
POSTGRES_PASSWORD = '141124'
POSTGRES_URL = 'postgresql+psycopg2://postgres:141124@localhost:5432/userdb'

class PostgresConnection:
    def __init__(self,
                 db: str, user: str, pwd: str,
                 host: str = "localhost", port: int = 5432):
        self.url = f"postgresql://{user}:{pwd}@{host}:{port}/{db}"
        self.engine = create_engine(self.url)

    def dispose(self) -> None:
        self.engine.dispose()

    @staticmethod
    def get_connection_string() -> str:
        db = POSTGRES_DB
        user = POSTGRES_USER
        pwd = POSTGRES_PASSWORD
        host = POSTGRES_HOST
        port = POSTGRES_PORT
        return f"postgresql://{user}:{pwd}@{host}:{port}/{db}"





engine = create_engine(POSTGRES_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()