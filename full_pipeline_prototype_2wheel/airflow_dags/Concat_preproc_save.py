from datetime import datetime, timedelta
import json
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from minio import Minio
import os
import requests
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

# Define default_args for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'minio_geocode_etl',
    default_args=default_args,
    description='An ETL pipeline that reads from Minio, processes data, and saves back to Minio',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 1, 1),
    catchup=False,
)

minio_endpoint = "localhost:9000"
access_key = "admin"
secret_key = "password123"
input_bucket_name = "raw"
output_bucket_name = "preprocessed"


def read_json_from_minio(**kwargs):
    ti = kwargs['ti']
    try:
        minio_client = Minio(minio_endpoint, access_key=access_key, secret_key=secret_key, secure=False)
        objects = minio_client.list_objects(input_bucket_name, recursive=True)
        file_list = {obj.object_name[-19:-5]: obj.object_name for obj in objects}
        df_list = []

        for date, object_name in file_list.items():
            json_data = minio_client.get_object(input_bucket_name, object_name)
            json_content = json_data.read().decode('utf-8')
            json_parsed = json.loads(json_content)
            df = create_dataframe_from_json(json_parsed)
            if df is not None:
                df["date"] = pd.to_datetime(date, format='%Y%m%d%H%M%S')
                df_list.append(df)
            else:
                print(f"Failed to create DataFrame from {object_name}")

        if df_list:
            final_df_raw = pd.concat(df_list, ignore_index=True)
            ti.xcom_push(key='final_df_raw', value=final_df_raw)
        else:
            raise ValueError("No DataFrames were created from the JSON files.")
    except Exception as e:
        print(f"An error occurred: {e}")


def create_dataframe_from_json(json_data):
    try:
        extracted_data = []

        for json_obj in json_data:
            extracted_info = {
                'id': json_obj.get('id'),
                'street_address': json_obj['address']['value'].get('streetAddress'),
                'allowed_vehicle_type': json_obj.get('allowedVehicleType', {}).get('value', [None])[0],
                'available_spot_number': json_obj.get('availableSpotNumber', {}).get('value'),
                'data_provider': json_obj.get('dataProvider', {}).get('value'),
                'description': json_obj.get('description', {}).get('value'),
                'latitude': json_obj['location']['value'].get('coordinates', [None, None])[1],
                'longitude': json_obj['location']['value'].get('coordinates', [None, None])[0],
                'occupied_spot_number': json_obj.get('occupiedSpotNumber', {}).get('value'),
                'total_spot_number': json_obj.get('totalSpotNumber', {}).get('value')
            }
            extracted_data.append(extracted_info)

        df = pd.DataFrame(extracted_data)
        return df
    except Exception as e:
        print(f"An error occurred while creating the dataframe: {e}")
        return None


def get_postcode_info_latlon(lat, lon):
    geolocator = Nominatim(user_agent="get_location")
    geocode = RateLimiter(geolocator.reverse, min_delay_seconds=1)
    try:
        location = geocode(f"{lat}, {lon}", exactly_one=True)
        address = location.raw.get('address', {})
        post_code = address.get('postcode', '')
        return pd.Series([post_code])
    except Exception as e:
        return pd.Series([''])


def complete_geocode_table(**kwargs):
    ti = kwargs['ti']
    final_df_raw = ti.xcom_pull(key='final_df_raw', task_ids='read_json_from_minio')
    if final_df_raw is None:
        raise ValueError("final_df_raw is None. Cannot proceed with geocoding.")
    df = final_df_raw[["latitude", "longitude"]].groupby(["latitude", "longitude"]).first().reset_index()
    df["postal_code"] = df.apply(lambda x: get_postcode_info_latlon(x["latitude"], x["longitude"]), axis=1)
    df["postal_code"] = df["postal_code"].str.replace("-", "").astype(int)
    df_match_postcode = pd.read_csv('https://raw.githubusercontent.com/dssg-pt/mp-mapeamento-cp7/main/output_data/cod_post_freg_matched.csv', encoding='utf-8')
    to_geocode = df.merge(df_match_postcode[['CodigoPostal', 'Concelho', 'Freguesia Final (Pós RATF)']], left_on="postal_code", right_on='CodigoPostal', how="left")
    to_geocode = to_geocode.drop(columns=["CodigoPostal"]).rename(columns={"Concelho": "concelho", "Freguesia Final (Pós RATF)": "freguesia"})
    ti.xcom_push(key='to_geocode', value=to_geocode)


