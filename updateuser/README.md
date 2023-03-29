This will update a supplied user's policies by removing ALL policies and then applying the polcies specified in the JSON. Policies must be applied by supplied Policy Arn, because it includes AWS generated policies.

Policies can be sent singular or multiple. 

JSON format for singular policy:
{
  "User": "Username",
  "Policy": "Arn of Policy"
}

Multiple Policies can be added as below.

{
  "User": "Username",
  "Policy": ["Policy ARN #1", "Policy ARN #2", etc...]
}
