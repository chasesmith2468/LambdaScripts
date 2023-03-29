import json
import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    # Creating a boto3 client representing IAM service.
    iam_client = boto3.client('iam')
    # Extracting the user to be deleted from the event object.
    #Uncomment below lines and comment out "user = event['User] when we connect to http api
    user = event['User']
    #body = event['body']
    #data = json.loads(body)
    #user = data['User']
    try:
        # Check if the user exists.
        user_check = iam_client.get_user(UserName=user)
        print('User ' + user + ' exists!')
    except ClientError as error:
        # If user does not exist, return appropriate message.
        if error.response['Error']['Code'] == 'NoSuchEntity':
            print('User does not exist')
            return 'User does not exist.'
        else:
            print('Unexpected error occurred while finding user.... exiting from here', error)
            return 'User could not be queried', error

    try:
        # Remove the user's password if one exists.
        login_profile = iam_client.delete_login_profile(UserName=user)
    except ClientError as error:
        if error.response['Error']['Code'] == 'NoSuchEntity':
            print('User does not have a password')
        else:
            print('Unexpected error occurred while creating group... exiting from here', error)
            return 'User could not be deleted', error

    # Remove user's access keys.
    for access_key in iam_client.list_access_keys(UserName=user).get('AccessKeyMetadata', []):
        iam_client.delete_access_key(UserName=user, AccessKeyId=access_key['AccessKeyId'])

    # Remove user's signing certificates.
    for certificate in iam_client.list_signing_certificates(UserName=user).get('Certificates', []):
        iam_client.delete_signing_certificate(UserName=user, CertificateId=certificate['CertificateId'])

    # Remove user's SSH public keys.
    for ssh_key in iam_client.list_ssh_public_keys(UserName=user).get('SSHPublicKeys', []):
        iam_client.delete_ssh_public_key(UserName=user, SSHPublicKeyId=ssh_key['SSHPublicKeyId'])

    # Remove user's Service Specific Credentials.
    for credential in iam_client.list_service_specific_credentials(UserName=user).get('ServiceSpecificCredentials', []):
        iam_client.delete_service_specific_credential(UserName=user, ServiceSpecificCredentialId=credential['ServiceSpecificCredentialId'])

    # Deactivate user's MFA devices.
    for mfa_device in iam_client.list_mfa_devices(UserName=user).get('MFADevices', []):
        iam_client.deactivate_mfa_device(UserName=user, SerialNumber=mfa_device['SerialNumber'])

    # Detach user's attached policies.
    for policy in iam_client.list_attached_user_policies(UserName=user).get('AttachedPolicies', []):
        iam_client.detach_user_policy(UserName=user, PolicyArn=policy['PolicyArn'])

    # Delete user's inline policies.
    for policy_name in iam_client.list_user_policies(UserName=user).get('PolicyNames', []):
        iam_client.delete_user_policy(UserName=user, PolicyName=policy_name)

    # Remove user from all groups.
    for group in iam_client.list_groups_for_user(UserName=user).get('Groups', []):
        iam_client.remove_user_from_group(GroupName=group['GroupName'], UserName=user)

    # Finally delete the user.
    iam_client.delete_user(UserName=user)

    # Return success message after user has been deleted.
    return {
        "statusCode": 200,
	    "body": 'User '+ user + ' has been deleted successfully'
    }
