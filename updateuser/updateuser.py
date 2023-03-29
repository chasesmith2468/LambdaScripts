import json
import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    iam_client = boto3.client('iam')
    user = event['User']
    policies = event['Policy']
    
    #check if user exists
    try:
        user_check = iam_client.get_user(UserName=user)
        print(f'User {user} Exists!')
    except ClientError as error:
        if error.response['Error']['Code'] == 'NoSuchEntity':
            print('User does not exist')
            return 'User does not exist.'
        else:
            print('Unexpected error occurred while finding user.... exiting from here', error)
            return 'User could not be queried', error
    
    #Gets user's Attached Policies and removes them.
    try:
        user_policy = iam_client.list_attached_user_policies(UserName=user)
        policy_arns = [x['PolicyArn'] for x in user_policy.get('AttachedPolicies', [])]
        for policy_arn in policy_arns:
            print(f'Detaching User Policy {policy_arn} from {user}')
            iam_client.detach_user_policy(UserName=user, PolicyArn=policy_arn)
        
        user_policy_inline = iam_client.list_user_policies(UserName=user)
        policy_names = user_policy_inline.get('PolicyNames', [])
        for policy_name in policy_names:
            print(f'Removing Inline Policy {policy_name} from {user}')
            iam_client.delete_user_policy(UserName=user, PolicyName=policy_name)
    except ClientError as error:
        if error.response['Error']['Code'] == 'NoSuchEntity':
            print('User Does Not Have Attached Policy')
        else:
            print('Unexpected error occurred while creating group... exiting from here', error)
            return 'User could not be updated', error
    
    #Attaches policies based on ARN string.
    try:
        policy_arns = policies if isinstance(policies, list) else [policies]
        for policy_arn in policy_arns:
            print(f'Attaching Policy {policy_arn} to {user}')
            iam_client.attach_user_policy(UserName=user, PolicyArn=policy_arn)
    except ClientError as error:
        return 'Something broke'
