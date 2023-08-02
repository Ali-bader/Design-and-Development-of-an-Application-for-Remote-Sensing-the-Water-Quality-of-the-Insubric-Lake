import base64
import os
import zipfile
import shutil
from dotenv import load_dotenv
load_dotenv()

import pandas as pd
import geopandas as gpd
from datetime import datetime

# Plotting
import matplotlib.pyplot as plt
from matplotlib_scalebar.scalebar import ScaleBar

# API requests config
import requests

# Widgets and maps view
# from __future__ import print_function
from ipywidgets import interact, interactive, fixed, interact_manual
import ipywidgets as wg
from hda import Client
# from IPython.display import display


cwd = {
    'S3_images': './in/satellite_imagery/S3',
    'EUMETSAT_images': './in/satellite_imagery/EUMETSAT',
    'simile_lakes': './vector/simile_laghi'
}   

def extractZipFile(image_dir, file_path):
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(image_dir)
        os.remove(file_path)


def download_satellite_imagery(start_date, end_date,user_client,password_client):
    # Load environment variables from .env file
    load_dotenv()

    # Get credentials from environment variables
    url = os.environ['HDA_URL']
    user = user_client
    password = password_client

    # Create credentials string
    credentials = user + ":" + password
    credentials_bytes = credentials.encode('ascii')
    base64_bytes = base64.b64encode(credentials_bytes)
    base64_credentials = base64_bytes.decode('ascii')

    # Set authorization header
    header = {'authorization': 'Basic ' + base64_credentials}

    # Get access token
    response = requests.get(url + '/gettoken', headers=header)
    response = response.json()
    access_token = response['access_token']

    # Accept terms and conditions
    header = {
        'accept': 'application/json',
        'authorization': access_token
    }
    requests.put(url + '/termsaccepted/Copernicus_General_License', headers=header)

    # Set parameters for the client
    parameters = f'url: {url}\nuser: {user}\npassword: {password}\ntoken: {access_token}'

    # Create .hdarc config file in the home directory
    with open(os.path.join(os.environ['HOME'], '.hdarc'), 'w') as fp:
        fp.write(parameters)

    # Create hda Client
    c = Client()
    
    gdf = gpd.read_file(os.path.join(cwd['simile_lakes'],'simile_laghi.shp'))
    
    # It is necessary to have the query coordinates in web mercator
    gdf = gdf.to_crs("EPSG:4326")
    # Extract the information from the bounding box of the layer
    x_min = min(gdf.bounds['minx'])
    x_max = min(gdf.bounds['maxx'])
    y_min = min(gdf.bounds['miny'])
    y_max = min(gdf.bounds['maxy'])  

    # Define your search query
    query = {
        "datasetId": "EO:EUM:DAT:SENTINEL-3:OL_1_EFR___",
        "boundingBoxValues": [
            {
                "name": "bbox",
                "bbox": [
                    x_min,
                    y_min,
                    x_max,
                    y_max
                ]
            }
        ],
        "dateRangeSelectValues": [
            {
                "name": "position",
                "start": datetime.strptime(start_date, '%Y-%m-%d').strftime('%Y-%m-%dT%H:%M:%S.000Z'),
                "end": datetime.strptime(end_date, '%Y-%m-%d').strftime('%Y-%m-%dT%H:%M:%S.000Z')
            }
        ],
        "stringChoiceValues": [
            {
                "name": "platformname",
                "value": "Sentinel-3"
            },
            {
                "name": "producttype",
                "value": "OL_1_EFR___"
            },
            {
                "name": "timeliness",
                "value": "NT"
            }
        ]
    }

    # Run the query and download the products
    matches = c.search(query)
    matches.download()
    
    for product in matches.__dict__['results']:
        shutil.move(product['filename'], cwd['S3_images'])

    
    for root, dirs, files in os.walk(cwd['S3_images']):
        for zip_name in files:
            file_path = os.path.join(root,zip_name)
            print(f'Currently extracting: {zip_name}')
        # Exception required for products retrieved through the HDA API. The products download include the .SEN3 extension and not a compressed file format
            if zip_name.endswith('.SEN3'):
                os.rename(os.path.join(cwd['S3_images'],zip_name),os.path.join(cwd['S3_images'],zip_name.split('.')[0]+'.zip'))
                file_path = os.path.join(cwd['S3_images'],zip_name.split('.')[0]+'.zip')
                extractZipFile(cwd['S3_images'], file_path)
            elif zip_name.endswith('.zip'):
                extractZipFile(cwd['S3_images'], file_path)
    

    


    # Return a result or status message
    return "Satellite imagery downloaded successfully"