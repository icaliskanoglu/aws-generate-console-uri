#!/usr/bin/env python
"""
Launch an AWS Web Console.
Usage:
  awsconsole launch --role=<role_arn> [--profile=<profile_name>]
Commands:
  launch - Launch the AWS Console in your default web browser with
           the specified credentials.  The console will be authenticated
           using the IAM Role you specify with the --role option.
"""

from urllib.parse import urlencode
import requests
import boto3
import json
import argparse


issuer_url = 'https://example.com/'
console_url = 'https://console.aws.amazon.com/'
sign_in_url = 'https://signin.aws.amazon.com/federation'


def generate_uri(role_arn, duration=3600, session_name="generate-uri"):
    sts = boto3.client('sts')
    creds = sts.assume_role(
        RoleArn=role_arn,
        RoleSessionName=session_name,
        DurationSeconds=duration
    )

    data = {'sessionId': creds['Credentials']['AccessKeyId'],
         'sessionKey': creds['Credentials']['SecretAccessKey'],
         'sessionToken': creds['Credentials']['SessionToken']}
    json_str = json.dumps(data)
    request_params = {'Action': 'getSigninToken',
              'Session': json_str}

    response = requests.get(sign_in_url, params=request_params)
    urlparams = json.loads(response.text)
    urlparams['Action'] = 'login'
    urlparams['Issuer'] = issuer_url
    urlparams['Destination'] = console_url
    return sign_in_url + '?' + urlencode(urlparams)


if __name__ == '__main__':
  # construct the argument parse and parse the arguments
  parser = argparse.ArgumentParser()
  parser.add_argument("-r", "--role", required=True, help="Requested Role ARN")
  parser.add_argument("-d", "--duration",type=int, required=False, help="Session Duration Second", default=3600)
  parser.add_argument("-s", "--session-name", required=False, help="Session Name", default="generate-uri")

  args = parser.parse_args()
  uri = generate_uri(role_arn=args.role, duration=args.duration, session_name=args.session_name)
  print(uri)
