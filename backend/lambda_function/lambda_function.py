import boto3
import json
import random

TABLE_NAME_NORMAL = 'hangmantrivia-wordbank-normal'
TABLE_NAME_HARD = 'hangmantrivia-wordbank-hard'
TABLE_NAME_DRUNK = 'hangmantrivia-wordbank-drunk'

def lambda_handler(event, context):
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
        available_answers = {item['answer']: item['clue'] for item in all_answers if item['answer'] not in seen_answers}

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

