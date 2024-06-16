import os
import json
from datetime import datetime
import pandas as pd
import warnings
# Disable specific warning categories
warnings.filterwarnings('ignore', category=DeprecationWarning)
from minio import Minio
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# Configs MinIO
minio_endpoint = "localhost:9000"
access_key = "admin"
secret_key = "password123"

# Define the bucket names
input_bucket_name = "raw"
output_bucket_name = "preprocessed"

# Get current date
date = datetime.today().strftime('%Y%m%d%H%M%S')

# Source file for post code freguesia matching
match_postcode_file = 'https://raw.githubusercontent.com/dssg-pt/mp-mapeamento-cp7/main/output_data/cod_post_freg_matched.csv'


def read_json_from_minio(minio_endpoint, access_key, secret_key, bucket_name, object_name):
    try:
        minio_client = Minio(minio_endpoint, access_key=access_key, secret_key=secret_key, secure=False)
        json_data = minio_client.get_object(bucket_name, object_name)
        json_content = json_data.read().decode('utf-8')
        json_parsed = json.loads(json_content)
        return json_parsed
    except Exception as e:
        print(f"An error occurred while reading JSON from MinIO: {e}")
        return None


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


def read_bucket_json_df_concatenate(minio_endpoint, access_key, secret_key, bucket_name):
    try:
        minio_client = Minio(minio_endpoint, access_key=access_key, secret_key=secret_key, secure=False)
        objects = minio_client.list_objects(bucket_name, recursive=True)
        file_list = {obj.object_name[-19:-5]: obj.object_name for obj in objects}

        df_list = []

        for date, object_name in file_list.items():
            try:
                json_data = read_json_from_minio(minio_endpoint, access_key, secret_key, bucket_name, object_name)
                if json_data:
                    df = create_dataframe_from_json(json_data)
                    df["date"] = pd.to_datetime(date, format='%Y%m%d%H%M%S')
                    df_list.append(df)
            except Exception as e:
                print(f"An error occurred while processing object '{object_name}': {e}")

        if df_list:
            return pd.concat(df_list, ignore_index=True)
        else:
            return None
    except Exception as e:
        print(f"An error occurred while reading bucket '{bucket_name}': {e}")
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


def complete_geocode_table(df):
    try:
        df = df[["latitude", "longitude", "total_spot_number"]].groupby(["latitude", "longitude"]).first().reset_index()
        df["postal_code"] = df.apply(lambda x: get_postcode_info_latlon(x["latitude"], x["longitude"]), axis=1)
        df["postal_code"] = df["postal_code"].str.replace("-", "").astype(int)
        try:
            df_match_postcode = pd.read_csv(match_postcode_file, encoding='utf-8')
        except Exception as e:
            print(f"An error occurred while reading the match_postcode file: {e}")
            return None
        to_geocode = df.merge(df_match_postcode[['CodigoPostal', 'Concelho', 'Freguesia Final (Pós RATF)']], left_on="postal_code", right_on='CodigoPostal', how="left")
        to_geocode = to_geocode.drop(columns=["CodigoPostal"]).rename(columns={"Concelho": "concelho", "Freguesia Final (Pós RATF)": "freguesia"})
        return to_geocode
    except Exception as e:
        print(f"An error occurred while completing the geocode table: {e}")
        return None


def process_geocode_data(df_raw, to_geocode):
    try:
        df_raw["occupied_perc"] = df_raw["occupied_spot_number"] / df_raw["total_spot_number"] * 100
        df_raw['date'] = pd.to_datetime(df_raw['date'])
        df_raw.set_index('date', inplace=True)

        window_size = 2

        df_processed = df_raw.groupby(['id', 'street_address', 'latitude', 'longitude']).apply(
            lambda x: x.rolling(window=window_size, min_periods=1).agg({
                'occupied_spot_number': ['mean', 'max', 'min'],
                'occupied_perc': ['mean', 'max', 'min']
            })
        ).reset_index()

        df_processed.columns = ['id', 'street_address', 'latitude', 'longitude', 'date',
                                'occupied_spot_number_mean', 'occupied_spot_number_max', 'occupied_spot_number_min',
                                'occupied_perc_mean', 'occupied_perc_max', 'occupied_perc_min']

        df_processed = df_processed.merge(to_geocode[["latitude", "longitude", "concelho", "freguesia", "total_spot_number"]], on=["latitude", "longitude"], how="left")

        return df_processed
    except Exception as e:
        print(f"An error occurred while processing the data: {e}")
        return None


def save_parquet_to_minio(df, minio_endpoint, access_key, secret_key, bucket_name, secure=False):
    try:
        minio_client = Minio(minio_endpoint, access_key=access_key, secret_key=secret_key, secure=secure)
        date = datetime.today().strftime('%Y%m%d%H%M%S')
        parquet_output_path = f"2wheel_{date}.parquet"
        object_name = f"twowheel/2wheel_{date}.parquet"

        df.to_parquet(parquet_output_path)
        minio_client.fput_object(bucket_name, object_name, parquet_output_path)
        print(f"🎉 Preprocessed data is saved as Parquet in the MinIO bucket: {bucket_name}/{object_name}")

        if os.path.exists(parquet_output_path):
            os.remove(parquet_output_path)
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    try:
        print("✅ Reading JSON from bucket, converting to dataframe and concatenating")
        final_df_raw = read_bucket_json_df_concatenate(minio_endpoint, access_key, secret_key, input_bucket_name)
        if final_df_raw is None:
            raise ValueError("Failed to produce final_df_raw. Exiting the script.")

        print("✅ API call and completing geocode table")
        to_geocode = complete_geocode_table(final_df_raw)
        if to_geocode is None or to_geocode.empty:
            raise ValueError("Failed to produce to_geocode. Exiting the script.")

        print("✅ Geocoding data and saving to MinIO as Parquet file")
        df_processed = process_geocode_data(final_df_raw, to_geocode)
        if df_processed is None or df_processed.empty:
            raise ValueError("Failed to process geocode data. Exiting the script.")

        save_parquet_to_minio(df_processed, minio_endpoint, access_key, secret_key, output_bucket_name)
    except ValueError as e:
        print(e)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
