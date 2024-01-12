from dotenv import load_dotenv
import os 
from helper import get_incident_details

load_dotenv()
API_KEY = os.getenv("API_KEY_TOMTOM")

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

print(get_incident_details(api_params_incidents, 1705069120))

