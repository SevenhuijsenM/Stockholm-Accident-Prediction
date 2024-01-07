from dotenv import load_dotenv
import os
import requests
import json
import sys
import numpy as np

# A function that exports the TOMTOM api parameters
def tomtom_api_params():
    # Get the API key from the .env
    load_dotenv()
    API_KEY = os.getenv("API_KEY_TOMTOM")

    # Export the function parameters for the tomtom api
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

    return api_params_incidents

# A function that gets the weeather API parameters
def weather_api_params():
    # Get the api key from the .env
    load_dotenv()
    API_KEY = os.getenv("WEATHER_API_KEY")

    api_params = {
        'API_KEY': API_KEY,
        'city': 'Stockholm',
        'country': 'Sweden',
    }

    api_params['url'] = f"http://api.openweathermap.org/data/2.5/weather?q={api_params['city']}&appid={api_params['API_KEY']}"

    return api_params
    
# Function to make a request getting weather data
def get_weather_data(params):
    response = requests.get(params['url'])
    res = response.json()
    
    # Check if the city is found or not
    if res["cod"] != "404":
        data = res["main"]
    
        # Storing the live temperature data
        live_temperature = data["temp"]
        
        # Storing the live pressure data
        live_pressure = data["pressure"]
        desc = res["weather"]
        
        # Storing the weather description
        weather_description = desc[0]["description"]

        # Return the weather data
        return {'temperature': live_temperature, 'pressure': live_pressure, 'weather_description': weather_description }
    else:
        print("There was an error with the request")

        # Throw an error
        sys.exit(1)

# Function to make  a request getting the incident details
def get_incident_details(params, t):
    # If t is 0 then we get the recent events
    if t == 0:
        t = 'present'

    url = f"https://{params['base_url']}/traffic/services/{params['version_number']}/incidentDetails?bbox={params['min_lon']}%2C{params['min_lat']}%2C{params['max_lon']}%2C{params['max_lat']}&fields={params['fields']}&language={params['language']}&categoryFilter={params['category_filter']}&timeValidityFilter={params['time_validity_filter']}&key={params['API_KEY']}" + (f"&t={t}" if t != 0 else "")
    return json.loads(requests.get(url).text)


# Function that handles an incident
def handle_incident(incident, hourly_weather_datas):
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

    # Get the row of weather data that matches the hour
    weather_data = hourly_weather_datas.loc[int(hour_value)]

    # Put all the weather data in the dictionary
    for key, value in weather_data.items():
        if (key != 'date'):
            dict_incident[key] = value
        dict_incident[key] = value
        if (key == 'snow_depth' and np.isnan(value)):
            dict_incident[key] = 0
    
    return dict_incident

__all__ = ["tomtom_api_params", "get_incident_details", "handle_incident", "weather_api_params", "get_weather_data"]