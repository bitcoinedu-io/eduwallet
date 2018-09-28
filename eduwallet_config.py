# Common config for eduwallet

VERSION = '1.0'
GITHUB = 'https://github.com/bitcoinedu-io/eduwallet'

rpc_user = 'user'
rpc_pass = 'pass'
NODEURL = 'http://%s:%s@localhost:8332' % (rpc_user, rpc_pass)

sslfiles = '/.../ssl/current/'
SSL_CONTEXT = (sslfiles+'ssl.crt',sslfiles+'ssl.key')

# For flask session support, just a big random binary string
APPSECRET = b'tooshort'

# Config for Amazon Cognito authentication service

# An amazon web services developer account is needed with credentials and config
# in ~/.aws/ like:
# ~/.aws/credentials
#  [default]
#  aws_access_key_id = ...
#  aws_secret_access_key = ...
#
# ~/.aws/config
#  [default]
#  region=eu-central-1
#
# The name of the user pool created on Cognito is 'eduwallet'.

COGNITO = {
    'client_id': '',
    'redirect_url': '',
    'logout_url': '',
    'base_url': 'https://eduwallet.auth.eu-central-1.amazoncognito.com/',
    'login': 'login?response_type=code&client_id=%s&redirect_uri=%s&state=%s',
    'logout': 'logout?client_id=%s&logout_uri=%s',
    'token': 'oauth2/token'
}

