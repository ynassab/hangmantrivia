"""
Test Suite: Lambda Function (Hangman Trivia Backend)

Test coverage for lambda_function.py - AWS Lambda handler for the backend API
"""

import pytest
import os
import json
from unittest import mock
from moto import mock_aws
import boto3

# The module to test
from backend.lambda_function import lambda_function

TABLE_NAME_NORMAL = 'hangmantrivia-wordbank-normal'
TABLE_NAME_HARD = 'hangmantrivia-wordbank-hard'
TABLE_NAME_DRUNK = 'hangmantrivia-wordbank-drunk'

PARTITION_KEY = 'answer'
SECONDARY_KEY = 'clue'

AWS_REGION = 'us-east-1'

@pytest.fixture
def lambda_event_normal():
    """Sample Lambda event for normal difficulty."""
    return {
        'body': json.dumps({
            'difficulty': 'normal',
            'seen': []
        })
    }

@pytest.fixture
def lambda_event_hard():
    """Sample Lambda event for hard difficulty."""
    return {
        'body': json.dumps({
            'difficulty': 'hard',
            'seen': []
        })
    }

@pytest.fixture
def lambda_event_drunk():
    """Sample Lambda event for drunk difficulty."""
    return {
        'body': json.dumps({
            'difficulty': 'drunk',
            'seen': []
        })
    }

@pytest.fixture
def lambda_context():
    """Mock Lambda context object."""
    return mock.Mock()


