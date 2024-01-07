# This file is used to get training data. A list of activate IDs is listed, and each 5 minutes the API fetches data
# From the tom tom API and gets all necessary information. A running list is updated that contains all the 
# active ids, if an id is not active anymore (not in the fetched data) then it is removed from the list and added to a csv file
# This way we have an approximate end date

# Import necessary libraries
import os
import requests
import json
import pandas as pd
import time
from helper import tomtom_api_params, get_weather_data, weather_api_params


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
def handle_incident(incident, weather_data):
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
        'temperature': weather_data['temperature'],
        'pressure': weather_data['pressure'],
        'weather_description': weather_data['weather_description']
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
    if os.path.isfile('incidents.csv-v2'):
        df_incidents = pd.read_csv('incidents-v2.csv')
    else:
        df_incidents = pd.DataFrame(columns=['id', 'code', 'description', 'endTime', 'hour', 'iconCategory', 'latitude', 'longitude', 'magnitudeOfDelay', 'month', 'startTime', 'type', 'temperature', 'pressure', 'weather_description'])
        df_incidents.set_index('id', inplace=True)
        
    return df_incidents

# The main for loop that runs every sleeps for 5 minutes between iteration
if __name__ == '__main__':
    api_params_incidents = tomtom_api_params()     # Get the api parameters
    api_params_weather = weather_api_params()      # Get the weather api parameters
    frequency_api_call_minutes = 2              # Define how often the API is called   
    data_collection_period_minutes = 60         # Data collection period in minutes
    iterations = int(data_collection_period_minutes / frequency_api_call_minutes)
    
    # Get the current incidents.csv file
    df_incidents = load_or_create_incidents_csv()
    
    # Get a list of all the active ids
    df_incident_indices = df_incidents.index.tolist()        

    # A dictionary of active IDs
    active_ids = {}
    
    # iteration count
    i = 0
    
    while(i < iterations):
        # Make a request to get the incident details
        print(f"Getting incident details at time {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.localtime())}")
        incidents = get_incident_details(api_params_incidents)['incidents']

        # Get the weather data
        weather_data = get_weather_data(api_params_weather)
        
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
            active_ids[incident['properties']['id']] = handle_incident(incident, weather_data)
            print(f"ID {incident['properties']['id']} is now active")
        
        # Sleep until the next iteration
        i += 1
        time.sleep(frequency_api_call_minutes * 60)