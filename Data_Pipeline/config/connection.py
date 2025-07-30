from sqlalchemy import create_engine
from pymongo import MongoClient


POSTGRES_HOST = 'localhost'
POSTGRES_PORT = 5432
POSTGRES_DB = 'movie_db_test'
POSTGRES_USER = 'postgres'
POSTGRES_PASSWORD = '141124'

MONGO_URI = "mongodb://localhost:27017"
MONGO_DB_NAME = "tmdb_data"
MONGO_LOG_DB = "movie_logs"
MONGO_LOG_COLLECTIONS = {
    "click": "click_logs",
    "rating": "rating_logs",
    "trailer": "trailer_logs",
    "search": "search_logs",
    "dwelltime": "dwell_logs"
}
MOVIE_COLLECTION = "raw_movies_test"
USER_COMMENT_COLLECTION = "user_comments"

# Configuration for Kafka in the movie data pipeline project
KAFKA_BOOTSTRAP_SERVERS = 'localhost:9092'
KAFKA_TOPICS = {
    "click": "userlog_click",
    "rating": "userlog_rating",
    "trailer": "userlog_trailer",
    "search": "userlog_search",
    "dwelltime": "userlog_dwelltime"
}

SPARK_APP_NAME = "MovieStreamingProcessor"
SPARK_MASTER = "local[*]"  #"spark://host:port" nếu dùng cluster
SPARK_LOG_LEVEL = "WARN"
SPARK_CLEANED_DATA_PATH = "/tmp/spark_output/cleaned_data"


class PostgresConnection:
    def __init__(self,
                 db: str, user: str, pwd: str,
                 host: str = "localhost", port: int = 5432):
        self.url = f"postgresql://{user}:{pwd}@{host}:{port}/{db}"
        self.engine = create_engine(self.url, pool_pre_ping=True)

    def dispose(self) -> None:
        self.engine.dispose()


class MongoConnection:
    def __init__(self, uri: str, db_name: str, collection_name: str):
        self.client = MongoClient(uri)
        self.db      = self.client[db_name]
        self.coll    = self.db[collection_name]

    def close(self) -> None:
        self.client.close()
