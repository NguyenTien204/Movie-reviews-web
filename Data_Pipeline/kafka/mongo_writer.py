from pymongo import MongoClient
from config.connection import MONGO_URI, MONGO_LOG_DB, MONGO_LOG_COLLECTIONS

client = MongoClient(MONGO_URI)
db = client[MONGO_LOG_DB]

def write_to_mongo(df, epoch_id, topic_type):
    if df.isEmpty():
        print(f"[INFO] Epoch {epoch_id}: No data received.")
        return
    print(f"[INFO] Epoch {epoch_id}: Received {df.count()} rows.")
    collection = db[MONGO_LOG_COLLECTIONS[topic_type]]
    data = df.toJSON().map(lambda j: eval(j)).collect()
    if data:
        collection.insert_many(data)
