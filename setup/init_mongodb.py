# setup/init_mongodb.py
from pymongo import MongoClient
from Data_Pipeline.config.connection import MONGO_DB_NAME, MOVIE_COLLECTION #USER_COMMENT_COLLECTION


def create_collections():
    print("[3/3] Creating MongoDB collections...")
    
    client = MongoClient("mongodb://localhost:27017/")
    db = client[MONGO_DB_NAME]

    # Tạo collection nếu chưa có
    collections = db.list_collection_names()
    if MOVIE_COLLECTION not in collections:
        db.create_collection(MOVIE_COLLECTION)
        print(f"[Y] '{MOVIE_COLLECTION}' collection created.")
    else:
        print(f"[i] '{MOVIE_COLLECTION}' collection already exists.")

    client.close()

if __name__ == "__main__":
    create_collections()
