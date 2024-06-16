FROM apache/airflow:2.1.0

# Install minio
RUN pip install minio==6.0.2 pandas geopy
