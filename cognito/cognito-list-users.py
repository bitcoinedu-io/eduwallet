#!/usr/bin/env python3

# fix crazy cognito double dict format to normal dict
# [{'Value': 'af5de94f-7883-40a2-8dec-ca7bcdab6d65', 'Name': 'sub'}, 
#  {'Value': 'true', 'Name': 'email_verified'},
#  {'Value': 'Thomas', 'Name': 'given_name'},
#  {'Value': 'Lundqvist', '# Name': 'family_name'},
#  {'Value': 'email@domain.com', 'Name': 'email'}]

def doubledict2dict(doubledict):
    attr = {}
    for a in doubledict:
        attr[a['Name']] = a['Value']
    return attr

import boto3
c = boto3.client('cognito-idp') 
ul = c.list_users(UserPoolId='eu-central-xxxxxxxx')
COLS = '%-15s %-15s %-35s %-7s'
print(COLS % ('Given name', 'Family name', 'Email', 'Verified'))
for user in ul['Users']:
    attr = doubledict2dict(user['Attributes'])
    print(COLS % (attr['given_name'], attr['family_name'], attr['email'], attr['email_verified']))
