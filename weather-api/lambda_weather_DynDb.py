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

Warning : Please use your own API key from api.openweathermap.org first !!

TODO :
- Safely fail in case of timeout
- Externalize OpenWeatherMap.org API KEY
"""
from __future__ import print_function  # Python 2/3 compatibility
import traceback
import json
import logging
import sys
import urllib
import urllib2
import boto3
from botocore.exceptions import ClientError

LOGGING_LEVEL = 'INFO'
#logging.basicConfig(
#    level = getattr(logging, LOGGING_LEVEL),
#    format = '%(asctime)s \033[0;34m%(name)-12s \033[0;33m%(levelname)-8s \033[0;37m%(message)s\033[0m',
#    datefmt = '\033[0;31m%m/%d/%Y %I:%M:%S %p\033[0m'
#)
logging.basicConfig(
    level = getattr(logging, LOGGING_LEVEL),
    format = '%(asctime)s %(name)-8s %(levelname)-8s %(message)s',
    datefmt = '%Y-%m-%d %I:%M:%S %p'
)

## automate http://api.openweathermap.org/data/2.5/forecast?id=524901&APPID=eb6397a6776974b07c1abc35f64af1a2
API_URL = 'http://api.openweathermap.org/data/2.5/forecast'
API_KEY = 'eb6397a6776974b07c1abc35f64af1a2'
TABLE_NAME = 'weather'

REQUEST_HEADERS = {
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
"Accept": "application/json",
}

# Globals
_dynamodb = boto3.resource('dynamodb', region_name='eu-west-1', endpoint_url='http://localhost:8000')
##_dynamodb = boto3.resource("dynamodb", region_name='eu-west-1')    

## Uncomment If you use DynDb localy for testing
def getTable(dynamodb, tablename):
    try:
        table = dynamodb.Table(tablename)
        logging.info('Table ' + tablename + ' exists since ' + str(table.creation_date_time))
        return table
    except ClientError as e:
        if e.response['Error']['Code'] == u'ResourceNotFoundException':
            logging.error('Table ' + tablename + ' needs to be created.')
            try:
                table = dynamodb.create_table(
                    TableName=tablename,
                    KeySchema=[{'AttributeName': 'location', 'KeyType': 'HASH'}],
                    AttributeDefinitions=[{'AttributeName': 'location', 'AttributeType': 'S'}],
                    ProvisionedThroughput={'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1}
                    )
                return table
            except ClientError:
                traceback.print_exc()
                sys.exit(1)

# =============================================================================
def get_weather(table, q):
    """xxx"""
    data = {}
    try:
        response = table.get_item(Key={'location':q})
        if response['Item'] is not None:
            data = response['Item']
        #print(json.dumps(data, indent=4))
    except KeyError:
        logging.info("No data found in DynDB")
    except ClientError as e:
        logging.error(repr(traceback.format_stack(),e))
    finally:
        return data

# =============================================================================
def save_weather_data(table, q, data):
    """xxx"""
    if q is None or data is None:
        return
    else:
        try:
            item = {}
            item['location'] = q
            item['list']={}
            for i in xrange(0, len(data['list'])):
                item['list'][i] = data['list'][i]
                i += 1
            item['city'] = {}
            item['city']['country'] = data['city']['country']
            item['city']['id'] = data['city']['id']
            item['city']['coord']={}
            item['city']['coord']['lat'] = str(data['city']['coord']['lat'])
            item['city']['coord']['lon'] = str(data['city']['coord']['lon'])
            item['cod'] = data['cod']
            item['cnt'] = data['cnt']
            #item['list'] = json.dumps(data['list'])
            response = table.put_item(Item = item)
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                logging.info("PutItem succeeded:")
                logging.debug(json.dumps(item, indent=4))
        except (Exception, ClientError) as error:
            logging.error(error)
        finally:
            return data
    return


# =============================================================================
def lambda_handler(event, context):
    """xxx"""
    # params represent the Query parameters sent to the API
    params = {}
    params['q'] = event['queryStringParameters']['q']
    params['APPID'] = API_KEY
    # Test if location is stored in DynamoDB
    logging.info('Looking for weather info for location ' + params['q'] + ' from DynDb.')
    table = getTable(_dynamodb, TABLE_NAME)
    data = get_weather(table, params['q'])
    content = ''
    # If it's not, we ask for the weather service
    if data is None or len(data) == 0:
        logging.info('No data -> Getting weather for location ' + params['q'] + ' from the Web.')
        url_values = urllib.urlencode(params)
        full_url = API_URL + '?' + url_values
        request = urllib2.Request(full_url, headers=REQUEST_HEADERS)
        response = urllib2.urlopen(request)
        content = response.read()
        data = json.loads(content)
        if content is not None and len(content) > 1:
            logging.info('Saving data for location ' + params['q'] + ' to DynDb.')
            save_weather_data(table, params['q'], json.loads(content))
        else:
            logging.info('No data found for location ' + + params['q'])
    logging.info('Returning result (even if it''s empty) and ending.')
    return {
        "statusCode": 200,
        "headers": {},
        "body": data
    }

# =============================================================================
if __name__ == '__main__':
    logging.info('Starting main function (for testing...')
    EVENT = {'queryStringParameters':{'q':'Orleans'}}
    CONTEXT = ''
    logging.info(lambda_handler(EVENT, CONTEXT))
