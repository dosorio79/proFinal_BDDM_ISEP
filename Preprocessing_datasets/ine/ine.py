# -*- coding: utf-8 -*-
"""
Created on Fri May 17 22:45:04 2024

@author: diogo
"""
import csv  
import requests
from datetime import date
import pandas as pd
current_year=date.today().year
response_API = requests.get('https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0011688&Dim1=T&lang=PT')
print(response_API.status_code)
jsonstring=response_API.json()
jsonstring2=jsonstring[0]
jsonstring2=jsonstring2['Dados']
while str(current_year) not in jsonstring2.keys():
    current_year -=1

jsonstring2=jsonstring2[str(current_year)]
#HM é o somatorio de homens e mulheres

df=pd.DataFrame(jsonstring2)
df=df.loc[df['dim_3_t'] != 'HM']
df=df.loc[df['dim_4'] != 'T']
df = df.drop(["dim_3","ind_string"], axis='columns')



df['district_code'] = df['geocod'].str[:2]




# Split the DataFrame into two based on the length of 'geocod'
df_4_digits = df[df['geocod'].str.len() == 4]
df_6_digits = df[df['geocod'].str.len() == 6]

df_6_digits.loc[df_6_digits.index, 'concelho_code'] = df_6_digits['geocod'].str[:4]

df_4_digits.pop('dim_3_t')
df_4_digits.pop('dim_4')
df_4_digits.pop('dim_4_t')
df_4_digits.pop('valor')
df_4_digits.pop('district_code')

df_4_digits = df_4_digits.drop_duplicates(subset=['geocod', 'geodsg'])

df_final=df_6_digits.merge(df_4_digits, left_on='concelho_code',right_on='geocod')
df_final.pop('geocod_y')
df_final = df_final.rename(columns={'geocod_x': 'freguesia_code'})
df_final = df_final.rename(columns={'geodsg_x': 'freguesia'})
df_final = df_final.rename(columns={'dim_3_t': 'genero'})
df_final.pop('dim_4')
df_final = df_final.rename(columns={'dim_4_t': 'faixa_etaria'})
df_final = df_final.rename(columns={'geodsg_y': 'concelho'})
df_final = df_final.rename(columns={'valor': 'count'})
df_final = df_final[df_final['district_code'] == '13']
df_final.pop('freguesia_code')
df_final.pop('district_code')
df_final.pop('concelho_code')
df_final['ano']=current_year
df_final.to_csv(r'C:\Users\diogo\Desktop\ine.csv',encoding='utf-16', index=False)