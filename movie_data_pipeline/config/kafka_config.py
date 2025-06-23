# Configuration for Kafka in the movie data pipeline project
KAFKA_BOOTSTRAP_SERVERS = 'localhost:9092'

# Kafka topic names for movie data and user logs
KAFKA_TOPIC_MOVIE = 'movie'
KAFKA_TOPIC_USER_LOGS = 'user_logs'

# Kafka consumer group for processing movie data
KAFKA_CONSUMER_GROUP = 'movie_consumer_group'
