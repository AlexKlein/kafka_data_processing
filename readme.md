# Kafka and Spark Data Processing Project

This project demonstrates real-time data processing using Apache Kafka for message queuing and Apache Spark for data processing and analytics.

## Components

1. **Kafka**: Used for message queuing and streaming.
2. **Spark**: Handles processing of streaming data.
3. **PostgreSQL**: Acts as the data warehouse to store processed data.
4. **Data Producer**: Simulates stock price data and sends it to Kafka.
5. **Data Consumer**: Consumes messages from Kafka and processes them using PostgreSQL and Spark.

## Build and Run

When you need to start the app with all infrastructure, you have to make this steps:
1. Correct your credential files in the [yml-file](./project/docker-compose.yml).
2. Change to the directory `cd project` to stay in the same folder as `docker-compose.yml`.
3. Run the following: `docker-compose up -d --build` command. Give it some time. Your app, tables, and Airflow will soon be ready.

## Services

### Producer Service

The producer simulates stock price data and sends it to a Kafka topic named `simulated_stock_prices`. It generates new data every second for different stock symbols like `AAPL`, `MSFT`, etc.

### Consumer Service

The consumer service runs two main threads:

1. **PostgreSQL Consumer**: Consumes data from Kafka and directly inserts it into PostgreSQL for long-term storage.
2. **Spark Consumer**: Consumes the same Kafka topic and processes data using Spark, writing results to Console, CSV or PostgreSQL, depends on a switcher.

## Monitoring and Management

Kafka and Zookeeper provide built-in management interfaces.

Spark's operations can be monitored via the [Spark UI](http://localhost:8080).

## Logs

Logs for each service can be accessed through the Docker container logs for detailed debugging and monitoring.

## Conclusion

This project is a robust example of real-time data processing using modern technologies like Apache Kafka and Apache Spark. It is scalable, easy to deploy, and provides a solid foundation for processing streaming data.
