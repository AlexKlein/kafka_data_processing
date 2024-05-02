import os
import json
import time
import random
from datetime import datetime
from kafka import KafkaProducer
from dataclasses import dataclass, asdict


KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")

@dataclass
class StockData:
    """Data class to hold stock data points."""
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    timestamp: str

    @staticmethod
    def generate(symbol: str):
        """Generates a simulated stock price data point for a given symbol."""
        price = round(random.uniform(100, 500), 2)
        high = round(price + random.uniform(0, 10), 2)
        low = round(price - random.uniform(0, 10), 2)
        close = round(random.uniform(low, high), 2)
        volume = random.randint(100000, 500000)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return StockData(symbol, price, high, low, close, volume, timestamp)

def main():
    """Initializes the Kafka producer, generates, and sends stock data to Kafka every second."""
    time.sleep(60)

    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
        value_serializer=lambda v: json.dumps(asdict(v)).encode('utf-8')
    )

    stock_symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]

    while True:
        for symbol in stock_symbols:
            stock_data = StockData.generate(symbol)
            producer.send('simulated_stock_prices', value=stock_data)
            print(f"Sent simulated data for {symbol} to Kafka: {asdict(stock_data)}")
            time.sleep(1)  # Generate new data every second for each symbol

if __name__ == "__main__":
    main()
