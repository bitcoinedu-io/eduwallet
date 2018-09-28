# eduwallet
Web wallet for Bitcoin Edu

- Simple implementation relying on the Bitcoin Core node for information
- Written in Python 3 using the Flask web framework
- Makes transactions using only RPC-api of Bitcoin Core node
- Relies on the Amazon Cognito service for authentication and handling of users

## Installation
Using normal linux package management:
- Install python 3 (debian package: python3)
- Install pip for python 3 (debian package: python3-pip)

Using pip (or maybe distribution packages as above):
- pip3 install requests
- pip3 install flask

Run:
- Make sure you have a Bitcoin Core node running (bitcoind or bitcoin-qt)
- Enable RPC and txindex in bitcoin.conf (server=1, rpcuser=xxx, rpcpassword=yyy, txindex=1)
- Modify config in eduwallet_config.py
- Run preferably via mod_wsgi and apache2

## Implementation overview

The web server part consists of the following files:
- **eduwallet_webserver.py** - the main web server methods (using Flask)
- **static/main.css** - css used for all pages
- **template/** - templates for all html pages (Flask templates)

Templates:
- **main-page** - main page

