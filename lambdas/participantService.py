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
participantTable = dynamodb.Table(os.environ["PARTICIPANT_TABLE"])

def lambda_handler(event, context):
    logger.info(f"event: {json.dumps(event)}")
    httpContext = event['requestContext'].get("http", {})
    method = httpContext["method"]
    path = httpContext['path']
    body = json.loads(event.get('body', '{}')) 
    status = 400
    message = "bad request method or malformed request"

    logger.info(f"\npath: {path}\nmethod: {method}\nbody: {body}") 
    
    if method == 'GET' and path == '/participantservice/health':
        response = buildResponse(200, "UP")

    elif method == 'PUT' and path == "/participantservice/create-participant":
        response = createPartcipant(body)

    elif method == "GET" and path == "/participantservice/participant":
        response = getParticipant(body)

    elif method == 'PUT' and path == "/participantservice/participant":
        response = updateParticipant(body)

    else:
        response = buildResponse(status, message)

    return response

# REQUEST HANDLERS ----------------------------------------

def createPartcipant(body):
    discordId = body.get("discordId", "").strip().lower()
    guildId = body.get("guildId", "").strip().lower()

    if discordId == "": 
        return buildResponse(422, "missing required parameters. expected \"discordId\".")
    elif guildId == "": 
        return buildResponse(422, "missing required parameters. expected \"guildId\".") 

    status, message, data = performQuery(participantTable, {"KeyConditionExpression": Key('guildId').eq(guildId) & Key('discordId').eq(discordId)})
    if status != 200:
        return buildResponse(500, "An error occurred, please try again later.")
    if len(data) != 0:
        return buildResponse(422, f"There is already a participant registered with that userId.")
    
    status, message = createNewParticipant(discordId, guildId)
    return buildResponse(status, message)


def updateParticipant(body):
    discordId = body.get("discordId", "").strip().lower()
    guildId = body.get("guildId", "").strip().lower()

    if discordId == "":
        return buildResponse(422, "missing required parameters. expected \"discordId\".")  
    elif guildId == "":
        return buildResponse(422, "missing required parameters. expected \"guildId\".")  
    
    status, message, data = performQuery(participantTable, {"KeyConditionExpression": Key('guildId').eq(guildId) & Key('discordId').eq(discordId)})
    if status != 200:
        return buildResponse(500, "An error occurred, please try again later.")
    if len(data) == 0:
        return buildResponse(404, "participant not found.")

    # TODO: add body validation before updating
    status, message = putItem(participantTable, body)
    return buildResponse(status, message)
    

def getParticipant(body):
    guildId = body.get("guildId", "").strip().lower()
    discordId = body.get("discordId", "").strip().lower()

    if guildId == "":
        return buildResponse(422, "missing required parameters. expected \"guildId\".")
    elif discordId == "":
        return buildResponse(422, "missing required parameters. expected \"discordId\".")
    

    status, message, data = performQuery(participantTable, {"KeyConditionExpression": Key('guildId').eq(guildId) & Key('discordId').eq(discordId)})
    if status != 200:
        return buildResponse(500, "An error occurred, please try again later.")
    if len(data) == 0:
        return buildResponse(404, f"participant not found.")
    return buildResponse(status, message, data[0])


# OTHER OPERATIONS ----------------------------------------
def createNewParticipant(discordId, guildId):
    participant = {
        "guildId": guildId,
        "discordId": discordId,
        "activeCharacter": None
    }
    return putItem(participantTable, participant)