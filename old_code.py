# The position of Stockholm
lon = 18.0687
lat = 59.3294

# Get the different dates in the dataset
dates = df_no_weather['date'].unique()

# Remove the nan values
dates = [date for date in dates if date == date]
dates = [date[0:10] for date in dates]

# Interchange the month and day
#dates = [date[0:4] + '-' + date[8:10] + '-' + date[5:7] for date in dates]

# remove duplicates
dates = list(set(dates))
print(dates)

# A dictionary that for each day contains the weather data
weather_data = {}
for date in dates:
    # Weather data for the current date
    hourly_weather = handle_weather_data(get_weather_data(lon, lat, date))
    
    # Add the weather data to the dictionary
    weather_data[date] = hourly_weather

# For each incident apply the weather data
for index, row in df_no_weather.iterrows():   
    # Get the weather data for the current date
    hourly_weather = weather_data[row['date'][0:10]]
    
    # Get the weather data for the current time
    weather_data_current_time = hourly_weather[hourly_weather['hour'] == row['time']]
    
    # Get the weather code
    weather_code = weather_data_current_time['weather_code'].values[0]
    
    # Update the dataframe
    df_no_weather.at[index, 'weather_code'] = weather_code
