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
characterTable = dynamodb.Table(os.environ['CHARACTER_TABLE'])


def lambda_handler(event, context):
    logger.info(f"event: {json.dumps(event)}")
    httpContext = event['requestContext'].get("http", {})
    method = httpContext["method"]
    path = httpContext['path']
    body = json.loads(event.get('body', '{}')) 
    status = 400
    message = "bad request method or malformed request"

    logger.info(f"\npath: {path}\nmethod: {method}\nbody: {body}") 
    
    if method == 'GET' and path == '/characterservice/health':
        response = buildResponse(200, "UP")

    elif method == 'GET' and path == '/characterservice/character':
        response = getCharacter(body)

    elif method == 'PUT' and path == '/characterservice/character':
        response = putCharacter(body)

    else:
        response = buildResponse(status, message)

    return response

# REQUEST HANDLERS ----------------------------------------

def getCharacter(body):
    characterId = body.get("characterId", "").strip().lower()
    if characterId == "":
        return buildResponse(401, "missing required parameter \"characterId\".")

    status, message, data = performQuery(characterTable, {"KeyConditionExpression": Key('characterId').eq(characterId)})
    if status != 200:
        return buildResponse(500, message)
    if len(data) == 0:
        return buildResponse(404, f"No matching character for characterId \"{characterId}\"")
    
    return buildResponse(status, message, {"data": data[0]})

def putCharacter(body):
    body["characterId"] = body["characterId"].lower()
    body["participant"] = body["participant"].lower()
    status, message = putItem(characterTable, body)
    return buildResponse(status, message)

# OTHER OPERATIONS ----------------------------------------
