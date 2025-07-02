import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from pymongo import MongoClient
from kafka import KafkaProducer
import json
from bson import json_util

from config.mongo_config import MONGO_URI, MONGO_DB_NAME, MOVIE_COLLECTION, USER_COMMENT_COLLECTION
from config.kafka_config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_CONSUMER_GROUP, KAFKA_TOPIC_MOVIE, KAFKA_TOPIC_USER_LOGS


# Connect to mongoDB
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[MONGO_DB_NAME]
collection = db[MOVIE_COLLECTION]


# Connect to kafka
producer = KafkaProducer(
    bootstrap_servers = KAFKA_BOOTSTRAP_SERVERS,
    value_serializer = lambda v: json.dumps(v, default=json_util.default).encode('utf-8')
)

# Read data from MongoDB to kafka
# Lắng nghe sự kiện real-time
with collection.watch() as stream:
    for change in stream:
        # Gửi toàn bộ thông tin change vào Kafka
        producer.send('movie', change)
        print("Sent to Kafka:", change)
    
producer.flush()
print("All documents send")