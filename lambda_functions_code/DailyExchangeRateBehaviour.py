# import packages
import json
import boto3
from datetime import datetime

def lambda_handler(event, context):
    # read data from the dynamodb
    # currently we only have data against Euro exhange rate
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('CurrencyExchangeInfo')
    response = table.get_item(
        Key={
            'currency_name': 'Euro'
        }
    )
    item = response['Item']
    
    # sort data for the exchange data
    ordered_exchange_data = sorted(item["exchange_rates"].items(), key = lambda x:datetime.strptime(x[0], '%Y-%m-%d'), reverse=True)
    
    # process the data
    current_date = ordered_exchange_data[0][0]
    previous_day_date = ordered_exchange_data[1][0]
    current_data = ordered_exchange_data[0][1]
    previous_day_data = ordered_exchange_data[1][1]
    
    current_rates = [float(i) for i in current_data.values()]
    previous_day_rates = [float(i) for i in previous_day_data.values()]
    
    difference = []
    for x in range(len(current_rates)):
        difference.append(round((current_rates[x] - previous_day_rates[x]), 4))
    
    # generate rest api response
    response_body = {
        "currency_name": item["currency_name"],
        "current_exchange_rates": current_data,
        "current_date": current_date,
        "previous_day_date": previous_day_date,
        "exchnage_rate_change": dict(zip(current_data.keys(), difference))
    }
    return {
        'statusCode': 200,
        'body': response_body
    }
