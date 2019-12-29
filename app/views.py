# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

# Python modules
import os, logging, requests, json
import string
from random import *
from datetime import datetime

# Flask modules
from flask               import render_template, request, url_for, redirect, send_from_directory
from flask_login         import login_user, logout_user, current_user, login_required
from werkzeug.exceptions import HTTPException, NotFound, abort

# App modules
from app        import app, lm, db, bc
from app.models import User, Verification
from app.forms  import LoginForm, RegisterForm

aie_node_api = 'http://localhost:6870/nxt'
aiq_asset_id = '5384720030523531536'
genesis_block_ts = 1568469599

def get_aiq_balance(aie_account):
    aiereponse = requests.post(aie_node_api+'?requestType=getAccountAssets', data={'account':aie_account, 'asset':aiq_asset_id})
    json_aieresponse = aiereponse.json()
    try:
        balance = float(json_aieresponse["quantityQNT"])/100
    except Exception as e:
        balance = 0.0
    return balance

def get_aie_balance(aie_account):
    aiereponse = requests.post(aie_node_api+'?requestType=getBalance', data={'account':aie_account})
    json_aieresponse = aiereponse.json()
    try:
        balance = float(json_aieresponse["balanceNQT"])/100000000
    except Exception as e:
        balance = 0.0
    return balance

def get_account_transactions(aie_account):
    transactions = {}
    aiereponse = requests.post(aie_node_api+'?requestType=getBlockchainTransactions', data={'account':aie_account, 'lastIndex':10})
    json_aieresponse = aiereponse.json()
    try:
        transactions_raw = json_aieresponse["transactions"]
    except Exception as e:
        transactions_raw = 0
    
    if transactions_raw != 0:
        for transaction in transactions_raw:
            transactions.setdefault(datetime.utcfromtimestamp(genesis_block_ts+int(transaction["timestamp"])).strftime('%Y-%m-%d %H:%M:%S'),{})['sender'] = transaction["senderRS"]
            transactions.setdefault(datetime.utcfromtimestamp(genesis_block_ts+int(transaction["timestamp"])).strftime('%Y-%m-%d %H:%M:%S'),{})['recipient'] = transaction["recipientRS"]
            transactions.setdefault(datetime.utcfromtimestamp(genesis_block_ts+int(transaction["timestamp"])).strftime('%Y-%m-%d %H:%M:%S'),{})['fee'] = str(float(transaction["feeNQT"])/100000000)
            if transaction["type"] == 0 and transaction["subtype"] == 0:
                transactions.setdefault(datetime.utcfromtimestamp(genesis_block_ts+int(transaction["timestamp"])).strftime('%Y-%m-%d %H:%M:%S'),{})['amount'] = str(float(transaction["amountNQT"])/100000000)+" AIE"
            elif transaction["type"] == 2 and transaction["subtype"] == 1:
                if transaction["attachment"]["asset"] == aiq_asset_id:
                    transactions.setdefault(datetime.utcfromtimestamp(genesis_block_ts+int(transaction["timestamp"])).strftime('%Y-%m-%d %H:%M:%S'),{})['amount'] = str(float(transaction["attachment"]["quantityQNT"])/100)+" AIQ"
                else:
                    transactions.setdefault(datetime.utcfromtimestamp(genesis_block_ts+int(transaction["timestamp"])).strftime('%Y-%m-%d %H:%M:%S'),{})['amount'] = "NA"
            else:
                transactions.setdefault(datetime.utcfromtimestamp(genesis_block_ts+int(transaction["timestamp"])).strftime('%Y-%m-%d %H:%M:%S'),{})['amount'] = "NA"
    return transactions

# provide login manager with load_user callback
@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Logout user
@app.route('/logout.html')
def logout():
    logout_user()
    return redirect(url_for('index'))

# Register a new user
@app.route('/register.html', methods=['GET', 'POST'])
def register():
    
    # declare the Registration Form
    form = RegisterForm(request.form)

    msg = None

    if request.method == 'GET': 

        return render_template( 'pages/register.html', form=form, msg=msg )

    # check if both http method is POST and form is valid on submit
    if form.validate_on_submit():

        # assign form data to variables
        username = request.form.get('username', '', type=str)
        password = request.form.get('password', '', type=str) 
        type    = request.form.get('type'   , '', type=str) 
        myaiq_username = type+"-"+username
        if type == "TG":
            allchar = string.ascii_letters + string.digits
            user_tweet = "".join(choice(allchar) for x in range(randint(5, 5)))
            confirm_my_stuff = "/verifyme " + user_tweet
            verification = Verification(username=myaiq_username, confirm_my_stuff=user_tweet)
            verification.set_password(password)
            db.session.add(verification)
            db.session.commit()
            msg = 'Please use telegram, talk to @MyAiqBot and tell him "' + confirm_my_stuff + '"'
            #flash(totweet)
            #return redirect(url_for('login'))

#        # filter User out of database through username
#        user = User.query.filter_by(user=username).first()
#
#        # filter User out of database through username
#        user_by_email = User.query.filter_by(email=email).first()
#
#        if user or user_by_email:
#            msg = 'Error: User exists!'
#        
#        else:         
#
#            pw_hash = password #bc.generate_password_hash(password)
#
#            user = User(username, email, pw_hash)
#
#            user.save()
#
#            msg = 'User created, please <a href="' + url_for('login') + '">login</a>'     

    else:
        msg = 'Input error'     

    return render_template( 'pages/register.html', form=form, msg=msg )

# Authenticate user
@app.route('/login.html', methods=['GET', 'POST'])
def login():
    
    # Declare the login form
    form = LoginForm(request.form)

    # Flask message injected into the page, in case of any errors
    msg = None

    # check if both http method is POST and form is valid on submit
    if form.validate_on_submit():

        # assign form data to variables
        username = request.form.get('username', '', type=str)
        password = request.form.get('password', '', type=str) 
        type    = request.form.get('type'   , '', type=str) 
        myaiq_username = type+"-"+username

        # filter User out of database through username
        user = User.query.filter_by(username=myaiq_username).first()

        if user:
            
            #if bc.check_password_hash(user.password, password):
            if user.check_password(password):
                login_user(user)
                return redirect(url_for('index'))
            else:
                msg = "Wrong password. Please try again."
        else:
            msg = "Unknown user"

    return render_template( 'pages/login.html', form=form, msg=msg ) 

# App main route + generic routing
@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path>')
def index(path):

    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    content = None

    try:

        # @WIP to fix this
        # Temporary solution to solve the dependencies
        if path.endswith(('.png', '.svg' '.ttf', '.xml', '.ico', '.woff', '.woff2')):
            return send_from_directory(os.path.join(app.root_path, 'static'), path)    
        aie_account = current_user.aie_account
        aiq_balance=get_aiq_balance(aie_account)
        aie_balance=get_aie_balance(aie_account)
        transactions=get_account_transactions(aie_account)

        # try to match the pages defined in -> pages/<input file>
        return render_template( 'pages/'+path, aiq_balance=aiq_balance, aie_balance=aie_balance, transactions=transactions )

    except:
        
        return render_template('layouts/auth-default.html',
                                content=render_template( 'pages/404.html' ) )
