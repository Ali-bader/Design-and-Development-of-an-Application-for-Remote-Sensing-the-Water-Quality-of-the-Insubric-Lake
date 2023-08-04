import tkinter as tk
from tkinter.messagebox import showinfo
import os
from dotenv import load_dotenv
from sodapy import Socrata
# Data Management
import numpy as np
import pandas as pd
import geopandas as gpd
import zipfile
import os
import requests
from DownloadMeto import download_meteo_data
import requests
from tkinter import messagebox
from tkinter import *
from tkinter import ttk
from DownloadS3 import download_satellite_imagery
from datetime import datetime
import threading
import queue
from DownloadMeto import save_temperature
from DownloadMeto import insert

# Create a queue for communication between threads
result_queue = queue.Queue()

cwd = {
    'S3_images': './in/satellite_imagery/S3',
    'EUMETSAT_images': './in/satellite_imagery/EUMETSAT',
    'simile_lakes': './vector/simile_laghi'
}


def toggle_password_visibility():
    password_entry.config(show="" if show_password.get() else "*")


def toggle_password_visibility_img():
    password1_entry.config(show="" if show_password1.get() else "*")


def authenticate_with_api(username_auth, password_auth):
    # Make a request to the API's authentication endpoint with the provided credentials
    auth_url = 'https://wekeo-broker.apps.mercator.dpi.wekeo.eu/databroker'
    response = requests.post(auth_url, json={"username": username_auth, "password": password_auth})
    return response

def on_download_meteo_data():
    username = username_entry.get()
    password = password_entry.get()
    token = token_entry.get()
    
    try:
        # Perform the necessary operations to download meteo data from the API
        download_meteo_data(username,password,token)
        result_label2.config(text="Meteo data downloaded successfully")
    except Exception as e:
        result_label2.config(text="Username, password, token is incorrect "  )
        #result_label2.config(text="Error" + str(e))
    

def insert_temp():
    temperature = temperature_entry.get()
    date_time = date_time_entry_temp.get()
    try:
        # Validate start date format
        date_time = datetime.strptime(date_time, "%d/%m/%Y %H:%M")
        save_temperature(temperature, date_time)
        result_label5.config(text="Temperature inserted successfully") 
    except Exception as e:
        result_label5.config(text="Invalid date and time format. Please use dd/mm/yyyy HH:MM.") 
        #result_label5.config(text="Error" + str(e))


def insert_parameters():
    t = t_entry.get()
    Ld = Ld_entry.get()
    Lu = Lu_entry.get()
    date_time = date_time_entry.get()
    try:
        # Validate start date format
        date_time = datetime.strptime(date_time, "%m/%d/%Y %H:%M")
        insert(t, Ld, Lu, date_time)
        result_label8.config(text="Parameters inserted successfully") 
    except Exception as e:
        result_label8.config(text="Invalid date and time format. Please use dd/mm/yyyy HH:MM.")
        #result_label8.config(text="Error: " + str(e))

   


        
def download_button_click():
    start_date_str = start_entry.get()
    end_date_str = end_entry.get()
    username_client = username1_entry.get()
    password_client = password1_entry.get()
    
    try:
        # Validate start date format
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        
        # Validate end date format
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        
        # Validate date range
        if end_date < start_date:
            result_label3.config(text="End date should be after start date")
        else:
            # Perform the necessary operations to download meteo data from the API
            download_satellite_imagery(start_date_str, end_date_str, username_client, password_client)
            result_label3.config(text="Image downloaded successfully")
    except ValueError:
        result_label3.config(text="Invalid date format. Please use YYYY-MM-DD")
    except Exception as e:
        result_label3.config(text="Username, password is incorrect")
        #result_label3.config(text="Error: " + str(e))

def handle_checkbox1():
    global selected_option
    selected_option = "downloaded"
    var2.set(0)  # Uncheck checkbox2

def handle_checkbox2():
    global selected_option
    selected_option = "inserted"   
    var1.set(0)  # Uncheck checkbox1
    
    
    
    
