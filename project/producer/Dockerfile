# Use an official Python runtime
FROM python:3.9-slim

# Developer and maintainer of the project
LABEL maintainer="Aleksandr Klein"

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy requirements.txt into the Docker container
COPY requirements.txt ./

# Install needed Python packages
RUN pip install --upgrade pip \
 && pip install --trusted-host pypi.python.org -r requirements.txt

# Copy the rest of the application's code
COPY . .

# Run producer.py when the container launches
CMD ["python", "producer.py"]
