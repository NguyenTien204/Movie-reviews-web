from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from kafka_schemas import userlog_schema
from mongo_writer import write_to_mongo
from config.connection import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPICS

def start_click_stream():
    spark = SparkSession.builder \
        .appName("ClickStreamConsumer") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")

    kafka_df = (
        spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS)
        .option("subscribe", KAFKA_TOPICS["click"])
        .option("startingOffsets", "latest")
        .load()
    )

    parsed_df = kafka_df.selectExpr("CAST(value AS STRING) as json_str") \
        .select(from_json(col("json_str"), userlog_schema).alias("data")) \
        .select("data.*")

    parsed_df.writeStream \
        .foreachBatch(lambda df, epoch_id: write_to_mongo(df, epoch_id, "click")) \
        .outputMode("append") \
        .option("checkpointLocation", "./checkpoint/click") \
        .start() \
        .awaitTermination()
