# Stockholm incident prediction

# We have different pipelines for different purposes. Therefore this file is seperated into multiple parts explaining each partition of the project.

# ## 0. Prerequisites and purpose
This project is a part of the course ID2223 HT23 Scalable Machine Learning and Deep Learning at KTH Royal Institute of Technology. The purpose of this project is to predict the duration of incidents in Stockholm using AI. The project is divided into three parts: data collection, data preprocessing and model training. The project is written in Python and the code is available at https://github.com/SevenhuijsenM/Stockholm-Accident-Prediction. Also there is a huggingface GUI available at https://huggingface.co/spaces/dussen/Stockholm_Accident_Prediction.

Multiple other services have been used. The data is collected from the TOMTOM API. The data and models are stored in Hopsworks as the feature store and model registry. The models are trained using sklearn and then put in the model registry. Therefore there is a TOMTOM api needed as well as a Hopsworks api key. For weather data (see future works) we use the 

# ## 1. Data collection
The data is collected using TOMTOM API. This gives live data of the traffic in the world, and we specifically filter on Stockholm. The problem with this is that it is real time, and in order to get data one must continuously query the API. Therefore we have created a script that queries the API every 2 minutes and stores the data in a csv file. This script is run on a server and is therefore always running. This is within the file get-training-data. Also the inference pipeline does this for one hour at a time. The limitation is the amount of data and different features. The main data is collected in v1, and in v2 an attempt was made to include weather data. However, as the samples are very much correlated and not i.i.d. the performance of all models will be low. The samples do not differ as much from one another.

Current features are
id: The id of the incident, is unique
code: The predefined alert code, describing the event (part of incident).
description: Description of the incident
endTime: End time of the incident
hour: Time of the day
iconCategory: Information 
    0: Unknown
    1: Accident
    2: Fog
    3: Dangerous Conditions
    4: Rain
    5: Ice
    6: Jam
    7: Lane Closed
    8: Road Closed
    9: Road Works
    10: Wind
    11: Flooding
    14: Broken Down Vehicle
latitude: Latitude of the incident
longitude: Longitude of the incident
magnitudeOfDelay:
    0: Unknown
    1: Minor
    2: Moderate
    3: Major
    4: Undefined (used for road closures and other)
month: Month of the occurence
startTime: Starting time of the incident
type: The value is set as "Feature", this is not used as it is always the same


# ## 2. Data preprocessing
The data preprocessing is done in the training pipeline. The data is read from the csv file and then the data is cleaned. This means that some features are removed that have not enough unique values, or are redundant. Also rows will be dropped with missing values (if any), and if there are very large values a log scale is used, this is dependent on the data. The amount of seconds will be predicted. There are more than 1000 samples that are used for training the dataset.

# ## 3. Model training
The model training is also done in the training pipeline. Here a lot of different models are explored on a regression task with the data. The models are trained using sklearn. The models are then evaluated using the mean squared error on a validation set. The models are then stored in the model registry. The models are then available for inference. The split for train, validation and test is 80%, 10% and 10% respectively. The best regression model is then used in the prediction on huggingface, and stored on HopsWorks.

We tried the following models:
* Linear regression
* Multi layer perceptron
* Random forest
* Gradient boosting
* Decision tree
* K nearest neighbors
* Support vector machine
* XGBRegressor


# ## X. Future works
The future works are to add more features to the data. For example weather data, which is available from SMHI. The inference pipeline already collects pressure, temperature and weather information. To limit the effect of the data being highly dependent a lot of different samples must be obtained. Now we only have data from one week within december, and a whole year of data would lead to better results and more features. In general more features are needed, the weather is one of them but there are more ideas on this. Think of the amount of general traffic, the amount of current incidents (more incidents leads to less resources on fixing the specific one, this requires trial and error), more information on each incident, amount of snow, is it raining or slippery. This requires more analysis again, but the model can now be used to get an idea of how long it will take, which is a very rough estimate due to the limitation of data. In addition  information to the roads can be given, such as the amount of lanes, the type of street, the amount of traffic lights and the amount of traffic signs. This data is hard to obtain but can influence the prediction performance.

One label that is currently left out and should be added is the description, which should be incorporated in the model. This is a text field and therefore requires a different approach. For now the description is only shown to the user, but it contains a lot of information that can be used to predict the duration.
 The tomtom api also has other features that will be included:
delay: The delay in seconds
roadNumbers: The road numbers of the incident
probabilityOfOccurrence:
    * certain
    * probable
    * risk_of
    * improbable
numberOfReports: The amount of reports of the incident

Another topic for the future is data validation. The data is now not validated, and therefore the data can be wrong. This can be done by checking the data with other sources, and if the data is wrong it can be removed. 