def long_function():
    # Get the selected sensor from the combobox
    selected_sensor = combobox.get()
    start_date = start_entry_pro.get()
    end_date = end_entry_pro.get()



    if selected_sensor == "S3":
        if selected_option == "downloaded":
            from production_s3 import wqp_s3
            # Call the wqp_s3() function
            result = wqp_s3(start_date, end_date)
            result_label4.config(text="CHL and TSM Maps Created successfully")
        elif selected_option == "inserted":
            from production_s3 import wqp_s3_ins
            # Call the wqp_s3_ins() function
            result = wqp_s3_ins(start_date, end_date)
            result_label4.config(text="CHL and TSM Maps Created successfully")
        else:
            result = None
    elif selected_sensor == "Landsat 8":
        from production_L8 import tem_L8
        # Call the tem_L8() function
        result = tem_L8()
        result_label4.config(text="LWST Map Created successfully")
    else:
        result = None

    # Put the result in the queue
    result_queue.put(result)





# Create the main window
window = tk.Tk()

# Create a StringVar to track the visibility state of the password
show_password = tk.BooleanVar()
show_password.set(False)

# Create a StringVar to track the visibility state of the password
show_password1 = tk.BooleanVar()
show_password1.set(False)

# Set the window title
window.title("Window with Run Button")
window.geometry("1700x1700")

# Create a Notebook widget
notebook = ttk.Notebook(window)
notebook.grid(row=0, column=0, padx=10, pady=10)

# Create tabs
tab1 = ttk.Frame(notebook)
tab2 = ttk.Frame(notebook)
tab3 = ttk.Frame(notebook)

# Add tabs to the notebook
notebook.add(tab1, text="Additional Dataset")
notebook.add(tab2, text="Download Sentinel-3 imagery")
notebook.add(tab3, text="Create Maps")

#tab one
tk.Label(tab1, text="Option 1: Download Temperature ").grid(row=0, column=0, padx=5, pady=5)
tk.Label(tab1, text="NOTE: use the same Username,Password and Token on -dati.lombardia.it-").grid(row=1, column=0, padx=5, pady=5)
# Create a Run button
run_button = tk.Button(tab1, text="Download MetoData", command=on_download_meteo_data)
run_button.grid(row=6, column=1, padx=5, pady=5)
# Add labels and entry boxes for username and password
tk.Label(tab1, text="Enter The UserName").grid(row=2, column=0, padx=5, pady=5)
username_entry = tk.Entry(tab1)
username_entry.grid(row=2, column=1, padx=5, pady=5)

tk.Label(tab1, text="Enter The Password").grid(row=3, column=0, padx=5, pady=5)
#password_entry = tk.Entry(tab1)
password_entry = tk.Entry(tab1, show="*", width=20)
password_entry.grid(row=3, column=1, padx=5, pady=5)

tk.Label(tab1, text="Enter The Token").grid(row=4, column=0, padx=5, pady=5)
token_entry = tk.Entry(tab1)
token_entry.grid(row=4, column=1, padx=5, pady=5)

result_label2 = tk.Label(tab1, text="")
result_label2.grid(row=5, column=0, padx=5, pady=5)

result_label5 = tk.Label(tab1, text="")
result_label5.grid(row=10, column=0, padx=5, pady=5)



visibility_checkbox = tk.Checkbutton(tab1, text="Show Password", variable=show_password, command=toggle_password_visibility)
visibility_checkbox.grid(row=3, column=2, padx=5, pady=5)

tk.Label(tab1, text="Option 2: Insert Temperature").grid(row=7, column=0, padx=5, pady=5)

tk.Label(tab1, text="Enter the temperature").grid(row=8, column=0, padx=5, pady=5)
temperature_entry = tk.Entry(tab1)
temperature_entry.grid(row=8, column=1, padx=5, pady=5)

tk.Label(tab1, text="Enter the Date and time (DD/MM/YYYY HH:MM): ").grid(row=9, column=0, padx=5, pady=5)
date_time_entry_temp = tk.Entry(tab1)
date_time_entry_temp.grid(row=9, column=1, padx=5, pady=5)

# Create a Run button
save_t_button = tk.Button(tab1, text="Enter", command=insert_temp)
save_t_button.grid(row=11, column=1, padx=5, pady=5)


tk.Label(tab1, text=" Atmospheric Correction Parameters").grid(row=12, column=0, padx=5, pady=5)
tk.Label(tab1, text=" The parameters are computed using the -https://atmcorr.gsfc.nasa.gov/atm_corr.html-").grid(row=13, column=0, padx=5, pady=5)
tk.Label(tab1, text="Lu").grid(row=14, column=0, padx=5, pady=5)
Lu_entry = tk.Entry(tab1)
Lu_entry.grid(row=14, column=1, padx=5, pady=5)

tk.Label(tab1, text="Ld").grid(row=15, column=0, padx=5, pady=5)
Ld_entry = tk.Entry(tab1)
Ld_entry.grid(row=15, column=1, padx=5, pady=5)

