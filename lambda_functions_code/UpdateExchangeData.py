#importing packages

import json
import boto3
import urllib3
from datetime import datetime
from xml.etree import ElementTree

def lambda_handler(event, context):
    
    # get currency excahnge data
    http = urllib3.PoolManager()
    response = http.request('GET', "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist-90d.xml")
    
    # process xml data from the european bank api
    tree_response = ElementTree.fromstring(response.data)
    
    # filter the data
    current_date_ex_rate = {}
    for child in tree_response.iter('*'):
        if "time" in child.attrib.keys():
            current_date_ex_rate[child.attrib["time"]] = {}
            current_iteration_date = child.attrib["time"]
        elif "currency" in child.attrib.keys():
            current_date_ex_rate[current_iteration_date][child.attrib["currency"]] = child.attrib["rate"]
            
    # data ingestion to dynamodb table
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('CurrencyExchangeInfo')
    response = table.put_item(
      Item={
            'currency_name': 'Euro',
            "exchange_rates": current_date_ex_rate
            
        }
    )

    return {
        'statusCode': 200,
        'body': response
    }
