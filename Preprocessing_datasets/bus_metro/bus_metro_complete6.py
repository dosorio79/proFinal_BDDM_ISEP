# -*- coding: utf-8 -*-
"""
Created on Sat Jun  1 09:14:10 2024

@author: diogo
"""


#1.1 code to import bus datasets

import pandas as pd
df_bus_stop_time=pd.read_csv(r'C:\Users\diogo\Desktop\ISEP\SEM\gtfs-stcp-2023-09\stop_times.txt')
df_bus_stops=pd.read_csv(r'C:\Users\diogo\Desktop\ISEP\SEM\gtfs-stcp-2023-09\stops.txt')
df_metro_stop_time=pd.read_csv(r'C:\Users\diogo\Desktop\ISEP\SEM\gtfs_mdp_11_09_2023\stop_times.txt')
df_metro_stops=pd.read_csv(r'C:\Users\diogo\Desktop\ISEP\SEM\gtfs_mdp_11_09_2023\stops.txt')
df_metro_calendar=pd.read_csv(r'C:\Users\diogo\Desktop\ISEP\SEM\gtfs_mdp_11_09_2023\calendar.txt')
#1.2 code to process bus dataset


df_bus_stops.pop('stop_code')
#df_bus_stops.pop('stop_name')
df_bus_stops.pop('zone_id')
df_bus_stops.pop('stop_url')
df_bus_stop_time[['line', 'flag1','weekclassifier','flag2']] = df_bus_stop_time['trip_id'].str.split("_", expand = True)
df_bus_stop_time.pop('trip_id')
df_bus_stop_time.pop('arrival_time')
df_bus_stop_time.pop('stop_sequence')
df_bus_stop_time.pop('stop_headsign')
df_bus_stop_time.pop('flag1')
df_bus_stop_time.pop('flag2')

df_bus_stop_time['weekclassifier']=df_bus_stop_time['weekclassifier'].replace('I','U')
df_bus_stop_time['weekclassifier']=df_bus_stop_time['weekclassifier'].replace('K','D')
df_bus_stop_time['weekclassifier']=df_bus_stop_time['weekclassifier'].replace('J','S')

df_metro_stops.pop('stop_code')
#df_metro_stops.pop('stop_name')
df_metro_stops.pop('stop_desc')
df_metro_stops.pop('zone_id')
df_metro_stops.pop('stop_url')
df_metro_stop_time.pop('stop_sequence')
df_metro_stop_time.pop('stop_headsign')
df_metro_stop_time.pop('pickup_type')
df_metro_stop_time.pop('drop_off_type')
df_metro_stop_time.pop('shape_dist_traveled')

df_metro_stop_time['trip_id'].replace('\d+', '', regex=True, inplace=True)
df_metro_stop_time=df_metro_stop_time.merge(df_metro_calendar, left_on='trip_id',right_on='service_id')
df_metro_stop_time.pop('service_id')
df_metro_stop_time.pop('trip_id')
df_stops = pd.concat([df_bus_stops, df_metro_stops], ignore_index=True)
df_metro_stop_time.pop('tuesday')
df_metro_stop_time.pop('wednesday')
df_metro_stop_time.pop('thursday')
df_metro_stop_time.pop('friday')
df_metro_stop_time.pop('start_date')
df_metro_stop_time.pop('end_date')

df_metro_stop_time['monday']=df_metro_stop_time['monday'].replace(0,'')
df_metro_stop_time['monday']=df_metro_stop_time['monday'].replace(1,'U')
df_metro_stop_time['saturday']=df_metro_stop_time['saturday'].replace(0,'')
df_metro_stop_time['saturday']=df_metro_stop_time['saturday'].replace(1,'S')
df_metro_stop_time['sunday']=df_metro_stop_time['sunday'].replace(0,'')
df_metro_stop_time['sunday']=df_metro_stop_time['sunday'].replace(1,'D')
df_metro_stop_time['weekclassifier'] =df_metro_stop_time['monday']+df_metro_stop_time['saturday']+df_metro_stop_time['sunday']
df_metro_stop_time.pop('monday')
df_metro_stop_time.pop('saturday')
df_metro_stop_time.pop('sunday')
df_metro_stop_time.pop('arrival_time')
df_bus_stop_time.pop('line')
df_bus_stop_time['bus_metro_flag']='bus'
df_metro_stop_time['bus_metro_flag']='metro'

