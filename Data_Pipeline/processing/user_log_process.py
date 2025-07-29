from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, window
from pyspark.sql.types import StructType, StringType, IntegerType, TimestampType
import os



PYTHON_PATH = r"C:\Users\Admin\AppData\Local\Programs\Python\Python310\python.exe"
os.environ["PYSPARK_PYTHON"] = PYTHON_PATH
os.environ["PYSPARK_DRIVER_PYTHON"] = PYTHON_PATH

# 1. Tạo Spark session
spark = SparkSession.builder \
    .appName("KafkaStructuredBatch") \
    .appName("ClickStreamConsumer") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1") \
    .config("spark.ui.showConsoleProgress", "true") \
    .config("spark.python.worker.reuse", "true") \
    .config("spark.executorEnv.PYSPARK_PYTHON", PYTHON_PATH) \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")


userlog_schema = StructType() \
    .add("action_type", StringType()) \
    .add("target", StringType()) \
    .add("movie_id", IntegerType()) \
    .add("timestamp", TimestampType()) \
    .add("user_id", IntegerType()) \
    .add("user_agent", StringType())

# 3. Đọc từ Kafka nhiều topic
df_raw = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", ",".join([
        "userlog_click",
        "userlog_rating",
        "userlog_trailer",
        "userlog_search",
        "userlog_dwelltime"
    ])) \
    .option("startingOffsets", "latest") \
    .load()

# 4. Parse JSON từ Kafka message
df_parsed = df_raw.select(
    from_json(col("value").cast("string"), userlog_schema).alias("data"),
    col("topic")
).select("data.*", "topic")

# 5. Gom nhóm theo user_id và thời gian 5 phút
df_grouped = df_parsed \
    .withWatermark("timestamp", "10 minutes") \
    .groupBy(
        window(col("timestamp"), "5 minutes"),
        col("user_id")
    ) \
    .count()  # hoặc thực hiện enrichment, agg,...

# 6. Xuất kết quả ra console để test (sau này sẽ ghi vào PostgreSQL)
query = df_grouped.writeStream \
    .outputMode("update") \
    .trigger(processingTime="5 minutes") \
    .format("console") \
    .option("truncate", "false") \
    .start()

query.awaitTermination()

#run: python -m Data_Pipeline.processing.user_log_process
