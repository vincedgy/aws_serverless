
weather.py
============================================================================= 
An AWS lambda fonction for getting weather information from internet

Author : Vincent DAGOURY
Date : 2017-04-27

# Description :
This lambda will grab weather report from api.openweathermap.org for a location name.BaseException.BaseException
It will save the content of the response in DynamoDB and will serve back this data from DynamoDB if someone request it again
The purpose of this lambda is to be assembled with API Gateway.
This lambda has been first writen durint TIAD Camp organized by D2Si on 2017/04/27 in Paris
Enjoy !

## Warning
Please use your own API key from api.openweathermap.org first !!

## TODO :
- Safely fail in case of timeout 
- Externalize OpenWeatherMap.org API KEY 

# Prepare your DynamoDB instance locally

- List local tables
``aws dynamodb list-tables --endpoint-url http://localhost:8000

- Create weather table
``aws dynamodb create-table 