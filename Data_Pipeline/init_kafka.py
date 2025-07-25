from kafka.admin import KafkaAdminClient, NewTopic
from kafka import KafkaProducer
import json
import time
from config.connection import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPICS

def create_kafka_topics():
    admin_client = KafkaAdminClient(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        client_id='create_topic_script'
    )

    existing_topics = admin_client.list_topics()
    new_topics = []

    for topic_name in KAFKA_TOPICS.values():
        if topic_name not in existing_topics:
            print(f"[INFO] Creating topic: {topic_name}")
            new_topics.append(NewTopic(name=topic_name, num_partitions=1, replication_factor=1))

    if new_topics:
        admin_client.create_topics(new_topics=new_topics)
    else:
        print("[INFO] All topics already exist.")

def send_test_data_to_topic(topic_key: str, json_file_path: str):
    topic = KAFKA_TOPICS[topic_key]
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    with open(json_file_path, 'r', encoding='utf-8') as f:
        data_list = json.load(f)

    for i, record in enumerate(data_list):
        producer.send(topic, value=record)
        print(f"[SENT] ({i+1}) -> {record}")
        time.sleep(0.5)  # Delay để dễ theo dõi stream

    producer.flush()
    print("[DONE] Finished sending test data.")

if __name__ == "__main__":
    create_kafka_topics()
    send_test_data_to_topic("click", "D:/WorkSpace/Do-an-2/Data_Pipeline/test_click_data.json")