def process_geocode_data(**kwargs):
    ti = kwargs['ti']
    final_df_raw = ti.xcom_pull(key='final_df_raw', task_ids='read_json_from_minio')
    to_geocode = ti.xcom_pull(key='to_geocode', task_ids='complete_geocode_table')
    if final_df_raw is None or to_geocode is None:
        raise ValueError("final_df_raw or to_geocode is None. Cannot proceed with processing.")
    try:
        final_df_raw["occupied_perc"] = final_df_raw["occupied_spot_number"] / final_df_raw["total_spot_number"] * 100
        final_df_raw['date'] = pd.to_datetime(final_df_raw['date'])
        final_df_raw.set_index('date', inplace=True)

        window_size = 2

        df_processed = final_df_raw.groupby(['id', 'street_address', 'latitude', 'longitude']).apply(
            lambda x: x.rolling(window=window_size, min_periods=1).agg({
                'occupied_spot_number': ['mean', 'max', 'min'],
                'occupied_perc': ['mean', 'max', 'min']
            })
        ).reset_index()

        df_processed.columns = ['id', 'street_address', 'latitude', 'longitude', 'date',
                                'occupied_spot_number_mean', 'occupied_spot_number_max', 'occupied_spot_number_min',
                                'occupied_perc_mean', 'occupied_perc_max', 'occupied_perc_min']

        df_processed = df_processed.merge(to_geocode[["latitude", "longitude", "concelho", "freguesia"]], on=["latitude", "longitude"], how="left")
        ti.xcom_push(key='df_processed', value=df_processed)
    except Exception as e:
        print(f"An error occurred while processing the data: {e}")


def save_parquet_to_minio(**kwargs):
    ti = kwargs['ti']
    df_processed = ti.xcom_pull(key='df_processed', task_ids='process_geocode_data')
    if df_processed is None:
        raise ValueError("df_processed is None. Cannot proceed with saving.")
    try:
        minio_client = Minio(minio_endpoint, access_key=access_key, secret_key=secret_key, secure=False)
        date = datetime.today().strftime('%Y%m%d%H%M%S')
        parquet_output_path = f"/tmp/2wheel_{date}.parquet"
        object_name = f"twowheel/2wheel_{date}.parquet"

        df_processed.to_parquet(parquet_output_path)
        minio_client.fput_object(output_bucket_name, object_name, parquet_output_path)
        print(f"Preprocessed data is saved as Parquet in the MinIO bucket: {output_bucket_name}/{object_name}")

        if os.path.exists(parquet_output_path):
            os.remove(parquet_output_path)
    except Exception as e:
        print(f"An error occurred: {e}")


# Define the tasks
read_json_task = PythonOperator(
    task_id='read_json_from_minio',
    python_callable=read_json_from_minio,
    provide_context=True,
    dag=dag,
)

complete_geocode_task = PythonOperator(
    task_id='complete_geocode_table',
    python_callable=complete_geocode_table,
    provide_context=True,
    dag=dag,
)

process_geocode_task = PythonOperator(
    task_id='process_geocode_data',
    python_callable=process_geocode_data,
    provide_context=True,
    dag=dag,
)

save_parquet_task = PythonOperator(
    task_id='save_parquet_to_minio',
    python_callable=save_parquet_to_minio,
    provide_context=True,
    dag=dag,
)

# Define task dependencies
read_json_task >> complete_geocode_task >> process_geocode_task >> save_parquet_task
