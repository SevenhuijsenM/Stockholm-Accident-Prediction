# This file is used to get training data. A list of activate IDs is listed, and each 5 minutes the API fetches data
# From the tom tom API and gets all necessary information. A running list is updated that contains all the 
# active ids, if an id is not active anymore (not in the fetched data) then it is removed from the list and added to a csv file
# This way we have an approximate end date

# Import necessary libraries
import os
import requests
import json
import pandas as pd
import numpy as np
from dotenv import load_dotenv
import time

# Get the environmental variables
load_dotenv()
API_KEY = os.getenv("API-KEY-TOMTOM")

# Dictionary of all parameters for the API
api_params_incidents = {
    'base_url': 'api.tomtom.com',
    'API_KEY': API_KEY,
    'min_lon': 18.00,
    'max_lon': 18.16,
    'min_lat': 59.25,
    'max_lat': 59.40,
    'version_number': 5,
    'time_validity_filter': 'present',
    'category_filter': '0%2C1%2C2%2C3%2C4%2C5%2C6%2C7%2C8%2C9%2C10%2C11%2C14',
    'language': 'en-GB',
    'fields': '%7Bincidents%7Btype%2Cgeometry%7Bcoordinates%7D%2Cproperties%7Bid%2CmagnitudeOfDelay%2Cevents%7Bdescription%2Ccode%2CiconCategory%7D%2CstartTime%2CendTime%7D%7D%7D'
}

# Function to make  a request getting the incident details
def get_incident_details(params):
    url = f"https://{params['base_url']}/traffic/services/{params['version_number']}/incidentDetails?bbox={params['min_lon']}%2C{params['min_lat']}%2C{params['max_lon']}%2C{params['max_lat']}&fields={params['fields']}&language={params['language']}&categoryFilter={params['category_filter']}&timeValidityFilter={params['time_validity_filter']}&key={params['API_KEY']}"
    return json.loads(requests.get(url).text)
    
# Function that updates the incidents csv with a single row
def add_row_to_incidents_csv(row, df_incidents):
    # Create an df from the row
    df_row = pd.DataFrame(row, index=[row['id']])
    
    # merge the df_row with the df_incidents
    df_incidents = pd.concat([df_incidents, df_row])
    
    df_incidents.to_csv('incidents.csv')
    return df_incidents

    
# Function that handles an incident
def handle_incident(incident):
    hour_value = incident['properties']['startTime'][11:13]

    # Create a dictionary with the incident details
    dict_incident = {
        'id': incident['properties']['id'],
        'magnitudeOfDelay': incident['properties']['magnitudeOfDelay'],
        'startTime': incident['properties']['startTime'],
        'endTime': incident['properties']['endTime'],
        'type': incident['type'],
        'code': incident['properties']['events'][0]['code'],
        'iconCategory': incident['properties']['events'][0]['iconCategory'],
        'description': incident['properties']['events'][0]['description'],
        'month': incident['properties']['startTime'][5:7],
        'hour': hour_value,
    }

    # Get the coordinates of the incident, if statement is for if the incident only has one coordinate
    if any(isinstance(j, list) for j in incident['geometry']['coordinates']):
        dict_incident['longitude'] = incident['geometry']['coordinates'][0][0]
        dict_incident['latitude'] = incident['geometry']['coordinates'][0][1]
    else:
        dict_incident['longitude'] = incident['geometry']['coordinates'][0]
        dict_incident['latitude'] = incident['geometry']['coordinates'][1]

    return dict_incident

# Function that loads or creates the incidents csv
def load_or_create_incidents_csv():
    # Load the incidents csv if it exists
    if os.path.isfile('incidents.csv'):
        df_incidents = pd.read_csv('incidents.csv')
    else:
        df_incidents = pd.DataFrame(columns=['id', 'type', 'magnitudeOfDelay', 'startTime', 'endTime', 'description', 'code', 'iconCategory', 'longitude', 'latitude', 'temperature_2m', 'relative_humidity_2m', 'dew_point_2m', 'apparent_temperature', 'precipitation', 'rain', 'snowfall', 'snow_depth', 'weather_code', 'surface_pressure', 'et0_fao_evapotranspiration', 'vapour_pressure_deficit', 'wind_speed_10m', 'soil_temperature_0_to_7cm', 'is_day', 'sunshine_duration'])
        df_incidents.set_index('id', inplace=True)
        
    return df_incidents

# The main for loop that runs every sleeps for 5 minutes between iteration
if __name__ == '__main__':
    
    # Get the current incidents.csv file
    df_incidents = load_or_create_incidents_csv()
    
    # Get a list of all the active ids
    df_incident_indices = df_incidents.index.tolist()        

    # A dictionary of active IDs
    active_ids = {}
    
    # iteration count
    i = 0
    
    while(1):
        # Make a request to get the incident details
        print(f"Getting incident details at time {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.localtime())}")
        incidents = get_incident_details(api_params_incidents)['incidents']
        
        # Filter out the ids that have already been added to df incidents
        incidents = [incident for incident in incidents if incident['properties']['id'] not in df_incident_indices]
        
        # Create a new active ids dictionary that will be updated
        new_active_ids = active_ids.copy()
        
        # Check what ids are still active
        # If there is an id in active_ids that is not in the incidents then it is no longer active
        for id in active_ids:
            if id not in [incident['properties']['id'] for incident in incidents]:
                print(f"ID {id} is no longer active")
                # add a endTime to the incident
                active_ids[id]['endTime'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.localtime())
                
                # Add the incident to the csv
                df_incidents = add_row_to_incidents_csv(active_ids[id], df_incidents)
                df_incident_indices = df_incidents.index.tolist()
                
                # Remove the incident from the new_active_ids
                del new_active_ids[id]
                
                # Remove the incident from the incidents
                incidents = [incident for incident in incidents if incident['properties']['id'] != id]
                
                # Add the incident to df_incident_indices
                df_incident_indices.append(id)
                
        # Update the active_ids
        active_ids = new_active_ids.copy()
        
        # remove all the incidents that are already active
        incidents = [incident for incident in incidents if incident['properties']['id'] not in active_ids]
                        
        # If there are any incidents left then they are new incidents
        for incident in incidents:
            # Add the incident to the active_ids
            active_ids[incident['properties']['id']] = handle_incident(incident)
            print(f"ID {incident['properties']['id']} is now active")
                
        
        # Sleep for 5 minutes
        i += 1
        time.sleep(120)