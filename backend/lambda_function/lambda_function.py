"""
Hangman Trivia Backend

Serves as the backend API for the Hangman Trivia game. Retrieves trivia questions and
answers from DynamoDB tables based on difficulty level and ensures questions are not
repeated by filtering out previously seen answers.

@author Yahia Nassab
"""

import boto3
import json
import random

TABLE_NAME_NORMAL = 'hangmantrivia-wordbank-normal'
TABLE_NAME_HARD = 'hangmantrivia-wordbank-hard'
TABLE_NAME_DRUNK = 'hangmantrivia-wordbank-drunk'

def lambda_handler(event, context):
    """
    AWS Lambda entry point for processing trivia game requests.

    This function processes HTTP requests from the game frontend, retrieves appropriate
    trivia questions from DynamoDB based on difficulty level, and returns a random
    question that hasn't been seen by the player yet.

    Args:
        event (dict): AWS Lambda event object containing HTTP request data
        context (LambdaContext): AWS Lambda context object containing runtime information.
                                 Not used in this implementation but required by Lambda.

    Returns:
        dict: HTTP response with status code and JSON body

    ---

    Request Format:
    {
        "difficulty": "normal|hard|drunk",
        "seen": ["answer1", "answer2", ...] // Previously seen answers
    }

    Special Requests:
    {
        "wakeUp": "any_value" // Used to warm up the Lambda function
    }

    Response Format (Success):
    {
        "statusCode": 200,
        "body": {
            "clue": "Capital of France",
            "answer": "PARIS"
        }
    }

    Response Format (No Content):
    {
        "statusCode": 204,
        "body": {
            "message": "No more clues available for this difficulty level!"
        }
    }
    """
    try:
        data = json.loads(event['body'])

        # Return blank response if request is a wake-up call
        if 'wakeUp' in data:
            return {
                'statusCode': 200,
                'body': json.dumps('Hello from Lambda!'),
            }

        chosen_difficulty = data['difficulty']
        seen_answers = data['seen'] if 'seen' in data else []

        match chosen_difficulty:
            case 'normal':
                table_name = TABLE_NAME_NORMAL
            case 'hard':
                table_name = TABLE_NAME_HARD
            case 'drunk':
                table_name = TABLE_NAME_DRUNK

        ddb = boto3.resource('dynamodb')
        table = ddb.Table(table_name)

        response = table.scan()  # retrieve all database items
        all_answers = response.get('Items', [])

        seen_answers = set(seen_answers)
        available_answers = {
            item['answer']: item['clue']
            for item in all_answers
            if item['answer'] not in seen_answers
        }

        if not available_answers:
            return {
            'statusCode': 204,  # No content
            'body': json.dumps({'message': 'No more clues available for this difficulty level!'}),
        }

        answer, clue = random.choice(list(available_answers.items()))

        return {
            'statusCode': 200,
            'body': json.dumps({'clue': clue, 'answer': answer}),
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
        }

