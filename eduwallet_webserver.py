#!/usr/bin/env python3

# Main code for serving pages and some REST api functions
#
# Uses the Flask web framework
# Uses Amazon Cognito (boto3 library)

import sys, random
import requests, json
import datetime, time
import decimal
from flask import Flask, url_for, abort, request, redirect
from flask import render_template, session, jsonify
# skip SSL standalone, use certbot/apache2 instead
# from flask_sslify import SSLify
import boto3
from eduwallet_config import VERSION, NODEURL, SSL_CONTEXT, APPSECRET, COGNITO

app = Flask(__name__)
# sslify = SSLify(app)

# secret_key needed for session support in Flask
app.secret_key = APPSECRET

# Round bitcoin amounts to 8 decimals (satoshis)
# only needed once when going from float values

def float2dec(a):
    a = decimal.Decimal(a)
    return a.quantize(decimal.Decimal(10)**-8)

# Make RPC call to local bitcoin node

def getNode(method, *args):
    headers = {'content-type': 'application/json'}
    payload = {
        "method": method,
        "params": list(args),
    }
    r = requests.post(NODEURL, data=json.dumps(payload), headers=headers).json()
    if r.get('error'):
        print('API error:', r['error'])
    return r

def getNodeResults(method, *args):
    r = getNode(method, *args)
    return r['result']

# Return (inputs, balance) where inputs are [{txid, vout}, ...]
# and balance is a Decimal.
# As preparation for sending or just to calculate the balance.

def getinputs_balance(addr):
    unspents = getNodeResults('listunspent', 0, 9999999, [addr], True)
    balance = decimal.Decimal('0.0')
    inputs = []
    for u in unspents:
        balance += float2dec(u['amount'])
        inputs += [{'txid': u['txid'], 'vout': u['vout']}]
    return (inputs, balance)
    
# Check wallet to find account address. If new user, create new address
# Returns bitcoin address.

def get_bitcoin_address(email):
    addr_list = getNodeResults('getaddressesbylabel', email)
    if addr_list and len(addr_list) > 0:
        addr = list(addr_list)[0]
    else:
        addr = getNodeResults('getnewaddress', email, 'bech32')
    return addr

# fix crazy cognito double dict format to normal dict
# [{'Value': 'af5de94f-7883-40a2-8dec-ca7bcdab6d65', 'Name': 'sub'}, 
#  {'Value': 'true', 'Name': 'email_verified'},
#  {'Value': 'Thomas', 'Name': 'given_name'},
#  {'Value': 'Lundqvist', '# Name': 'family_name'},
#  {'Value': 'address@domain.com', 'Name': 'email'}]

def doubledict2dict(doubledict):
    attr = {}
    for a in doubledict:
        attr[a['Name']] = a['Value']
    return attr

# Didn't work for redirect, probably hopeless with http and https
# on the same port number.
#
#@app.before_request
#def before_request():
#    print(request.is_secure)
#    if request.url.startswith('http://'):
#        url = request.url.replace('http://', 'https://', 1)
#        code = 301
#        return redirect(url, code=code)

@app.after_request
def set_response_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route("/")
def main_page():
    client_id = COGNITO['client_id']
    redirect_url = COGNITO['redirect_url']
    # if GET args contain 'code' and 'state' it is redirected from Cognito
    # after login attempt
    if 'code' in request.args and 'state' in request.args:
        code = request.args['code']
        state = request.args['state']
        if not 'state' in session or int(state) != session['state']:
            # could be CSRF attack
            return 'Error in authorization'
        del session['state']
        # exchange 'code' for an access token using Cognito TOKEN endpoint url
        token_url = COGNITO['base_url'] + COGNITO['token']
        data={'grant_type':'authorization_code',
              'client_id': client_id,
              'redirect_uri': redirect_url,
              'code': code}
        r = requests.post(token_url, data=data)
        atoken = None
        try:
            atoken = r.json()['access_token']
            # fetch user info from cognito amazon API
            # email is primary identifier
            cog = boto3.client('cognito-idp')
            user = cog.get_user(AccessToken=atoken)
            attr = doubledict2dict(user['UserAttributes'])
            name = attr['given_name'] + ' ' + attr['family_name']
            email = attr['email']
            addr = get_bitcoin_address(email)
            session['email'] = email
            session['name'] = name
            session['addr'] = addr
            session['access_token'] = atoken
            print('Login by', email)
        except ValueError:
            pass
        except KeyError:
            pass
        if not atoken:
            return 'Authorization error'
        return redirect(url_for('main_page'))
    # first entry, redirect to login pages at Cognito
    if not 'access_token' in session:
        login = COGNITO['login']
        state = random.randint(1111,999999999)
        session['state'] = state
        cognito_login = COGNITO['base_url'] + login % (client_id, redirect_url, state)
        return redirect(cognito_login, code=302)
    # Logged in, main page
    addr = session['addr']
    email = session['email']
    inputs, balance = getinputs_balance(addr)
#    txs = get('listtransactions', email)
    return render_template('main-page.html', session=session, page='home', balance=float(balance), txs=[])


@app.route("/logout")
def logout():
    if not 'access_token' in session:
        return redirect(url_for('main_page'))
    del session['access_token']
    client_id = COGNITO['client_id']
    logout = COGNITO['logout']
    logout_url = COGNITO['logout_url']
    cognito_logout = COGNITO['base_url'] + logout % (client_id, logout_url)
    print('Logout by', session['email'])
    return redirect(cognito_logout, code=302)

@app.route("/send")
def send():
    # first entry, redirect to login pages at Cognito
    if not 'access_token' in session:
        return redirect(url_for('main_page'))
    # Logged in, send page
    addr = session['addr']
    email = session['email']
    inputs, balance = getinputs_balance(addr)
    return render_template('send-page.html', session=session, page='send', balance=float(balance))
    return 

@app.route("/receive")
def receive():
    if not 'access_token' in session:
        return redirect(url_for('main_page'))
    # Logged in, send page
    return render_template('receive-page.html', session=session, page='receive')
    return 

@app.route("/api/getbalance", methods = ['GET'])
def getbalance():
    addr = request.args['addr']
    inputs, balance = getinputs_balance(addr)
    return jsonify({'balance': float(balance)})
    
@app.route("/api/makepayment", methods = ['POST'])
def makepayment():
    par = request.form
    payfrom = par['payfrom']
    payto = par['payto']
    amount = float2dec(par['amount'])
    inputs, balance = getinputs_balance(payfrom)
    # Scale fee with inputs, assume one input is max 500 bytes
    fee = float2dec(0.00001 * int((len(inputs)+1)/2))
    change = balance - amount - fee
    if change < 0.0:
        amount = balance - fee
        outputs = { payto: str(amount) }
    else:
        outputs = { payto: str(amount), payfrom: str(change) }
    print('Payment from',payfrom,'to',payto,'amount',amount,'fee',fee,'change',change)
    r = getNode('createrawtransaction', inputs, outputs)
    if r.get('error'):
        return jsonify(r)
    hex = r['result']
    r = getNode('signrawtransactionwithwallet', hex)
    if r.get('error'):
        return jsonify(r)
    signed = r['result']
    if not signed['complete']:
        r['error'] = 'Signing not complete'
        return jsonify(r)
    r = getNode('sendrawtransaction', signed['hex'])
    hash = r['result']
    print(json.dumps(r))
    return jsonify(r)

if __name__ == "__main__":
    app.run(ssl_context=SSL_CONTEXT, port=5100, host='0.0.0.0')
