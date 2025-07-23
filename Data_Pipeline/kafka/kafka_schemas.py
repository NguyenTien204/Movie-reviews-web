from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType, FloatType, MapType

userlog_schema = StructType([
    StructField("event_id", StringType()),
    StructField("user_id", IntegerType()),
    StructField("session_id", StringType()),
    StructField("movie_id", IntegerType()),
    StructField("event_type", StringType()),
    StructField("event_time", TimestampType()),
    StructField("metadata", MapType(StringType(), StringType()))  # metadata: flexible
])

