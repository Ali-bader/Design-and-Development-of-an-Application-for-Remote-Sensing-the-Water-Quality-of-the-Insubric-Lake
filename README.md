# Design-and-Development-of-an-Application-for-Remote-Sensing-the-Water-Quality-of-the-Insubric-Lake
The app uses remote sensing (Sentinel-3 OLCI, Landsat-8 TIRS) to produce Water Quality Parameter maps, achieving UN's SDG of clean water. 
## WQP maps processing
The docker composition presented in this repository aims to support the continued production of the Water Quality Parameters (WQPs) maps for the SIMILE project. The build of the image base in the `mundialis/esa-snap:8.0-ubuntu` latest image, and set up multiple python libraries to enable the creation of an interactive environment for processing satellite images.
## Requirements
First, install Xming Server. The Virtual Machine is composed inside a Docker container. Then, to build the processing environment, install Docker in your system. Follow the instructions presented in https://docs.docker.com/get-docker/ for your working OS.
## Setup Environment
1. Clone the project.
## Clone the repository
git clone https://github.com/Ali-bader/Design-and-Development-of-an-Application-for-Remote-Sensing-the-Water-Quality-of-the-Insubric-Lake/tree/main. Then unzip files (notebooks/folder-structure).
## Move to the location of the cloned project.
1. Open the "docker-compose.yml" file. then, change the DISPLAY environment variable to your IP address.
## Build the VM docker container.
### Build the Image
docker-compose build
### Run the container
docker-compose up -d
## Run the Application
After building and running the container, the user should navigate the "Xming.exe" file in Command Prompt. then, execute the Xming server by using “Xming -ac” command. the second step is to run the "GUI.ipynb". the software will appear on the Xming window. 
