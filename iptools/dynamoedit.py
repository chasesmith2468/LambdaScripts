import boto3
#Testing
# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table_name = "NAME_OF_DATABASE"
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    
    username = event['username']
    new_ip_address = event['ip_address']

    # Query the DynamoDB table for items with matching partition key
    response = table.query(
        KeyConditionExpression='Username = :username',
        ExpressionAttributeValues={
            ':username': username
        }
    )

    # Update the IPAddress attribute for each matching item
    for item in response['Items']:
         table.update_item(
         Key={
                'Username': item['Username'],
                'SecurityGroup': item['SecurityGroup']
            },
            UpdateExpression='SET IPAddress = :new_ip_address',
            ExpressionAttributeValues={
                ':new_ip_address': new_ip_address
            }
        )
        
    return username + "IP address has been updated to " + new_ip_address