tk.Label(tab1, text="t").grid(row=16, column=0, padx=5, pady=5)
t_entry = tk.Entry(tab1)
t_entry.grid(row=16, column=1, padx=5, pady=5)

tk.Label(tab1, text="Enter the Date and time (MM/DD/YYYY HH:MM): ").grid(row=17, column=0, padx=5, pady=5)
date_time_entry = tk.Entry(tab1)
date_time_entry.grid(row=17, column=1, padx=5, pady=5)

# Create a Run button
save_t_button = tk.Button(tab1, text="Enter", command=insert_parameters)
save_t_button.grid(row=19, column=1, padx=5, pady=5)

result_label8 = tk.Label(tab1, text="")
result_label8.grid(row=18, column=0, padx=5, pady=5)



#tab two 
tk.Label(tab2, text="NOTE: use the same Username,Password  on -https://scihub.copernicus.eu/dhus/#/home-").grid(row=0, column=0, padx=5, pady=5)
# Create a Run button
run_button = tk.Button(tab2, text="Download S3", command=download_button_click)
run_button.grid(row=10, column=1, padx=5, pady=5)

# Add labels and entry boxes for username and password
tk.Label(tab2, text="Enter The UserName").grid(row=1, column=0, padx=5, pady=5)
username1_entry = tk.Entry(tab2)
username1_entry.grid(row=1, column=2, padx=5, pady=5)

tk.Label(tab2, text="Enter The Password").grid(row=2, column=0, padx=5, pady=5)
#password1_entry = tk.Entry(tab2)
password1_entry = tk.Entry(tab2, show="*", width=20)
password1_entry.grid(row=2, column=2, padx=5, pady=5)

# Create labels

start_label = tk.Label(tab2, text="Start Date (YYYY-MM-DD):").grid(row=3, column=0, padx=5, pady=5)
start_entry=tk.Entry(tab2)
start_entry.grid(row=3, column=2, padx=5, pady=5)



end_label = tk.Label(tab2, text="End Date (YYYY-MM-DD):").grid(row=4, column=0, padx=5, pady=5)
end_entry=tk.Entry(tab2)
end_entry.grid(row=4, column=2, padx=5, pady=5)


result_label3 = tk.Label(tab2, text="")
result_label3.grid(row=5, column=0, padx=5, pady=5)

visibility_checkbox = tk.Checkbutton(tab2, text="Show Password", variable=show_password1, command=toggle_password_visibility_img)
visibility_checkbox.grid(row=2, column=3, padx=5, pady=5)


#Tab Three
run_button = tk.Button(tab3, text="Run", command=long_function)
run_button.grid(row=10, column=1, padx=5, pady=5)
# Create a combobox for selecting the sensor
start_label = tk.Label(tab3, text="Select Sensor:").grid(row=7, column=0, padx=5, pady=5)
combobox = ttk.Combobox(tab3, values=["S3", "Landsat 8"])
combobox.grid(row=7, column=2, padx=5, pady=5)

result_label4 = tk.Label(tab3, text="")
result_label4.grid(row=9, column=0, padx=5, pady=5)

# Create the checkboxes variables
var1 = tk.IntVar()
var2 = tk.IntVar()

# Create the checkboxes
checkbox1 = tk.Checkbutton(tab3, text="Downloaded Temperature", variable=var1, command=handle_checkbox1)
checkbox2 = tk.Checkbutton(tab3, text="Inserted Temperature", variable=var2, command=handle_checkbox2)

# Place the checkboxes in the window
checkbox1.grid(row=8, column=1, padx=5, pady=5)
checkbox2.grid(row=9, column=1, padx=5, pady=5)

start_label = tk.Label(tab3, text="Start Date (YYYY-MM-DD):").grid(row=3, column=0, padx=5, pady=5)
start_entry_pro=tk.Entry(tab3)
start_entry_pro.grid(row=3, column=2, padx=5, pady=5)



end_label = tk.Label(tab3, text="End Date (YYYY-MM-DD):").grid(row=5, column=0, padx=5, pady=5)
end_entry_pro=tk.Entry(tab3)
end_entry_pro.grid(row=5, column=2, padx=5, pady=5)


# Create a separate thread for executing the long function
thread = threading.Thread(target=long_function)
thread.start()

# Check if the result is available in the queue
if not result_queue.empty():
    result = result_queue.get()

# Run the main window
window.mainloop()
