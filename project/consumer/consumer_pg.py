import os
import json
import psycopg2
import psycopg2.extras
from kafka import KafkaConsumer
from time import sleep

ENV_VARS = {
    'host': os.getenv('POSTGRES_HOST'),
    'port': os.getenv('POSTGRES_PORT'),
    'dbname': os.getenv('POSTGRES_DB'),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD')
}


def setup_database(conn):
    """Create necessary schema and tables if they do not exist."""
    with conn.cursor() as cur:
        cur.execute("""
            CREATE SCHEMA IF NOT EXISTS raw_data;
            CREATE TABLE IF NOT EXISTS raw_data.simulated_stock_prices (
                kafka_partition INTEGER,
                kafka_offset    INTEGER,
                message         TEXT,
                created_at      BIGINT
            );
            CREATE SCHEMA IF NOT EXISTS datamart;
            CREATE TABLE datamart.simulated_stock_prices (
                kafka_partition INTEGER,
                kafka_offset    INTEGER,
                symbol          VARCHAR(10),
                open            NUMERIC(10, 2),
                high            NUMERIC(10, 2),
                low             NUMERIC(10, 2),
                close           NUMERIC(10, 2),
                volume          INTEGER,
                timestamp       TIMESTAMP,
                created_at      BIGINT
            );

        """)
        conn.commit()

def consume_messages(consumer, conn):
    """Process messages from Kafka and insert them into the database."""
    for message in consumer:
        # print(f"Received message from topic {message.topic}, partition {message.partition}, offset {message.offset}")
        # print(f"Message data: {message.value}")

        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO raw_data.simulated_stock_prices (kafka_partition, kafka_offset, message, created_at)
                VALUES (%s, %s, %s, %s);
                """,
                (message.partition, message.offset, json.dumps(message.value), message.timestamp)
            )
            conn.commit()
            process_to_datamart(conn)


def process_to_datamart(conn):
    """Process new entries from raw_data to datamart."""
    with conn.cursor() as cur:
        cur.execute("""
                INSERT INTO datamart.simulated_stock_prices (kafka_partition, kafka_offset, symbol, open, high, low, close, volume, timestamp, created_at)
                SELECT
                    ssp.kafka_partition                           AS kafka_partition,
                    ssp.kafka_offset                              AS kafka_offset,
                    REPLACE(
                        (ssp.message::JSONB->'symbol')::VARCHAR,
                        '"', '')                      AS symbol,
                    CAST(ssp.message::JSONB->'open'   AS NUMERIC) AS open,
                    CAST(ssp.message::JSONB->'high'   AS NUMERIC) AS high,
                    CAST(ssp.message::JSONB->'low'    AS NUMERIC) AS low,
                    CAST(ssp.message::JSONB->'close'  AS NUMERIC) AS close,
                    CAST(ssp.message::JSONB->'volume' AS NUMERIC) AS volume,
                    REPLACE(
                        (ssp.message::JSONB->'timestamp')::VARCHAR,
                        '"', '')::TIMESTAMP           AS timestamp,
                    ssp.created_at                    AS created_at
                
                FROM 
                    raw_data.simulated_stock_prices AS ssp
                
                WHERE 
                    (ssp.kafka_partition, ssp.kafka_offset) > (
                        SELECT 
                            COALESCE(MAX(p.kafka_partition), 0) AS kafka_partition, 
                            COALESCE(MAX(p.kafka_offset), 0)    AS kafka_offset
                       
                        FROM 
                            datamart.simulated_stock_prices AS p);
            """)
        conn.commit()

def main():
    """Initializes database connection, sets up Kafka consumer, and processes incoming messages into PostgreSQL."""
    with psycopg2.connect(**ENV_VARS) as conn:
        setup_database(conn)

        consumer = KafkaConsumer(
            'simulated_stock_prices',
            bootstrap_servers=['kafka:9092'],
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest'
        )

        print(f"Subscribed to topics: {consumer.subscription()}")
        consume_messages(consumer, conn)
