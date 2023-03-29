Tools that will edit the inbound rules of a given security group.

ipremove will remove all rules associated with a given description, usually username.

ipupdate will remove all rules associated with a given description, usually username, and then will apply new rules.

Currently needed arguments.
{
  "security_group_id": "value1",
  "ip_address": "value2",
  "ports": [
    "port1",
    "port2",
    "port3",
    "etc"
  ],
  "description": "value3"
}

Dynamoedit will look at a dynamodb, grab the user's assigned securitygroup, and then update the IP stored from the provided new IP.
