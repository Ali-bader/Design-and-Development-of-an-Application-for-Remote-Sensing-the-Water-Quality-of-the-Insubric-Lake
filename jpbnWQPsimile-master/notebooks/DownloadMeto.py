import os
from dotenv import load_dotenv
from sodapy import Socrata
# Data Management
import numpy as np
import pandas as pd
import geopandas as gpd
import zipfile
import requests
from tkinter.messagebox import showinfo
import csv
from datetime import datetime



def download_meteo_data(username1, password1, token1):
    



    load_dotenv()
    cwd = {
    'wqp_path': './in/satellite_imagery/wqp_parameters',
    'simile_lakes': './vector/simile_laghi'
     }   

    url = os.environ['SOCRATA_DATA_PROVIDER']
    #user = os.environ['SOCRATA_USER']
    #user =username_entry.get()
    user =username1
    #password = os.environ['SOCRATA_PASSWORD']
    #password = password_entry.get()
    password=password1
    #token = os.environ['SOCRATA_APP_TOKEN']
    #token = token_entry.get()
    token=token1
    
    client = Socrata(
        url,
        app_token = token,
        username = user,
        password = password,
        timeout=100000
      )

    meteoStations = client.get('nf78-nj6b')
    meteoData = client.get('647i-nhxk',IdSensore='14606', limit = 100000)
    # Pass data to dataframe
    df_SL = gpd.GeoDataFrame(meteoStations)
    gdf_SL = gpd.GeoDataFrame(df_SL, geometry=gpd.points_from_xy(df_SL.lat, df_SL.lng))
    df_TS = pd.DataFrame(meteoData)
    # Lakes shapes
    df_lakes = gpd.read_file(os.path.join(cwd['simile_lakes'],'simile_laghi.shp'))

    #The coulmns must be renamed to fit the existing data
    keysData = {
    'idsensore':'IdSensore',
    'data':'Data',
    'valore':'Valore',
    'idoperatore':'idOperatore',
    'stato':'Stato',
     }
    df_TS.rename(columns = keysData, inplace = True)

    df_TS["IdSensore"] = df_TS['IdSensore'].astype('int')
    df_TS["Data"] = pd.to_datetime(df_TS['Data'])
    df_TS["Valore"] = df_TS['Valore'].astype('float')
    df_TS["idOperatore"] = df_TS['idOperatore'].astype('int')
    df_TS["Stato"] = df_TS['Stato'].astype('str')

    df = pd.read_csv(os.path.join(cwd['wqp_path'],'meteoTemp.csv'))
    df["IdSensore"] = df['IdSensore'].astype('int')
    df["Data"] = pd.to_datetime(df['Data'], format="%d/%m/%Y %H:%M:%S", errors='coerce')
    #df["Data"] = pd.to_datetime(df['Data'])
    df["Valore"] = df['Valore'].astype('float')
    df["idOperatore"] = df['idOperatore'].astype('int')
    df["Stato"] = df['Stato'].astype('str')
    max(df.Data)

    # Load available records
    df = pd.read_csv(os.path.join(cwd['wqp_path'],'meteoTemp.csv'))

    df["IdSensore"] = df['IdSensore'].astype('int')
    df["Data"] = pd.to_datetime(df['Data'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
    #df["Data"] = pd.to_datetime(df['Data'])
    df["Valore"] = df['Valore'].astype('float')
    df["idOperatore"] = df['idOperatore'].astype('int')
    df["Stato"] = df['Stato'].astype('str')

    # Update the dataframe with the recently retrieved dates for the current month
    df = pd.concat([df,df_TS])
    df = df.drop_duplicates() #Since a query over the date is not performed, we must make sure that there are no ducplicate records
    df["Data"] = pd.to_datetime(df['Data'])
    df.to_csv(os.path.join(cwd['wqp_path'],'meteoTemp.csv'),index=False)
    url_2023 = "/download/48xr-g9b9/application%2Fzip"
    
    
    
    response = requests.get('https://' + os.environ['SOCRATA_DATA_PROVIDER'] + url_2023)
    zip_name = './meteo/2023.zip'
    open(zip_name, "wb").write(response.content)
    with zipfile.ZipFile(zip_name, 'r') as zip_ref:
        zip_ref.extractall('./meteo')
    os.remove(zip_name)





    
    # Create list of dataframes with the historical records for the station of interest.
    # This step may take some time since each .csv file contains over 3e6 records for the whole meteorological network of sensors of ARPA Lombardia. 
    l = []
    for root, dirs, files in os.walk('./meteo'):
        for f in files:
            if f.endswith('.csv'):
                print(f)
                df = pd.read_csv(os.path.join(root,f))
                df = df[df['IdSensore']==14606]
                l.append(df) 
    df = pd.concat(l)
    df.to_csv(os.path.join(cwd['wqp_path'],'meteoTemp.csv'),index=False)
    # df = pd.concat(l)
    df.to_csv(os.path.join(cwd['wqp_path'],'meteoTemp.csv'),index=False,encoding='utf-8')
    # Uncomment the following line if the historical meteo data has been aggregated previously
    df = pd.read_csv(os.path.join(cwd['wqp_path'],'meteoTemp.csv'))
    df["IdSensore"] = df['IdSensore'].astype('int')
    df["Data"] = pd.to_datetime(df['Data'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
    df["Valore"] = df['Valore'].astype('float')
    df["Stato"] = df['Stato'].astype('str')
    df["idOperatore"] = df['idOperatore'].astype('int')
    df = df.set_index('Data')


    




def save_temperature(temperature, datetime_obj):
    load_dotenv()
    cwd = {
        'wqp_path': './in/satellite_imagery/wqp_parameters',
        'simile_lakes': './vector/simile_laghi'
    }

    # Specify the file path for the CSV
    file_path = os.path.join(cwd['wqp_path'], 'meteoTemp_ins.csv')

    # Check if the file exists
    file_exists = os.path.isfile(file_path)

    # Create the CSV file and write the header if it doesn't exist
    if not file_exists:
        with open(file_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["IdSensore", "Data", "Valore", "Stato", "idOperatore"])

    # Read the existing data from the CSV file
    existing_data = []
    with open(file_path, "r", newline="") as csvfile:
        reader = csv.reader(csvfile)
        existing_data.extend(list(reader))

    # Check if the datetime already exists
    datetime_str = datetime_obj.strftime("%d/%m/%Y %H:%M:%S")
    for row in existing_data:
        if row[1] == datetime_str:
            # Replace the existing row with the new temperature data
            row[2] = float(temperature)
            break
    else:
        # Append the new temperature data as a new row
        new_row = ["14606", datetime_obj.strftime("%d/%m/%Y %H:%M:%S"), float(temperature), "VA", "1"]
        existing_data.append(new_row)

    # Write the updated data back to the CSV file
    with open(file_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(existing_data)
        
        
        
        
def insert(t, Ld, Lu, datetime_obj):
    load_dotenv()
    cwd = {
        'wqp_path': './in/satellite_imagery/wqp_parameters',
        'simile_lakes': './vector/simile_laghi'
    }

    # Specify the file path for the CSV
    file_path = os.path.join(cwd['wqp_path'], 'atmCorr.csv')

    # Read the existing data from the CSV file
    existing_data = []
    existing_datetime = None  # Variable to store the existing datetime, if found

    with open(file_path, "r", newline="") as csvfile:
        reader = csv.reader(csvfile)
        existing_data.extend(list(reader))

    # Check if the datetime already exists
    datetime_str = datetime_obj.strftime("%m/%d/%Y %H:%M:%S")
    for row in existing_data:
        if row[0] == datetime_str:
            existing_datetime = row
            break

    # If the datetime already exists, replace the existing row with the new parameters
    if existing_datetime:
        existing_datetime[6] = float(t)
        existing_datetime[7] = float(Lu)
        existing_datetime[8] = float(Ld)
    else:
        # If the datetime doesn't exist, append a new row with the provided parameters
        new_row = [
            datetime_obj.strftime("%m/%d/%Y %H:%M:%S"),
            datetime_obj.year,
            datetime_obj.month,
            datetime_obj.day,
            datetime_obj.hour,
            datetime_obj.minute,
            float(t),
            float(Lu),
            float(Ld)
        ]
        existing_data.append(new_row)

    # Write the updated data back to the CSV file
    with open(file_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(existing_data)