class TestLambdaFunction:
    """Test cases for the AWS Lambda function handler."""

    @mock_aws
    def test_lambda_handler_wake_up_call(self, lambda_context):
        """Test that wake-up calls return a simple greeting."""
        event = {
            'body': json.dumps({'wakeUp': 'Hello from Hangman Trivia!'})
        }
        result = lambda_function.lambda_handler(event, lambda_context)

        assert result['statusCode'] == 200

    @mock_aws
    @mock.patch.dict(os.environ, {'AWS_DEFAULT_REGION': AWS_REGION})
    def test_lambda_handler_normal_difficulty_success(self, lambda_event_normal, lambda_context):
        """Test successful retrieval of normal difficulty question."""
        # Set up mock DynamoDB table
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.create_table(
            TableName=TABLE_NAME_NORMAL,
            KeySchema=[{'AttributeName': PARTITION_KEY, 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': PARTITION_KEY, 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )

        # Add test data
        table.put_item(Item={PARTITION_KEY: 'ANSWER 1', SECONDARY_KEY: 'Clue 1'})
        table.put_item(Item={PARTITION_KEY: 'ANSWER 2', SECONDARY_KEY: 'Clue 2'})

        result = lambda_function.lambda_handler(lambda_event_normal, lambda_context)

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert SECONDARY_KEY in body
        assert PARTITION_KEY in body
        assert body[PARTITION_KEY] in ['ANSWER 1', 'ANSWER 2']

    @mock_aws
    @mock.patch.dict(os.environ, {'AWS_DEFAULT_REGION': AWS_REGION})
    def test_lambda_handler_hard_difficulty_success(self, lambda_event_hard, lambda_context):
        """Test successful retrieval of hard difficulty question."""
        # Set up mock DynamoDB table
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.create_table(
            TableName=TABLE_NAME_HARD,
            KeySchema=[{'AttributeName': PARTITION_KEY, 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': PARTITION_KEY, 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )

        table.put_item(Item={PARTITION_KEY: 'HARD ANSWER', SECONDARY_KEY: 'Hard clue'})

        result = lambda_function.lambda_handler(lambda_event_hard, lambda_context)

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body[PARTITION_KEY] == 'HARD ANSWER'
        assert body[SECONDARY_KEY] == 'Hard clue'

    @mock_aws
    @mock.patch.dict(os.environ, {'AWS_DEFAULT_REGION': AWS_REGION})
    def test_lambda_handler_drunk_difficulty_success(self, lambda_event_drunk, lambda_context):
        """Test successful retrieval of drunk difficulty question."""
        # Set up mock DynamoDB table
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.create_table(
            TableName=TABLE_NAME_DRUNK,
            KeySchema=[{'AttributeName': PARTITION_KEY, 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': PARTITION_KEY, 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )

        table.put_item(Item={PARTITION_KEY: 'DRUNK ANSWER', SECONDARY_KEY: 'Drunk clue'})

        result = lambda_function.lambda_handler(lambda_event_drunk, lambda_context)

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body[PARTITION_KEY] == 'DRUNK ANSWER'
        assert body[SECONDARY_KEY] == 'Drunk clue'

    @mock_aws
    @mock.patch.dict(os.environ, {'AWS_DEFAULT_REGION': AWS_REGION})
    def test_lambda_handler_with_seen_answers(self, lambda_context):
        """Test filtering out previously seen answers."""
        # Set up mock DynamoDB table
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.create_table(
            TableName=TABLE_NAME_NORMAL,
            KeySchema=[{'AttributeName': PARTITION_KEY, 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': PARTITION_KEY, 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )

        table.put_item(Item={PARTITION_KEY: 'ANSWER 1', SECONDARY_KEY: 'Clue 1'})
        table.put_item(Item={PARTITION_KEY: 'ANSWER 2', SECONDARY_KEY: 'Clue 2'})

        event = {
            'body': json.dumps({
                'difficulty': 'normal',
                'seen': ['ANSWER 1']  # ANSWER 1 already seen
            })
        }

        result = lambda_function.lambda_handler(event, lambda_context)

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body[PARTITION_KEY] == 'ANSWER 2'  # Should only get ANSWER 2

    @mock_aws
    @mock.patch.dict(os.environ, {'AWS_DEFAULT_REGION': AWS_REGION})
    def test_lambda_handler_no_content_available(self, lambda_context):
        """Test response when all questions have been seen."""
        # Set up mock DynamoDB table
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.create_table(
            TableName=TABLE_NAME_NORMAL,
            KeySchema=[{'AttributeName': PARTITION_KEY, 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': PARTITION_KEY, 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )

        table.put_item(Item={PARTITION_KEY: 'ANSWER 1', SECONDARY_KEY: 'Clue 1'})

        event = {
            'body': json.dumps({
                'difficulty': 'normal',
                'seen': ['ANSWER 1']  # All questions seen
            })
        }

        result = lambda_function.lambda_handler(event, lambda_context)

        assert result['statusCode'] == 204
        body = json.loads(result['body'])
        assert body['message'] == 'No more clues available for this difficulty level!'

    @mock_aws
    @mock.patch.dict(os.environ, {'AWS_DEFAULT_REGION': AWS_REGION})
    def test_lambda_handler_empty_table(self, lambda_event_normal, lambda_context):
        """Test response when table is empty."""
        # Set up empty mock DynamoDB table
        dynamodb = boto3.resource('dynamodb')
        dynamodb.create_table(
            TableName=TABLE_NAME_NORMAL,
            KeySchema=[{'AttributeName': PARTITION_KEY, 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': PARTITION_KEY, 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )

        result = lambda_function.lambda_handler(lambda_event_normal, lambda_context)

        assert result['statusCode'] == 204

    def test_lambda_handler_invalid_json(self, lambda_context):
        """Test error handling for invalid JSON in request body."""
        event = {
            'body': 'invalid json'
        }

        result = lambda_function.lambda_handler(event, lambda_context)

        assert result['statusCode'] == 500
        body = json.loads(result['body'])
        assert 'error' in body

    def test_lambda_handler_missing_body(self, lambda_context):
        """Test error handling when request body is missing."""
        event = {}

        result = lambda_function.lambda_handler(event, lambda_context)

        assert result['statusCode'] == 500
        body = json.loads(result['body'])
        assert 'error' in body

    @mock_aws
    @mock.patch.dict(os.environ, {'AWS_DEFAULT_REGION': AWS_REGION})
    def test_lambda_handler_missing_seen_field(self, lambda_context):
        """Test that missing 'seen' field defaults to empty list."""
        # Set up mock DynamoDB table
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.create_table(
            TableName=TABLE_NAME_NORMAL,
            KeySchema=[{'AttributeName': PARTITION_KEY, 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': PARTITION_KEY, 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )

        table.put_item(Item={PARTITION_KEY: 'ANSWER 1', SECONDARY_KEY: 'Clue 1'})

        event = {
            'body': json.dumps({
                'difficulty': 'normal'
                # No 'seen' field
            })
        }

        result = lambda_function.lambda_handler(event, lambda_context)

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body[PARTITION_KEY] == 'ANSWER 1'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

