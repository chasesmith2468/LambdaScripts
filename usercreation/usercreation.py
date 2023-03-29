import boto3
import json, string, random, secrets
import logging
from botocore.exceptions import ClientError




def lambda_handler(event, context):
    # Creating an boto3 client representing IAM service.
    iam_client = boto3.client('iam')
    # Pull the AccountID for use later.
    sts_client = boto3.client('sts')
    account_id = sts_client.get_caller_identity()['Account']
    # Recieve group and user name as input
    data1 = event['body']
    data = json.loads(data1)
    group_name = data['GroupName']
    user_name = data['UserName']
    policy_name = data['PolicyName']

    try:
        group_response = iam_client.create_group(
            GroupName=group_name)
    except ClientError as error:
        if error.response['Error']['Code'] == 'EntityAlreadyExists':
            print('Group already exists... Use the same group')
        else:
            print('Unexpected error occured while creating group... exiting from here', error)
            return 'User could not be create', error

    try:
        user = iam_client.create_user(
            UserName=user_name,
            Tags=[
                {
                    'Key': 'Student',
                    'Value': 'Made by Lambda Function'
                }
            ]
        )
    except ClientError as error:
        if error.response['Error']['Code'] == 'EntityAlreadyExists':
            print('User already exists')
        else:
            print('Unexpected error occured while creating user.... exiting from here', error)
            return 'User could not be create', error

    policy_json = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": [
                "ec2:*"
            ],
            "Resource": "*"
        }]
    }

    policy_arn = ''

    try:
        policy = iam_client.create_policy(
            PolicyName=policy_name,
            PolicyDocument=json.dumps(policy_json)
        )
        policy_arn = policy['Policy']['Arn']
    except ClientError as error:
        if error.response['Error']['Code'] == 'EntityAlreadyExists':
            print('Policy already exists... Hence retrieving policy arn')
            policy_arn = 'arn:aws:iam::' + account_id + ':policy/' + policy_name
        else:
            print('Unexpected error occured while creating policy... hence cleaning up', error)
            iam_client.delete_user(UserName=user_name)
            return 'User could not be create', error

    try:
        response = iam_client.attach_user_policy(
            UserName=user_name,
            PolicyArn=policy_arn
        )
    except ClientError as error:
        print('Unexpected error occurred while attaching policy... hence cleaning up', error)
        iam_client.delete_user(UserName=user_name)
        return 'User could not be create', error
    # Extract account ID from policy ARN
    account_id = policy_arn.split(':')[4]
    password = random_string()
    try:
        login_profile = iam_client.create_login_profile(
            UserName=user_name,
            Password=password,
            PasswordResetRequired=True
        )
    except ClientError as error:
        if error.response['Error']['Code'] == 'EntityAlreadyExists':
            print('login profile already exists ')
        else:
            print('Unexpected error occured while creating login profile... hence cleaning up', error)
            return 'User could not be create', error
    print('User with UserName:{0} got created successfully'.format(user_name))

    # Add user to group
    add_user_to_group_res = iam_client.add_user_to_group(
        GroupName=group_name,
        UserName=user_name
    )

    # Now user got created... Sending its details via email
    ses_client = boto3.client('ses')
    sender_email = data['SenderEmail']
    receiver_email = data['ReceiverEmail']
    ses_res = ses_client.send_email(
        Source=sender_email,
        Destination={
            'ToAddresses': [
                receiver_email
            ]
        },
        Message={
            'Subject': {
                'Data': 'You IAM user details'
            },
            'Body': {
                'Text': {
                    'Data': 'Account ID is: "{0}" \nUser name is : "{1}" \nOne time password is : "{2}"'.format(account_id, user_name, password)
                }
            }
        }
    )
    
    #return 'User with UserName:{0} got created successfully'.format(user_name)
    return {
	"statusCode": 200,
	"body": "User was created and email sent."
}
# This function generates random string
def random_string(stringLength=12):
    letters = string.ascii_letters + string.digits + string.punctuation

    while True:
        pwd = ''
        for i in range(stringLength):
            pwd += ''.join(secrets.choice(letters))

        if (any(char in string.punctuation for char in pwd) and any(char in string.digits for char in pwd) and any(char in string.ascii_letters for char in pwd)):
            break    
    return(pwd)
