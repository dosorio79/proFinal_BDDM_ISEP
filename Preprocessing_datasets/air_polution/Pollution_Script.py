# Imports
import pandas as pd
import os
import numpy as np

#Localização do File .xlsx
os.chdir(r"C:/Users/Tiago/Documents/PG - Big Data & Decision Making/09. Seminars")


# Ler Excel num Dataframe
df_pol = pd.read_excel("urban-platform-air-quality-2022.xlsx")

# Drop de colunas desnecessárias
df_pol = df_pol.drop(columns=['date_observed', 'time_observed'])


# Converter 'timestamp' para datetime
df_pol['timestamp'] = pd.to_datetime(df_pol['timestamp'])

# Extrair data e hora do 'timestamp'
df_pol['date'] = df_pol['timestamp'].dt.date
df_pol['hour'] = df_pol['timestamp'].dt.hour

# Drop da coluna 'timestamp'
df_pol = df_pol.drop(columns=['timestamp'])

# Conversão da coluna 'name' para string
df_pol['name'] = df_pol['name'].astype(str)

# Remover linhas com valores NaN
df_pol = df_pol.dropna()

# Agregação das colunas 'date', 'hour' e 'name' para fazer média das variáveis
hourly_mean = df_pol.groupby(['date', 'hour','name']).mean().reset_index()

# GroupBy das colunas 'date' e 'name' para saber max e min
daily_min = df_pol.groupby(['date','name']).min().reset_index()
daily_max = df_pol.groupby(['date','name']).max().reset_index()

# Fazer merge dos dataframes de 'daily_min', 'daily_max' e 'hourly_mean' no dataframe final
df_pollution_day = df_pol.merge(daily_min, on=['date', 'name'], suffixes=('', '_min_day'))
df_pollution_day = df_pollution_day.merge(daily_max, on=['date', 'name'], suffixes=('', '_max_day'))
df_pollution_hour = df_pol.merge(hourly_mean, on=['date', 'hour', 'name'], how='right', suffixes=('', '_mean_hour'))

# Drop de colunas criadas com os sufixos definidos + colunas das variaveis de cálculo (já não necessárias)
df_pollution_day = df_pollution_day.drop(columns=['no2', 'o3','ox','pm1','pm10','pm25','co','latitude_max_day','longitude_max_day','hour_max_day','latitude_min_day','longitude_min_day','hour_min_day'])
df_pollution_hour = df_pollution_hour.drop(columns=['no2', 'o3','ox','pm1','pm10','pm25','co','latitude_mean_hour','longitude_mean_hour'])

#Remover duplicados
df_pollution_day = df_pollution_day.drop_duplicates(subset=['name', 'date'])
df_pollution_hour = df_pollution_hour.drop_duplicates(subset=['name', 'date', 'hour'])

# Passar coluna 'index' para 'ID'

df_pollution_day.reset_index(drop=True, inplace=True)
df_pollution_hour.reset_index(drop=True, inplace=True)

# Adicionar coluna "ID" a coemçar em 0
df_pollution_day['ID'] = np.arange(len(df_pollution_day))
df_pollution_hour['ID'] = np.arange(len(df_pollution_hour))

# Renomear index para "ID"
df_pollution_day.rename(columns={'index': 'ID'}, inplace=True)
df_pollution_hour.rename(columns={'index': 'ID'}, inplace=True)

# Troca de nome da coluna 'name' para 'Location_ID'
df_pollution_day['Location_ID'] = df_pollution_day['name']
df_pollution_hour['Location_ID'] = df_pollution_hour['name']
# Drop da coluna 'name'
df_pollution_day = df_pollution_day.drop(columns=['name'])
df_pollution_hour = df_pollution_hour.drop(columns=['name'])

# Guardar o dataframe num ficheiro .csv
# Definir localização do diretório de gravação
dir_path = r"C:\Users\Tiago\Documents\PG - Big Data & Decision Making\09. Seminars\Script Pollution"

# Drop da coluna 'hour' no df_pollution_day
df_pollution_day = df_pollution_day.drop(columns=['hour'])

# Definir ordem de colunas no df_pollution_day
order_day = ['ID', 'Location_ID', 'date', 'latitude', 'longitude', 
                 'no2_min_day', 'o3_min_day', 'ox_min_day', 'pm1_min_day', 
                 'pm10_min_day', 'pm25_min_day', 'co_min_day', 'no2_max_day', 
                 'o3_max_day', 'ox_max_day', 'pm1_max_day', 'pm10_max_day', 
                 'pm25_max_day', 'co_max_day']

# Mover coluna "ID" para esquerda
df_pollution_day = df_pollution_day[['ID'] + [col for col in order_day if col != 'ID']]

# Definir ordem de colunas no df_pollution_hour
order_hour = ['ID', 'Location_ID', 'date', 'hour', 'latitude', 'longitude', 
                      'no2_mean_hour', 'o3_mean_hour', 'ox_mean_hour', 
                      'pm1_mean_hour', 'pm10_mean_hour', 'pm25_mean_hour', 
                      'co_mean_hour']

# Mover coluna "ID" para esquerda
df_pollution_hour = df_pollution_hour[['ID'] + [col for col in order_hour if col != 'ID']]

# Guardar o ficheiro no diretório com o nome "pollution_data.csv" 
df_pollution_day.to_csv(os.path.join(dir_path, "pollution_data_max_min.csv"), index=False)
df_pollution_hour.to_csv(os.path.join(dir_path, "pollution_data_mean.csv"), index=False)