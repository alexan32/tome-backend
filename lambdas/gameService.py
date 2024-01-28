# DESCRIPTION: 
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
gameTable = dynamodb.Table(os.environ["GAME_TABLE"])
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

    elif method == 'POST' and path == '/game':
        response = createGame(body)

    elif method == "GET" and path == '/game':
        response = getGame(body)

    else:
        response = buildResponse(status, message)

    return response

# REQUEST HANDLERS ----------------------------------------

def createGame(body):
    ownerUser = body.get("ownerUser", "").strip().lower()
    guildId = body.get("guildId", "").strip().lower()
    ownerId= body.get("ownerId", "").strip().lower()

    if ownerUser == "" or guildId == "" or ownerId == "":
        return buildResponse(401, "missing required parameters. expected \"ownerUser\", \"guildId\", and \"ownerId\".")

    status, message = createNewGame()
    return buildResponse(status, message)


def getGame(body):
    guildId = body.get("guildId", "").strip().lower()
    if guildId == "":
        return buildResponse(401, "missing required parameter \"guildId\".")

    status, message, data = performQuery(gameTable, {"KeyConditionExpression": Key('guildId').eq(guildId)})
    if status != 200:
        return buildResponse(500, message)
    if len(data) == 0:
        return buildResponse(404, f"No matching game for guildId \"{guildId}\"")
    return buildResponse(status, message, data[0])


# OTHER OPERATIONS ----------------------------------------


def createNewGame(guildId, ownerId, ownerUser):
    gameData = {
        "guildId": guildId,
        "ownerId": ownerId,
        "ruleset":{},
        "participants":{},
        "ownerUser": ownerUser,
        "created": getDateString()
    }
    return putItem(gameTable, gameData)