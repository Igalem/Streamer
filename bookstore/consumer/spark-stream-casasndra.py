from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StringType, TimestampType, StructField


# Initialize Spark Session
spark = SparkSession.builder \
        .appName('SparkDataStreaming') \
        .config('spark.jars.packages', "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.4,"
                                       "com.datastax.spark:spark-cassandra-connector_2.12:3.4.1") \
        .config('spark.cassandra.connection.host', 'localhost') \
        .config("spark.sql.streaming.checkpointLocation", "/tmp/checkpoints") \
        .getOrCreate()

# Define Kafka parameters
kafka_bootstrap_servers = "localhost:9092"
kafka_topic = "bookstore_events"

# Define the schema of the incoming data
details_schema = StructType() \
    .add("book_title", StringType()) \
    .add("book_id", StringType())

schema = StructType() \
    .add("event_type", StringType()) \
    .add("timestamp", TimestampType()) \
    .add("details", details_schema)

# Read from Kafka
kafka_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
    .option("subscribe", kafka_topic) \
    .load()

# Extract value as JSON and parse it
events_df = kafka_df.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select(
        col("data.event_type").alias("event_type"),
        col("data.timestamp").alias("timestamp"),
        col("data.details.book_id").alias("book_id"),
        col("data.details.book_title").alias("book_title")
    )

# Write to Cassandra
query = events_df.writeStream \
    .foreachBatch(lambda batch_df, batch_id: batch_df.write \
                  .format("org.apache.spark.sql.cassandra") \
                  .mode("append") \
                  .options(table="events", keyspace="bookstore") \
                  .save()) \
    .outputMode("append") \
    .start()

query.awaitTermination()
