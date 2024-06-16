import requests
import json
from minio import Minio
from io import BytesIO

### Configs API ###

# Base URL
api_url = "https://broker.fiware.urbanplatform.portodigital.pt/v2/entities"

# API params
api_params = {
    'q': 'allowedVehicleType==twoWheeledVehicle',
    'type': 'OnStreetParking',
    'limit': '1000'
}

### Configs MinIO ###
# Define the MinIO endpoint URL and access keys
minio_endpoint = "localhost:9000"
access_key = "admin"
secret_key = "password123"

# Define the bucket name and object name
bucket_name = "raw"
object_name = "twowheel/twowheel.json"
# Function to fetch data from API
def get_data_from_api(api_url, api_params):
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
def save_json_to_minio(minio_endpoint, access_key, secret_key, bucket_name, object_name, json_data):
    try:
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
    return None

# Fetch data from API
json_data = get_data_from_api(api_url, api_params)
# Save the JSON data to MinIO
save_json_to_minio(minio_endpoint, access_key, secret_key, bucket_name, object_name, json_data)
