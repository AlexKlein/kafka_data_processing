import os
import time

from datetime import datetime

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import *

MODE = "DATABASE"

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
SPARK_MASTER_URL = os.getenv("SPARK_MASTER_URL")

KAFKA_TOPIC = "simulated_stock_prices"
SCALA_VERSION = '2.12'
SPARK_VERSION = '3.2.1'
POSTGRES_VERSION = '42.5.0'

PACKAGES = [
    f"org.apache.spark:spark-sql-kafka-0-10_{SCALA_VERSION}:{SPARK_VERSION}",
    f"org.apache.spark:spark-token-provider-kafka-0-10_{SCALA_VERSION}:{SPARK_VERSION}",
    "org.apache.kafka:kafka-clients:3.7.0",
    f"org.postgresql:postgresql:{POSTGRES_VERSION}"
]

POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_PORT = os.getenv('POSTGRES_PORT')
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')

POSTGRES_TABLE = "raw_data.simulated_stock_prices_spark"


def _write_streaming(df, epoch_id):
    df .write \
        .format("jdbc") \
        .mode("append") \
        .option("url", f"jdbc:postgresql://{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}") \
        .option("driver", "org.postgresql.Driver") \
        .option("dbtable", POSTGRES_TABLE) \
        .option("user", POSTGRES_USER) \
        .option("password", POSTGRES_PASSWORD) \
        .save()


def main():
    """Initializes a Spark session and writes Stream data to predefined storage."""
    try:
        spark = SparkSession.builder \
            .appName("KafkaToSparkConsumer") \
            .master(SPARK_MASTER_URL) \
            .config("spark.jars.packages", ",".join(PACKAGES)) \
            .getOrCreate()

        spark.sparkContext.setLogLevel("ERROR")

        # Define the schema of the incoming data
        stockSchema = StructType([
            StructField("symbol", StringType()),
            StructField("open", DoubleType()),
            StructField("high", DoubleType()),
            StructField("low", DoubleType()),
            StructField("close", DoubleType()),
            StructField("volume", IntegerType()),
            StructField("timestamp", StringType())
        ])

        df = spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
            .option("subscribe", KAFKA_TOPIC) \
            .option("startingOffsets", "earliest") \
            .load() \
            .select(from_json(col("value").cast("string"), stockSchema).alias("data")) \
            .select("data.*")

        if MODE == "CONSOLE":
            # Write data to console for debugging
            df.writeStream \
                .format("console") \
                .start()
        elif MODE == "CSV":
            current_date = datetime.today().strftime('%Y-%m-%d')

            # Write data to a CSV file
            df.writeStream \
                .format("csv") \
                .outputMode("append") \
                .option("path", f"/tmp/data/simulated_stock_prices/{current_date}") \
                .option("checkpointLocation", "/tmp/checkpoint") \
                .start()
        elif MODE == "DATABASE":
            df.writeStream \
                .trigger(processingTime='5 seconds') \
                .outputMode('append') \
                .foreachBatch(_write_streaming) \
                .start()


    except Exception as e:
        print(f"An error occurred: {e}")
