# Data_Pipeline/pipelines/connections.py
from pymongo import MongoClient
from sqlalchemy import create_engine
from typing import Any

MONGO_URI = "mongodb://localhost:27017"

# Configuration for MongoDB in the movie data pipeline project
MONGO_DB_NAME = "tmdb_data"
MOVIE_COLLECTION = "raw_movies"
USER_COMMENT_COLLECTION = "user_comments"


class MongoConnection:
    def __init__(self, uri: str, db_name: str, collection_name: str):
        self.client = MongoClient(uri)
        self.db      = self.client[db_name]
        self.coll    = self.db[collection_name]

    def close(self) -> None:
        self.client.close()

