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

    else:
        response = buildResponse(status, message)

    return response

# REQUEST HANDLERS ----------------------------------------

def createPartcipant(body):
    username = body.get("username", "").strip().lower()

    if username == "":
        return buildResponse(422, "missing required parameters. expected \"username\".")

    # status, message, data = performQuery(participantTable, {"KeyConditionExpression": Key('username').eq(username)})
    # if status != 200:
    #     return buildResponse(500, message)
    # if len(data) != 0:
    #     return buildResponse(422, f"There is already a participant register with that username.")
    
    status, message = createNewParticipant(username)
    return buildResponse(status, message)


def getParticipant(body):
    pass

# OTHER OPERATIONS ----------------------------------------
def createNewParticipant(username):
    participant = {
        "username": username,
        "discordId": None
    }
    return putItem(participantTable, participant)