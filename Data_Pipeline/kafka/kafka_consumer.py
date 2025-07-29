from kafka import KafkaConsumer
import json
import threading

KAFKA_TOPICS = [
    "userlog_click",
    "userlog_rating",
    "userlog_trailer",
    "userlog_search",
    "userlog_dwelltime"
]

def process_message(topic, message):
    print(f"[{topic}] {message}")

def start_consumer():
    consumer = KafkaConsumer(
        *KAFKA_TOPICS,  # dấu * để unpack list
        bootstrap_servers='localhost:9092',
        auto_offset_reset='latest',
        enable_auto_commit=True,
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        group_id="pipeline-consumer-group"
    )

    print("[Kafka Consumer] Đang lắng nghe các topic:", KAFKA_TOPICS)

    for msg in consumer:
        process_message(msg.topic, msg.value)

# Nếu muốn chạy riêng:
if __name__ == "__main__":
    start_consumer()
