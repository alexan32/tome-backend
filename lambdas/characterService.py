# DESCRIPTION: handlers and functions used to access/maintain characters inside of the game.
# to keep this project game neutral, characters should be thought of as any "creature" inside
# a game.
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
