from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from kafka.kafka_schemas import userlog_schema
from kafka.mongo_writer import write_to_mongo
from config.connection import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPICS
import os

PYTHON_PATH = r"C:\Users\Admin\AppData\Local\Programs\Python\Python310\python.exe"
os.environ["PYSPARK_PYTHON"] = PYTHON_PATH
os.environ["PYSPARK_DRIVER_PYTHON"] = PYTHON_PATH

def start_click_stream():
    spark = SparkSession.builder \
    .appName("ClickStreamConsumer") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1") \
    .config("spark.ui.showConsoleProgress", "true") \
    .config("spark.python.worker.reuse", "true") \
    .config("spark.executorEnv.PYSPARK_PYTHON", PYTHON_PATH) \
    .getOrCreate()


    spark.sparkContext.setLogLevel("WARN")

    kafka_df = (
        spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS)
        .option("subscribe", KAFKA_TOPICS["click"])
        .option("startingOffsets", "earliest")
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
