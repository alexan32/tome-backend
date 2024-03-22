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

    elif method == 'PUT' and path == "/participantservice/participant":
        response = createPartcipant(body)

    elif method == "GET" and path == "/participantservice/participant":
        response = getParticipant(body)

    elif method == 'PUT' and path == "/participantservice/update-participant":
        response = updateParticipant(body)

    else:
        response = buildResponse(status, message)

    return response

# REQUEST HANDLERS ----------------------------------------

def createPartcipant(body):
    userId = body.get("userId", "").strip().lower()
    discordId = body.get("participant", "not_set").strip().lower()

    if userId == "":
        return buildResponse(422, "missing required parameters. expected \"userId\".")

    status, message, data = performQuery(participantTable, {"KeyConditionExpression": Key('userId').eq(userId)})
    if status != 200:
        return buildResponse(500, "An error occurred, please try again later.")
    if len(data) != 0:
        return buildResponse(422, f"There is already a participant registered with that userId.")
    
    status, message = createNewParticipant(userId, discordId)
    return buildResponse(status, message)


def updateParticipant(body):
    userId = body.get("userId", "").strip().lower()

    if userId == "":
        return buildResponse(422, "missing required parameters. expected \"userId\".")  
    
    status, message, data = performQuery(participantTable, {"KeyConditionExpression": Key('userId').eq(userId)})
    if status != 200:
        return buildResponse(500, "An error occurred, please try again later.")
    if len(data) == 0:
        return buildResponse(404, "participant not found.")


    # TODO: add body validation before updating
    status, message = putItem(participantTable, body)
    return buildResponse(status, message)
    

def getParticipant(body):
    userId = body.get("userId", "").strip().lower()
    discordId = body.get("participant", "").strip().lower()

    if userId == "" and discordId == "":
        return buildResponse(422, "missing required parameters. expected \"userId\" or \"participant\".")
    
    if userId != "":
        kwargs = {
            "KeyConditionExpression": Key('userId').eq(userId)
        }
    else:
        kwargs = {
            "IndexName" : "participant-index",
            "KeyConditionExpression": Key('discordId').eq(discordId)
        }

    status, message, data = performQuery(participantTable, kwargs)
    if status != 200:
        return buildResponse(500, "An error occurred, please try again later.")
    if len(data) == 0:
        return buildResponse(404, f"participant not found.")
    return buildResponse(status, message, data[0])


# OTHER OPERATIONS ----------------------------------------
def createNewParticipant(userId, discordId):
    participant = {
        "userId": userId,
        "discordId": discordId,
        "games": [],
        "activeCharacter": None
    }
    return putItem(participantTable, participant)