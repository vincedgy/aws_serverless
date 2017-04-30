"""
weather.py : An AWS lambda fonction for getting weather information from internet
Author : Vincent DAGOURY
Date : 2017-04-27
Description :
This lambda will grab weather report from api.openweathermap.org for a location name.BaseException.BaseException
It will save the content of the response in DynamoDB and will serve back this data from DynamoDB if someone request it again
The purpose of this lambda is to be assembled with API Gateway.BaseException
This lambda has been first writen durint TIAD Camp organized by D2Si on 2017/04/27 in Paris
Enjoy !

/¡\ Please use your own API key from api.openweathermap.org first !!

TODO :
- Safely fail in case of timeout 
- Externalize OpenWeatherMap.org API KEY 
"""
from __future__ import print_function # Python 2/3 compatibility
import urllib2
import urllib
import json
import boto3
import logging
from botocore.exceptions import ClientError

LOGGING_LEVEL = 'INFO'
logging.basicConfig(
        level=getattr(logging, LOGGING_LEVEL),
        format='%(asctime)s \033[0;34m%(name)-12s \033[0;33m%(levelname)-8s \033[0;37m%(message)s\033[0m',
        datefmt='\033[0;31m%m/%d/%Y %I:%M:%S %p\033[0m'
        )

## automate http://api.openweathermap.org/data/2.5/forecast?id=524901&APPID=eb6397a6776974b07c1abc35f64af1a2
API_URL = 'http://api.openweathermap.org/data/2.5/forecast'
API_KEY = 'eb6397a6776974b07c1abc35f64af1a2'

## Uncomment If you use DynDb localy for testing
dynamodb = boto3.resource('dynamodb', region_name='eu-west-1', endpoint_url='http://localhost:8000')
##dynamodb = boto3.resource("dynamodb", region_name='eu-west-1')

def get_weather(q):
    """xxx"""
    data = {}
    try:
        table = dynamodb.Table('weather')
        response = table.get_item(Key={'location': q})
        data = json.loads(response['Item'])
        print("GetItem for DynDB succeeded.")
        #print(json.dumps(data, indent=4))
    except ClientError as e:
        print(e.response['Error']['Message'])
    finally:
        return data

#
def save_weather_data(q, data):
    """xxx"""
    if q is None or data is None:
        return
    else:
        try:
            table = dynamodb.Table('weather')
            response = table.put_item(
                Item={
                    'location': q,
                    'data': data
                    }
            )
            item = response['Item']
            print("PutItem succeeded:")
            print(json.dumps(item, indent=4))
        except ClientError as e:
            print(e.response['Error']['Message'])
        finally:
            return data

#
def lambda_handler(event, context):
    """xxx"""
    # PrintOut Logging info
    # print('LogGroupName = ' + context.logGroupName)
    # print('LogStreamName = ' + context.logStreamName)
    # params represent the Query parameters sent to the API
    params = {}
    params['q'] = event['queryStringParameters']['q']
    params['APPID'] = API_KEY
    # Test if location is stored in DynamoDB
    print('Looking for weather info for location ' + params['q'] + ' from DynDb.')
    data = get_weather(params['q'])
    # If it's not, we ask for the weather service
    if data is None or len(data) == 0:
        print('No data -> Getting weather for location ' + params['q'] + ' from the Web.')
        url_values = urllib.urlencode(params)
        full_url = API_URL + '?' + url_values
        response = urllib2.urlopen(full_url)
        data = response.read()
        if data is not None and len(data) > 1:
            print('Saving data for location ' + params['q'] + ' to DynDb.')
            save_weather_data(params['q'], data)
        else:
            print('No data found for location ' + + params['q'])
    # The data is return
    print('Returning result (even if it''s empty) and ending.')
    return {
        "statusCode": 200,
        "headers": {},
        "body": data
    }

if __name__ == '__main__':
    print('Starting')
    EVENT = {'queryStringParameters':{'q':'Cosne'}}
    CONTEXT = ''
    print(lambda_handler(EVENT, CONTEXT))
