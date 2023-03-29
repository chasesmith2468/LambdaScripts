Sender email needs to be verified in AWS SES before it will be able to send emails to the world. 
In "Sandbox" mode, both sender and reciever emails have to be verified.

There are a few hardcoded variables that will need to be changed for each specific host AWS account. Currently it is just sender_email.

Test event in lambda uses the following format to trigger the function to work.

{
  "GroupName": "group_to_make_or_select",
  "UserName": "user_to_create_or_update",
  "ReceiverEmail": "created_or_updated_users_email",
  "PolicyName": "policy_name_in_aws"
}
