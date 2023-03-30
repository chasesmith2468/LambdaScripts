import boto3
#testing
def lambda_handler(event, context):
    try:
        # Retrieve the security group ID, IP address, ports, and description from the event
        security_group_id = event['security_group_id']
        ip_address = event['ip_address']
        ports = [int(port) for port in event['ports']]
        user = event['description']

        # Create an EC2 client
        ec2 = boto3.client('ec2')

        # Get the list of ingress rules for the security group
        response = ec2.describe_security_groups(GroupIds=[security_group_id])
        ip_permissions = response['SecurityGroups'][0]['IpPermissions']

        # Print the list of ingress rules to the console
        print(ip_permissions)

        # Remove any ingress rules with a matching description
        new_data = []
        for entry in ip_permissions:
            if len(entry['IpRanges']) > 1:
                for ip_range in entry['IpRanges']:
                    if ip_range['Description'] == user:
                        new_entry = entry.copy()
                        new_entry['IpRanges'] = [ip_range]
                        new_data.append(new_entry)
            else:
                if entry['IpRanges'][0]['Description'] == user:
                    new_data.append(entry)
            
        if len(new_data) > 0:
            for ip_permission in new_data:
                    response = ec2.revoke_security_group_ingress(
                        GroupId=security_group_id,
                        IpPermissions=[ip_permission]
                )
        else:
            print("Nothing Removed")

        # Authorize the ingress rule to allow traffic from the IP address for each port
        for port in ports:
            ec2.authorize_security_group_ingress(
                GroupId=security_group_id,
                IpPermissions=[
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': port,
                        'ToPort': port,
                        'IpRanges': [
                            {'CidrIp': f'{ip_address}/32', 'Description': user
                            },
                        ],
                    }
                ]
            )

        return {
            'statusCode': 200,
            'body': 'IP address added to security group'
        }
    
    except Exception as e:
        print(f'Error: {str(e)}')
        return {
            'statusCode': 500,
            'body': f'Error: {str(e)}'
        }