df_bus_stop_time['dep_time_int']=0
df_bus_stop_time['day_night']=''

df_metro_stop_time['dep_time_int']=0
df_metro_stop_time['day_night']=''


# get nominatim

from geopy.geocoders import Nominatim
pd.options.mode.chained_assignment = None 



#Get dataframe from CSV


#start aux variables

df_bus_stops['postcode']=''
df_metro_stops['postcode']=''

from geopy.exc import GeocoderTimedOut
#get required fields from nominatin
def city_state_country(row, attempt=1, max_attempts=5):
    
    try:
        geolocator = Nominatim(user_agent="portosustentavel"+str(row["stop_id"]))
        coord = f"{row['stop_lat']}, {row['stop_lon']}"
        location = geolocator.reverse(coord, exactly_one=True,timeout=50)
        address = location.raw['address']
        postcode = address.get('postcode', '')
        row['postcode'] = postcode
    except GeocoderTimedOut:
        if attempt <= max_attempts:
            return city_state_country(address, attempt=attempt+1)
        raise
        
    return row

#apply to dataframe
# df_metro_stops=df_metro_stops.head(200)
# df_bus_stops=df_bus_stops.head(200)
df_metro_stops = df_metro_stops.apply(city_state_country, axis=1)
df_bus_stops = df_bus_stops.apply(city_state_country, axis=1)

df_bus_stop_time=df_bus_stop_time.merge(df_bus_stops, on='stop_id')
df_bus_stop_time.pop('stop_id')
df_metro_stop_time=df_metro_stop_time.merge(df_metro_stops, on='stop_id')
df_metro_stop_time.pop('stop_id')

df_stop_time = pd.concat([df_bus_stop_time, df_metro_stop_time], ignore_index=True)


for i in range (0,len(df_stop_time)):
    df_stop_time['dep_time_int'][i]=int(df_stop_time['departure_time'][i].replace(':',''))
    if df_stop_time['dep_time_int'][i]>=60000 and df_stop_time['dep_time_int'][i]<=220000:
        df_stop_time['day_night'][i]='day'
    else:
        df_stop_time['day_night'][i]='night'


df_stop_time.pop('dep_time_int')
df_stop_time.pop('departure_time')


df_stop_time['count']=1
df_stop_time=df_stop_time.groupby(["weekclassifier","day_night","bus_metro_flag","stop_lat","stop_lon","postcode","stop_name"])['count'].sum()
df_stop_time = df_stop_time.reset_index()


#--------------------------------------------------------------------------------------------------------------------------------

df_match_postcode=pd.read_csv('https://raw.githubusercontent.com/dssg-pt/mp-mapeamento-cp7/main/output_data/cod_post_freg_matched.csv',encoding='utf-8')



df_match_postcode['postcode']=df_match_postcode['CodigoPostal'].astype(int)
# Apply the function to each row in df1
df_stop_time['postcode'] = df_stop_time['postcode'].str.replace('-', '').astype(int)
df_stop_time=df_stop_time.merge(df_match_postcode, on='postcode',how='left')


df_stop_time.pop('Distrito')
df_stop_time.pop('Freguesia')
df_stop_time.pop('Distrito_map')
df_stop_time.pop('Concelho_map')
df_stop_time.pop('Freguesia_map')
df_stop_time.pop('Alteração RATF')
df_stop_time.pop('CodigoPostal')
df_stop_time = df_stop_time.rename(columns={'Freguesia Final (Pós RATF)': 'freguesia'})
df_stop_time = df_stop_time.rename(columns={'Concelho': 'concelho'})




#--------------------------------------------------------------------------------------------------------------------------------




df_stop_time.to_csv(r'C:\Users\diogo\Desktop\busmetrocomplete.csv', encoding='latin-1')