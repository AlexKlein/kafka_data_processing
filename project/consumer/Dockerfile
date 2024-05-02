# Use an official Python runtime
FROM python:3.9-slim

# Developer and maintainer of the project
LABEL maintainer="Aleksandr Klein"

# Define software versions in ARG variables
ARG JAVA_VERSION="17"
ARG SCALA_VERSION="2.12"
ARG SPARK_VERSION="3.5.1"
ARG HADOOP_VERSION="3.4.0"
ARG SPARK_SQL_KAFKA_VERSION="3.2.1"
ARG KAFKA_CLIENTS_VERSION="3.7.0"
ARG POSTGRES_VERSION="42.5.0"

# Set the working directory in the container
WORKDIR /usr/src/app

# Update packages and install necessary dependencies
RUN apt-get update \
 && apt install wget -y \
 && apt-get install software-properties-common -y \
 && apt-add-repository 'deb http://security.debian.org/debian-security stretch/updates main'

# Install Java and handle potential dpkg errors
RUN apt-get install openjdk-${JAVA_VERSION}-jdk -y \
 && dpkg --configure -a || true \
 && mv /var/lib/dpkg/info/openjdk-${JAVA_VERSION}-jre-headless:amd64.* /tmp \
 && mv /var/lib/dpkg/info/openjdk-${JAVA_VERSION}-jre:amd64.* /tmp \
 && mv /var/lib/dpkg/info/openjdk-${JAVA_VERSION}-jdk:amd64.* /tmp \
 && dpkg --configure -a || true \
 && apt-get install openjdk-${JAVA_VERSION}-jdk -y

# Install Scala
RUN apt-get install scala -y

# Setup Spark directory
RUN wget --no-check-certificate https://dlcdn.apache.org/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop3.tgz \
 && tar -xzf spark-${SPARK_VERSION}-bin-hadoop3.tgz \
 && mkdir /opt/spark \
 && mv spark-${SPARK_VERSION}-bin-hadoop3/* /opt/spark \
 && rm spark-${SPARK_VERSION}-bin-hadoop3.tgz \
 && rm -rf spark-${SPARK_VERSION}-bin-hadoop3

# Setup Hadoop directory
RUN wget --no-check-certificate https://downloads.apache.org/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz \
 && tar -xzf hadoop-${HADOOP_VERSION}.tar.gz \
 && mkdir /usr/local/hadoop \
 && mv hadoop-${HADOOP_VERSION}/* /usr/local/hadoop \
 && rm hadoop-${HADOOP_VERSION}.tar.gz \
 && mkdir /usr/local/hadoop/logs

# Download JARs for Spark
RUN wget -P /opt/spark/jars https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_${SCALA_VERSION}/${SPARK_SQL_KAFKA_VERSION}/spark-sql-kafka-0-10_${SCALA_VERSION}-${SPARK_SQL_KAFKA_VERSION}.jar \
 && wget -P /opt/spark/jars https://repo.maven.apache.org/maven2/org/apache/kafka/kafka-clients/${KAFKA_CLIENTS_VERSION}/kafka-clients-${KAFKA_CLIENTS_VERSION}.jar \
 && wget -P /opt/spark/jars https://repo1.maven.org/maven2/org/apache/spark/spark-token-provider-kafka-0-10_${SCALA_VERSION}/${SPARK_SQL_KAFKA_VERSION}/spark-token-provider-kafka-0-10_${SCALA_VERSION}-${SPARK_SQL_KAFKA_VERSION}.jar \
 && wget -P /opt/spark/jars https://jdbc.postgresql.org/download/postgresql-${POSTGRES_VERSION}.jar

# Set Java and Spark executables are executable
RUN chmod -R 755 /usr/lib/jvm/java-${JAVA_VERSION}-openjdk-amd64/bin \
 && chmod -R 755 /opt/spark

# Set environment variables
ENV JAVA_HOME="/usr/lib/jvm/java-${JAVA_VERSION}-openjdk-amd64"
ENV PATH="${PATH}:$JAVA_HOME/bin"
ENV _JAVA_OPTIONS="-Xmx512M"
ENV SPARK_HOME="/opt/spark"
ENV PATH="${PATH}:$SPARK_HOME/bin:$SPARK_HOME/sbin"
ENV PYTHONPATH="$SPARK_HOME/python"
ENV PYSPARK_PYTHON="$SPARK_HOME/python"
ENV PYSPARK_DRIVER_PYTHON="$SPARK_HOME/python"
ENV HADOOP_HOME="/usr/local/hadoop"
ENV PATH="$PATH:$HADOOP_HOME/sbin:$HADOOP_HOME/bin"

# Copy requirements.txt into the Docker container
COPY requirements.txt ./

# Install needed Python packages
RUN pip install --upgrade pip \
 && pip install --trusted-host pypi.python.org -r requirements.txt

# Copy the rest of the application's code
COPY . .

# Run consumer.py when the container launches
CMD ["python", "consumer.py"]
