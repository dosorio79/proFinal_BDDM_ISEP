from minio import Minio
from io import BytesIO
import pandas as pd
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import SQLAlchemyError

# Configs MinIO
minio_endpoint = "localhost:9000"
access_key = "admin"
secret_key = "password123"
input_bucket_name = "preprocessed"
object_name_2wheel = "twowheel/2wheel_20240610230610.parquet"

# Configs PostgreSQL
host = 'localhost'
port = 5432
database = 'datawarehouse'
schema = 'testschema1'
user = 'postgres'
password = 'password123'


def read_parquet_from_minio(minio_endpoint, access_key, secret_key, bucket_name, object_name):
    try:
        minio_client = Minio(minio_endpoint, access_key=access_key, secret_key=secret_key, secure=False)
        response = minio_client.get_object(bucket_name, object_name)
        data = response.read()
        df = pd.read_parquet(BytesIO(data))
        response.close()
        response.release_conn()
        return df
    except Exception as e:
        print(f"An error occurred while reading Parquet from MinIO: {e}")
        return None


def connect_to_postgresql(host, port, database, user, password, schema):
    db_url = f'postgresql://{user}:{password}@{host}:{port}/{database}'
    try:
        engine = create_engine(db_url, connect_args={"options": f"-csearch_path={schema}"})
        print("Connected to PostgreSQL successfully!")
        return engine
    except Exception as e:
        print(f"An error occurred while connecting to PostgreSQL: {e}")
        return None


def populate_tables(data, engine, schema):
    try:
        data.columns = map(str.lower, data.columns)
        data['locationid'] = data.groupby(['latitude', 'longitude']).ngroup() + 1

        metadata = MetaData(schema=schema)
        metadata.reflect(bind=engine)
        dim_location = Table('dimlocation', metadata, autoload_with=engine, schema=schema)
        fact_two_wheel = Table('facttwowheel', metadata, autoload_with=engine, schema=schema)

        with engine.connect() as connection:
            transaction = connection.begin()
            try:
                unique_locations = data[['locationid', 'latitude', 'longitude', 'concelho', 'freguesia']].drop_duplicates()
                location_inserts = unique_locations.to_dict(orient='records')
                insert_statement = pg_insert(dim_location).values(location_inserts)
                upsert_statement = insert_statement.on_conflict_do_nothing(index_elements=['latitude', 'longitude'])
                connection.execute(upsert_statement)
                transaction.commit()
            except SQLAlchemyError as e:
                transaction.rollback()
                print(f"Error during DimLocation insertion: {e}")
                return False

            transaction = connection.begin()
            try:
                if not data.empty:
                    fact_inserts = []
                    for _, row in data.iterrows():
                        fact_inserts.append({
                            'date': row['date'].date(),
                            'latitude': row['latitude'],
                            'longitude': row['longitude'],
                            'meanoccupation': row['occupied_spot_number_mean'],
                            'percentoccupation': row['occupied_perc_mean'],
                            'minoccupation': row['occupied_spot_number_min'],
                            'maxoccupation': row['occupied_spot_number_max'],
                            'totalspotnumber': row['total_spot_number'],
                            'locationid': row['locationid']
                        })
                    connection.execute(pg_insert(fact_two_wheel).on_conflict_do_nothing(), fact_inserts)
                    transaction.commit()
                else:
                    print("No data to insert into FactTwoWheel.")
                    return False
            except SQLAlchemyError as e:
                transaction.rollback()
                print(f"Error during FactTwoWheel insertion: {e}")
                return False

        print("🎉 Data insertion completed successfully!")
        return True
    except KeyError as e:
        print(f"Column not found in the DataFrame: {e}")
        return False
    except SQLAlchemyError as e:
        print(f"Error with SQLAlchemy: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False


if __name__ == "__main__":
    try:
        print("✅ Reading preprocessed parquet file from MinIO")
        data = read_parquet_from_minio(minio_endpoint, access_key, secret_key, input_bucket_name, object_name_2wheel)
        if data is None:
            raise ValueError("Failed to read data from MinIO. Exiting the script.")

        print("✅ Connecting to postgressql")
        engine = connect_to_postgresql(host, port, database, user, password, schema)
        if engine is None:
            raise ValueError("Failed to connect to PostgreSQL. Exiting the script.")

        print("✅ Populating tables")
        success = populate_tables(data, engine, schema)
        if not success:
            raise ValueError("Failed to populate tables. Exiting the script.")

    except ValueError as e:
        print(e)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
