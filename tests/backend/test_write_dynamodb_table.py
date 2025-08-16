"""
Test Suite: Write DynamoDB Table (Hangman Trivia Backend)

Test coverage for write_dynamodb_table.py - Database management script
"""

import pytest
import json
import os
import subprocess
from unittest import mock
from moto import mock_aws
import boto3

# The module to test
from backend.db_management import write_dynamodb_table

TABLE_NAME_NORMAL = 'hangmantrivia-wordbank-normal'
TABLE_NAME_HARD = 'hangmantrivia-wordbank-hard'
TABLE_NAME_DRUNK = 'hangmantrivia-wordbank-drunk'

PARTITION_KEY = 'answer'
SECONDARY_KEY = 'clue'

AWS_REGION = 'us-east-1'

TEST_KEY_ID = 'test-key-id'
TEST_SECRET_KEY = 'test-secret-key'
TEST_SESSION_TOKEN = 'test-session-token'
TEST_AWS_ACCOUNT_ID = '123456789012'

class TestWriteDynamoDBTable:
    """Test cases for the database management script."""

    @mock.patch('subprocess.run')
    def test_get_temporary_credentials_success(self, mock_subprocess):
        """Test successful credential assumption."""
        # Mock subprocess response
        mock_result = mock.Mock()
        mock_result.stdout = json.dumps({
            'Credentials': {
                'AccessKeyId': TEST_KEY_ID,
                'SecretAccessKey': TEST_SECRET_KEY,
                'SessionToken': TEST_SESSION_TOKEN
            }
        })
        mock_subprocess.return_value = mock_result

        # Mock environment variable
        with mock.patch.dict(os.environ, {'AWS_ACCOUNT_ID': TEST_AWS_ACCOUNT_ID}):
            write_dynamodb_table.get_temporary_credentials()

            # Verify subprocess was called once with correct parameters
            mock_subprocess.assert_called_once()

            # Verify environment variables were set correctly
            assert os.environ['AWS_ACCESS_KEY_ID'] == TEST_KEY_ID
            assert os.environ['AWS_SECRET_ACCESS_KEY'] == TEST_SECRET_KEY
            assert os.environ['AWS_SESSION_TOKEN'] == TEST_SESSION_TOKEN

    @mock.patch('subprocess.run')
    def test_get_temporary_credentials_failure(self, mock_subprocess):
        """Test handling of credential assumption failure."""
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, 'aws sts assume-role')

        with mock.patch.dict(os.environ, {'AWS_ACCOUNT_ID': TEST_AWS_ACCOUNT_ID}):
            with pytest.raises(subprocess.CalledProcessError):
                write_dynamodb_table.get_temporary_credentials()

    def test_remove_temporary_credentials(self):
        """Test removal of temporary credentials from environment."""
        # Set up environment variables
        os.environ['AWS_ACCESS_KEY_ID'] = 'test-key'
        os.environ['AWS_SECRET_ACCESS_KEY'] = 'test-secret'
        os.environ['AWS_SESSION_TOKEN'] = 'test-token'

        write_dynamodb_table.remove_temporary_credentials()

        # Verify environment variables were removed
        assert 'AWS_ACCESS_KEY_ID' not in os.environ
        assert 'AWS_SECRET_ACCESS_KEY' not in os.environ
        assert 'AWS_SESSION_TOKEN' not in os.environ

    def test_remove_temporary_credentials_missing_vars(self):
        """Test that removing non-existent credentials doesn't cause errors."""
        # Ensure variables don't exist
        for var in ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_SESSION_TOKEN']:
            os.environ.pop(var, None)

        # Should not raise an exception
        write_dynamodb_table.remove_temporary_credentials()

    @mock_aws
    def test_update_table_add_new_items(self):
        """Test adding new items to DynamoDB table."""
        # Set up mock table
        dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
        table = dynamodb.create_table(
            TableName='test-table',
            KeySchema=[{'AttributeName': PARTITION_KEY, 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': PARTITION_KEY, 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )

        # Test data
        bank = {'ANSWER 1': 'Clue 1', 'ANSWER 2': 'Clue 2'}

        write_dynamodb_table.update_table(bank, table)

        # Verify items were added
        response = table.scan()
        items = response['Items']
        assert len(items) == 2

        answers = {item[PARTITION_KEY] for item in items}
        assert answers == {'ANSWER 1', 'ANSWER 2'}

    @mock_aws
    def test_update_table_remove_old_items(self):
        """Test removing items that no longer exist in word bank."""
        # Set up mock table with existing data
        dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
        table = dynamodb.create_table(
            TableName='test-table',
            KeySchema=[{'AttributeName': PARTITION_KEY, 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': PARTITION_KEY, 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )

        # Add existing items
        table.put_item(Item={PARTITION_KEY: 'ANSWER 1', SECONDARY_KEY: 'Clue 1'})
        table.put_item(Item={PARTITION_KEY: 'ANSWER 2', SECONDARY_KEY: 'Clue 2'})

        # New bank only has ANSWER 1
        bank = {'ANSWER 1': 'Clue 1'}

        write_dynamodb_table.update_table(bank, table)

        # Verify ANSWER 2 was removed, ANSWER 1 remains
        response = table.scan()
        items = response['Items']
        assert len(items) == 1
        assert items[0][PARTITION_KEY] == 'ANSWER 1'

    @mock_aws
    def test_update_table_update_existing_items(self):
        """Test updating existing items with new clues."""
        # Set up mock table with existing data
        dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
        table = dynamodb.create_table(
            TableName='test-table',
            KeySchema=[{'AttributeName': PARTITION_KEY, 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': PARTITION_KEY, 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )

        # Add existing item
        table.put_item(Item={PARTITION_KEY: 'ANSWER 1', SECONDARY_KEY: 'Old clue'})

        # Update with new clue
        bank = {'ANSWER 1': 'New clue'}

        write_dynamodb_table.update_table(bank, table)

        # Verify clue was updated
        response = table.get_item(Key={PARTITION_KEY: 'ANSWER 1'})
        assert response['Item'][SECONDARY_KEY] == 'New clue'

    @mock.patch('backend.db_management.write_dynamodb_table.get_temporary_credentials')
    @mock.patch('backend.db_management.write_dynamodb_table.remove_temporary_credentials')
    @mock.patch('backend.db_management.write_dynamodb_table.update_table')
    @mock.patch('boto3.resource')
    def test_main_function_success(self, mock_boto3, mock_update_table,
                                   mock_remove_creds, mock_get_creds):
        """Test successful execution of main function."""
        # Set up mocks
        mock_ddb = mock.Mock()
        mock_boto3.return_value = mock_ddb

        mock_table_normal = mock.Mock()
        mock_table_hard = mock.Mock()
        mock_table_drunk = mock.Mock()

        mock_ddb.Table.side_effect = [mock_table_normal, mock_table_hard, mock_table_drunk]

        write_dynamodb_table.main()

        # Verify credentials were handled
        mock_get_creds.assert_called_once()
        mock_remove_creds.assert_called_once()

        # Verify DynamoDB resource was created
        mock_boto3.assert_called_once_with('dynamodb', region_name=AWS_REGION)

        # Verify tables were accessed
        expected_calls = [
            mock.call(TABLE_NAME_NORMAL),
            mock.call(TABLE_NAME_HARD),
            mock.call(TABLE_NAME_DRUNK)
        ]
        mock_ddb.Table.assert_has_calls(expected_calls)

        # Verify update_table was called for each difficulty
        assert mock_update_table.call_count == 3

    @mock.patch('backend.db_management.write_dynamodb_table.get_temporary_credentials')
    @mock.patch('backend.db_management.write_dynamodb_table.remove_temporary_credentials')
    @mock.patch('boto3.resource')
    def test_main_function_exception_handling(self, mock_boto3, mock_remove_creds, mock_get_creds):
        """Test that credentials are always cleaned up even if an exception occurs."""
        # Make boto3.resource raise an exception
        mock_boto3.side_effect = Exception("AWS connection failed")

        with pytest.raises(Exception, match="AWS connection failed"):
            write_dynamodb_table.main()

        # Verify credentials were still cleaned up
        mock_get_creds.assert_called_once()
        mock_remove_creds.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

