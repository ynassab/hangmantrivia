
"""
Hangman Trivia Game - Database Management Script

Manages the DynamoDB tables that store trivia questions and answers for the
Hangman Trivia game. Updates the database tables with new content from local
word bank files and removes outdated entries.

@author Yahia Nassab
"""

import boto3
import os
import subprocess
import json

# Word banks ignored by git
from word_bank_normal import bank as bank_normal
from word_bank_hard import bank as bank_hard
from word_bank_drunk import bank as bank_drunk

AWS_ACCOUNT_ID = os.environ['AWS_ACCOUNT_ID']

TABLE_NAME_NORMAL = 'hangmantrivia-wordbank-normal'
TABLE_NAME_HARD = 'hangmantrivia-wordbank-hard'
TABLE_NAME_DRUNK = 'hangmantrivia-wordbank-drunk'

PARTITION_KEY = 'answer'
SECONDARY_KEY = 'clue'

def get_temporary_credentials():
    """
    Assume a temporary AWS IAM role for enhanced security.

    Uses AWS STS (Security Token Service) to assume a temporary role with limited
    permissions instead of using long-term access keys. This follows AWS security
    best practices and provides time-limited access to resources.

    Role Requirements:
        - PortfolioWebsiteRole must exist in the target AWS account
        - Role should have the minimum required permissions for DynamoDB operations (read,
          write, delete on the specific tables).
        - PortfolioWebsiteUser profile must have sts:AssumeRole permission for
          PortfolioWebsiteRole

    Notes:
        - Credentials are temporary and will expire after 1 hour
        - The PortfolioWebsiteRole profile should be configured in ~/.aws/credentials or
          ~/.aws/config
        - Role session name 'PortfolioWebsiteSession' is used for AWS CloudTrail logging
    """
    cmd = "aws sts assume-role --profile PortfolioWebsiteUser " + \
    f"--role-arn arn:aws:iam::{AWS_ACCOUNT_ID}:role/PortfolioWebsiteRole " + \
    "--role-session-name PortfolioWebsiteSession"
    result = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE)
    credentials = json.loads(result.stdout)['Credentials']
    os.environ['AWS_ACCESS_KEY_ID'] = credentials['AccessKeyId']
    os.environ['AWS_SECRET_ACCESS_KEY'] = credentials['SecretAccessKey']
    os.environ['AWS_SESSION_TOKEN'] = credentials['SessionToken']
    print('Assumed temporary user role.')


def remove_temporary_credentials():
    """
    Remove temporary AWS credentials from environment variables for security cleanup.

    This function removes the temporary AWS credentials that were set by get_temporary_credentials()
    to prevent credential leakage and ensure clean environment state. It's designed to be called
    in a finally block to guarantee cleanup even if errors occur during deployment.

    Usage Pattern:
        try:
            get_temporary_credentials()
            # Perform CLI operations
        finally:
            remove_temporary_credentials()  # Always cleanup
    """
    for env_variable in ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_SESSION_TOKEN']:
        os.environ.pop(env_variable)


def update_table(bank, table):
    """
    Synchronizes a local word bank with its corresponding DynamoDB table.

    This function performs a two-way sync:
    1. Removes entries from DynamoDB that no longer exist in the local word bank
    2. Adds or updates entries in DynamoDB that exist in the local word bank

    Args:
        bank (dict): Local word bank dictionary {answer: clue, ...}
        table (boto3.resource): DynamoDB table resource object

    """
    response = table.scan()
    existing_keys = [item[PARTITION_KEY] for item in response['Items']]
    keys_to_delete = [key for key in existing_keys if key not in bank]
    for key in keys_to_delete:
          table.delete_item(Key={PARTITION_KEY: key})

    # Update data store with new keys
    for key, val in bank.items():
        table.put_item(Item={PARTITION_KEY: key, SECONDARY_KEY: val})


def main():
    """Main execution function that coordinates the table update process."""
    print('Starting...')
    try:
        get_temporary_credentials()

        ddb = boto3.resource('dynamodb', region_name='us-east-1')
        table_normal = ddb.Table(TABLE_NAME_NORMAL)
        table_hard = ddb.Table(TABLE_NAME_HARD)
        table_drunk = ddb.Table(TABLE_NAME_DRUNK)

        print('Updating Normal Table...')
        update_table(bank_normal, table_normal)
        print('Updating Hard Table...')
        update_table(bank_hard, table_hard)
        print('Updating Drunk Table...')
        update_table(bank_drunk, table_drunk)

    finally:
        remove_temporary_credentials()
        print('Done.')


if __name__ == "__main__":
    main()

