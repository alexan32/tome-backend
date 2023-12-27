# DESCRIPTION: handlers and functions used access/maintain the participant table, which holds data
# related to players and gms. Not to be confused with "users" service from the login stack, which
# should be used solely for authentication purposes.
#
# NOTES: 
#
# LAST UPDATE: 12/27/2023, lightly_caffienated. 


import logging
import json
import boto3
import os
from lambdas.utils import *
from boto3.dynamodb.conditions import Key

logger = logging.getLogger()
loglevel = os.environ["LOG_LEVEL"]
logger.setLevel(eval(loglevel))

dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    logger.info(f"event: {json.dumps(event)}")
    httpContext = event['requestContext'].get("http", {})
    method = httpContext["method"]
    path = httpContext['path']
    body = json.loads(event.get('body', '{}')) 
    status = 400
    message = "bad request method or malformed request"

    logger.info(f"\npath: {path}\nmethod: {method}\nbody: {body}") 
    
    if method == 'GET' and path == '/health':
        response = buildResponse(200, "UP")

    else:
        response = buildResponse(status, message)

    return response

# REQUEST HANDLERS ----------------------------------------



# OTHER OPERATIONS ----------------------------------------
