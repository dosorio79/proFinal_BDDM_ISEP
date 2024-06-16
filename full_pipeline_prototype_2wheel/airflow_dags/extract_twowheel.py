from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import requests
import json
from minio import Minio
from io import BytesIO

# Define the default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2022, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Base URL and API params
api_url = "https://broker.fiware.urbanplatform.portodigital.pt/v2/entities"
api_params = {
    'q': 'allowedVehicleType==twoWheeledVehicle',
    'type': 'OnStreetParking',
    'limit': '1000'
}

# Define the MinIO endpoint URL and access keys
minio_endpoint = "minio:9000"
access_key = "admin"
secret_key = "password123"

# Define the bucket name
bucket_name = "raw"

# Function to fetch data from API
def get_data_from_api():
    try:
        response = requests.get(api_url, params=api_params)
        print(f"API Response Code: {response.status_code}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"An error occurred: {req_err}")
    return None

# Function to save JSON data to MinIO
def save_json_to_minio():
    try:
        # Fetch data from API
        json_data = get_data_from_api()

        if json_data is None:
            print("No data fetched from API.")
            return

        # Generate a dynamic object name based on the current timestamp
        date = datetime.now().strftime('%Y%m%d%H%M%S')
        object_name = f"twowheel/twowheel_{date}.json"

        # Create Minio client
        minio_client = Minio(minio_endpoint, access_key=access_key, secret_key=secret_key, secure=False)

        # Check if the bucket already exists
        if not minio_client.bucket_exists(bucket_name):
            # If not, create the bucket
            minio_client.make_bucket(bucket_name)

        # Convert the json_data to a string and then to bytes
        json_string = json.dumps(json_data)
        json_bytes = json_string.encode('utf-8')

        # Convert bytes to a byte stream
        byte_stream = BytesIO(json_bytes)

        # Save the json_data to the MinIO bucket
        minio_client.put_object(bucket_name, object_name, byte_stream, length=len(json_bytes), content_type='application/json')

        print(f"'{object_name}' is successfully uploaded to bucket '{bucket_name}'.")

    except Exception as e:
        print(f"An error occurred while saving JSON to MinIO: {e}")

# Define the Airflow DAG
dag = DAG(
    'fetch_and_save_data_to_minio',
    default_args=default_args,
    description='Fetch data from API and save to MinIO',
    schedule_interval=None,  # Define your desired schedule interval here
)

# Define the tasks in the DAG
fetch_data_task = PythonOperator(
    task_id='fetch_data_from_api',
    python_callable=get_data_from_api,
    dag=dag,
)

save_to_minio_task = PythonOperator(
    task_id='save_to_minio',
    python_callable=save_json_to_minio,
    dag=dag,
)

# Define task dependencies
fetch_data_task >> save_to_minio_task
