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
import re

# Flask modules
from flask               import render_template, request, url_for, redirect, send_from_directory
from flask_login         import login_user, logout_user, current_user, login_required
from werkzeug.exceptions import HTTPException, NotFound, abort

# App modules
from app        import app, lm, db, bc
from app.models import User, Verification
from app.forms  import LoginForm, RegisterForm

aie_node_api = 'http://localhost:6870/nxt'
btc_node_api = 'https://blockexplorer.com/api/'
aiq_asset_id = '5384720030523531536'
genesis_block_ts = 1568469599

def requests_post_api(url, data):
    requests_post_api_response = requests.post(url, data=data)
    json_requests_post_api_response = requests_post_api_response.json()
    return json_requests_post_api_response

def requests_get_api(url):
    try:
        requests_get_api_response = requests.get(url)
        json_requests_get_api_response = requests_get_api_response.json()
        return json_requests_get_api_response
    except Exception as e:
        print(e)

def get_account_balance(type,account_address):
    if type == "aiq":
        json_response = requests_post_api(aie_node_api+'?requestType=getAccountAssets', {'account':account_address, 'asset':aiq_asset_id})
        if json_response.get('errorDescription', "noError") != "noError":
            balance = "NA"
        else:            
            balance = float(json_response.get('quantityQNT', 0))/100

    elif type == "aie":
        json_response = requests_post_api(aie_node_api+'?requestType=getBalance', {'account':account_address})
        if json_response.get('errorDescription', "noError") != "noError":
            balance = "NA"
        else:            
            balance = float(json_response.get('balanceNQT', 0))/100000000

    elif type == "bitcoin":
        json_response = requests_get_api(btc_node_api+'addr/'+account_address)
        try:
            if json_response.get('balance', "noBalance") == "noBalance":
                balance = "NA"
            else:            
                balance = float(json_response.get('balance', 0))
        except Exception as e:
            balance = "NA"
    return balance, json_response

def get_coingecko_market_chart(currency, vs_currency, days):
    market_data_dict = {}
    market_data = requests_get_api('https://api.coingecko.com/api/v3/coins/'+currency)
    #print(market_data_volume)
    my_data_list = [['7 DAYS','price_change_percentage_7d_in_currency'],['14 DAYS','price_change_percentage_14d_in_currency'],['30 DAYS','price_change_percentage_30d_in_currency'],['60 DAYS','price_change_percentage_60d_in_currency'],['200 DAYS','price_change_percentage_200d_in_currency'],['1 YEAR','price_change_percentage_1y_in_currency']]
    for my_value in my_data_list:
        try:
            market_data_dict.setdefault(market_data["symbol"]+"-"+vs_currency+" Market Data",{}).setdefault("Change Percentage",{})[my_value[0]] = market_data["market_data"][my_value[1]][vs_currency]

        except Exception as e:
            market_data_dict.setdefault(market_data["symbol"]+"-"+vs_currency+" Market Data",{}).setdefault("Change Percentage",{})[my_value[0]] = 0
    mysymbol = market_data["symbol"]
    market_data = requests_get_api('https://api.coingecko.com/api/v3/coins/'+str(currency)+'/market_chart?vs_currency='+str(vs_currency)+'&days='+str(days))
    #print(market_data)
    market_data_prices=','.join([str("{0:.8f}".format(float(item))) for key,item in market_data["prices"] ])
    market_data_volume=','.join([str(item) for key,item in market_data["total_volumes"] ])
    market_data_market_caps=','.join([str(item) for key,item in market_data["market_caps"] ])
    market_data_ts=','.join([str(key) for key,item in market_data["prices"] ])
    #conversion of timestamps to huma readable datetime
    mytimestamps = market_data_ts.split(",")
    mytimes=''
    for mytime in mytimestamps:
        mytimestr = str(datetime.utcfromtimestamp(int(mytime[:-3])).strftime('%Y-%m-%d %H%M'))
        mytimes += mytimestr+','
    mytimes = mytimes[:-1]
    #end of conversion
    market_data_dict.setdefault(mysymbol+"-"+vs_currency+" Market Data",{}).setdefault("Data Series",{})['Price;rgba(237, 231, 246, 0.5);deep-purple-500;deep-purple-700;2'] = market_data_prices
    market_data_dict.setdefault(mysymbol+"-"+vs_currency+" Market Data",{}).setdefault("Data Series",{})['Volume;rgba(232, 245, 233, 0.5);blue-500;blue-700;2'] = market_data_volume
    market_data_dict.setdefault(mysymbol+"-"+vs_currency+" Market Data",{}).setdefault("Data Series",{})['Mcap;rgba(233, 241, 243, 0.5);red-500;red-700;2'] = market_data_market_caps
    market_data_dict.setdefault(mysymbol+"-"+vs_currency+" Market Data",{})['Labels'] = mytimes
    #market_data_dict.setdefault(currency,{})["symbol"] = market_data["symbol"]


    return market_data_dict

def get_market_data():
    market_data_dict = {}
    market_data = requests_get_api('https://api.coingecko.com/api/v3/coins/artiqox/market_chart?vs_currency=btc&days=7')

    market_data_prices=','.join([str("{0:.8f}".format(float(item))) for key,item in market_data["prices"] ])
    market_data_volume=','.join([str(item) for key,item in market_data["total_volumes"] ])
    market_data_serie_names = "Price BTC,Volume"
    market_data_market_caps=','.join([str(item) for key,item in market_data["market_caps"] ])
    market_data_ts=','.join([str(key) for key,item in market_data["prices"] ])
    # Separate on comma.
    mytimestamps = market_data_ts.split(",")
    mytimes=''
    for mytime in mytimestamps:
        mytimestr = str(datetime.utcfromtimestamp(int(mytime[:-3])).strftime('%Y-%m-%d %H%M'))
        mytimes += mytimestr+','
    market_data_dict.setdefault("AIQ-BTC Market Data",{}).setdefault("Data Series",{})['Price;rgba(237, 231, 246, 0.5);deep-purple-500;deep-purple-700;2'] = market_data_prices
    market_data_dict.setdefault("AIQ-BTC Market Data",{}).setdefault("Data Series",{})['Volume;rgba(232, 245, 233, 0.5);blue-500;blue-700;2'] = market_data_volume
    #market_data_dict.setdefault("AIQ-BTC Market Data",{})['Series Styles'] = "rgba(237, 231, 246, 0.5);deep-purple-500;deep-purple-700;2|rgba(232, 245, 233, 0.5);blue-500;blue-700;2"
    market_data_dict.setdefault("AIQ-BTC Market Data",{})['Labels'] = mytimes[:-1]

    market_data_dict.setdefault("AIE-BTC Market Data",{}).setdefault("Data Series",{})['Price;rgba(237, 231, 246, 0.5);deep-purple-500;deep-purple-700;2'] = market_data_prices
    market_data_dict.setdefault("AIE-BTC Market Data",{}).setdefault("Data Series",{})['Volume;rgba(232, 245, 233, 0.5);blue-500;blue-700;2'] = market_data_volume
    market_data_dict.setdefault("AIE-BTC Market Data",{}).setdefault("Data Series",{})['Mcap;rgba(233, 241, 243, 0.5);red-500;red-700;2'] = market_data_market_caps
    #market_data_dict.setdefault("AIE-BTC Market Data",{})['Series Styles'] = "rgba(237, 231, 246, 0.5);deep-purple-500;deep-purple-700;2|rgba(232, 245, 233, 0.5);blue-500;blue-700;2|rgba(233, 241, 243, 0.5);red-500;red-700;2"
    market_data_dict.setdefault("AIE-BTC Market Data",{})['Labels'] = mytimes[:-1]

    market_data = requests_get_api('https://api.coingecko.com/api/v3/coins/artiqox')
    #print(market_data_volume)
    my_data_list = [['7 DAYS','price_change_percentage_7d_in_currency'],['14 DAYS','price_change_percentage_14d_in_currency'],['30 DAYS','price_change_percentage_30d_in_currency'],['60 DAYS','price_change_percentage_60d_in_currency'],['200 DAYS','price_change_percentage_200d_in_currency'],['1 YEAR','price_change_percentage_1y_in_currency']]
    for my_value in my_data_list:
        try:
            market_data_dict.setdefault("AIQ-BTC Market Data",{}).setdefault("Change Percentage",{})[my_value[0]] = market_data["market_data"][my_value[1]]["btc"]
            market_data_dict.setdefault("AIE-BTC Market Data",{}).setdefault("Change Percentage",{})[my_value[0]] = market_data["market_data"][my_value[1]]["btc"]
        except Exception as e:
            market_data_dict.setdefault("AIQ-BTC Market Data",{}).setdefault("Change Percentage",{})[my_value[0]] = 0
            market_data_dict.setdefault("AIE-BTC Market Data",{}).setdefault("Change Percentage",{})[my_value[0]] = 0

    return market_data_dict

def get_account_transactions(type,myparameter):
    transactions = {}
    if type == "artiqox":
        json_response = requests_post_api(aie_node_api+'?requestType=getBlockchainTransactions', {'account':myparameter, 'lastIndex':10})
        try:
            transactions_raw = json_response["transactions"]
        except Exception as e:
            transactions_raw = 0
        
        if transactions_raw != 0:
            for transaction in transactions_raw:
                transactions.setdefault(datetime.utcfromtimestamp(genesis_block_ts+int(transaction["timestamp"])).strftime('%Y-%m-%d %H:%M:%S'),{})['sender'] = transaction["senderRS"]
                
                transactions.setdefault(datetime.utcfromtimestamp(genesis_block_ts+int(transaction["timestamp"])).strftime('%Y-%m-%d %H:%M:%S'),{})['fee'] = str(float(transaction["feeNQT"])/100000000)
                if transaction["type"] == 0 and transaction["subtype"] == 0:
                    transactions.setdefault(datetime.utcfromtimestamp(genesis_block_ts+int(transaction["timestamp"])).strftime('%Y-%m-%d %H:%M:%S'),{})['amount'] = str(float(transaction["amountNQT"])/100000000)+" AIE"
                    transactions.setdefault(datetime.utcfromtimestamp(genesis_block_ts+int(transaction["timestamp"])).strftime('%Y-%m-%d %H:%M:%S'),{})['recipient'] = transaction["recipientRS"]
                elif transaction["type"] == 2 and transaction["subtype"] == 1:
                    if transaction["attachment"]["asset"] == aiq_asset_id:
                        transactions.setdefault(datetime.utcfromtimestamp(genesis_block_ts+int(transaction["timestamp"])).strftime('%Y-%m-%d %H:%M:%S'),{})['amount'] = str(float(transaction["attachment"]["quantityQNT"])/100)+" AIQ"
                        transactions.setdefault(datetime.utcfromtimestamp(genesis_block_ts+int(transaction["timestamp"])).strftime('%Y-%m-%d %H:%M:%S'),{})['recipient'] = transaction["recipientRS"]
                    else:
                        transactions.setdefault(datetime.utcfromtimestamp(genesis_block_ts+int(transaction["timestamp"])).strftime('%Y-%m-%d %H:%M:%S'),{})['amount'] = "NA"
                        transactions.setdefault(datetime.utcfromtimestamp(genesis_block_ts+int(transaction["timestamp"])).strftime('%Y-%m-%d %H:%M:%S'),{})['recipient'] = "NA"
                else:
                    transactions.setdefault(datetime.utcfromtimestamp(genesis_block_ts+int(transaction["timestamp"])).strftime('%Y-%m-%d %H:%M:%S'),{})['amount'] = "NA"
                    transactions.setdefault(datetime.utcfromtimestamp(genesis_block_ts+int(transaction["timestamp"])).strftime('%Y-%m-%d %H:%M:%S'),{})['recipient'] = "NA"
    return transactions

def get_account_properties(account):
    account_properties = {}
    
    json_response = requests_post_api(aie_node_api+'?requestType=getAccountProperties', {'recipient':account})
    try:
        account_properties_raw = json_response["properties"]
    except Exception as e:
        account_properties_raw = 0
    
    if account_properties_raw != 0:
        for property in account_properties_raw:
            account_properties.setdefault(property["property"],{})['setterRS'] = property["setterRS"]
            account_properties.setdefault(property["property"],{})['value'] = property["value"]

    return account_properties

def get_top_accounts(type,myparameter):
    accounts = {}
    accounts_dict = {}
    if type == "artiqox":
#TODO: check how many accounts have aiq, make use of 'lastIndex':myparameter in loop
        json_response = requests_post_api(aie_node_api+'?requestType=getAssetAccounts', {'asset':aiq_asset_id})

        try:
           accounts_raw = json_response["accountAssets"]
        except Exception as e:
            accounts_raw = 0
        
        if accounts_raw != 0:
            for account in accounts_raw:
                accounts[account["accountRS"]] = float(account["quantityQNT"])/100
            #sort by value
            #to get dictionary with accounts: accounts = {k: v for k, v in sorted(accounts.items(), key=lambda item: item[1])}
            #to get of tuples [account, balance]:
            accounts_dict["AIQ"] = sorted(accounts.items(), key=lambda x: x[1])
    return accounts_dict

def get_wallet_details(type,account_address):
    wallet_details = {}
    if type == "artiqox":
        aiq_balance, aiq_balance_json = get_account_balance("aiq",account_address)
        aie_balance, aie_balance_json = get_account_balance("aie",account_address)
        balance = '{0:.2f}'.format(float(aiq_balance))+" AIQ, "+'{0:.8f}'.format(float(aie_balance))+" AIE"
        if balance != "NA AIQ, NA AIE":
            wallet_details['external_explorer'] = "https://block.hebeblock.com/#/account/"+str(account_address)+"?type=Aie"
            wallet_details['type'] = "artiqox"
            wallet_details['address'] = account_address
            wallet_details['balance'] = balance
            transactions = get_account_transactions(type,account_address)
            wallet_details['transactions'] = transactions
    elif type == "bitcoin":
        balance, balance_json = get_account_balance(type,account_address)
        if balance != "NA":
            wallet_details['external_explorer'] = "https://blockexplorer.com/address/"+str(account_address)
            wallet_details['type'] = "bitcoin"
            wallet_details['address'] = account_address
            wallet_details['balance'] = '{0:.8f}'.format(float(balance))+" BTC"
            #transactions = get_account_transactions(type,balance_json)
            #wallet_details['transactions'] = transactions
    return wallet_details

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
        dashboardwallets_dict = {}
        dashboardwallets_list = []
        dashboardwallets_list.append("artiqox:"+aie_account)
        market_data_dict = {}
        account_properties = {}
        account_properties = get_account_properties(aie_account)
        for property in account_properties.keys():
            pattern = re.compile(r'^MyArtiqox Wallet\s{1}(\w+)', re.IGNORECASE)
            result = pattern.match(property)
            if result:
                wallet_label = result.group(1)
                dashboardwallets_list.append(account_properties[property]["value"])
            else:
                wallet_label = "NA"
        print(dashboardwallets_list)
        for mywallet in dashboardwallets_list:
            splits = mywallet.split(":")
            wallet_details = get_wallet_details(splits[0],splits[1])
            if wallet_details:
                dashboardwallets_dict[splits[1]] = wallet_details
                if market_data_dict.get(splits[0],"NA") == "NA":

                    top_accounts = get_top_accounts(splits[0],999)
                    if top_accounts:
                        for coin, data in top_accounts.items():
                            market_data_dict.setdefault(splits[0],{}).setdefault("top_accounts",{}).setdefault(coin,{})["accounts"] = list(reversed(data))
                            market_data_dict.setdefault(splits[0],{}).setdefault("top_accounts",{}).setdefault(coin,{})["club10"] = list(reversed(data[-10:]))
                            market_data_dict.setdefault(splits[0],{}).setdefault("top_accounts",{}).setdefault(coin,{})["club100"] = list(reversed(data[-100:]))
                            market_data_dict.setdefault(splits[0],{}).setdefault("top_accounts",{}).setdefault(coin,{})["club1000"] = list(reversed(data[-1000:]))
                    else:
                        market_data_dict.setdefault(splits[0],{})
        #aiq_balance=get_account_balance("aiq",aie_account)
        #aie_balance=get_account_balance("aie",aie_account)
        #transactions=get_account_transactions("artiqox",aie_account)
        
        # try to match the pages defined in -> pages/<input file>
        return render_template( 'pages/'+path, dashboardwallets_dict = dashboardwallets_dict, linecharts_dict=market_data_dict, barcharts_dict=market_data_dict )

    except Exception as e:
        print (e.message, e.args)
        return render_template('layouts/auth-default.html',
                                content=render_template( 'pages/404.html' ) )

@app.route('/charts.html', methods=['GET', 'POST'])
def charts():

    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    content = None

    try:

        aie_account = current_user.aie_account
        dashboardwallets_dict = {}
        market_data_dict = {}

        json_aieresponse = requests_post_api(aie_node_api+'?requestType=getAccountProperties', {'recipient':aie_account, 'property':"MyArtiqox Dashboard Wallet"})
        try:
            dashboardwallets = json_aieresponse["properties"][0]["value"]
        except Exception as e:
            dashboardwallets = ""
        dashboardwallets_list = dashboardwallets.split(",")
        for mywallet in dashboardwallets_list:
            splits = mywallet.split(":")
            wallet_details = get_wallet_details(splits[0],splits[1])
            if wallet_details:
                dashboardwallets_dict[splits[1]] = wallet_details
                if market_data_dict.get(splits[0],"NA") == "NA":
                    vs_currency = "btc"
                    if splits[0] == "bitcoin":
                        vs_currency = "usd"
                    
                    market_data = get_coingecko_market_chart(splits[0],vs_currency,7)
                    if market_data:
                        market_data_dict.setdefault(splits[0],{})["market_data"] = market_data
                    top_accounts = get_top_accounts(splits[0],999)
                    if top_accounts:
                        for coin, data in top_accounts.items():
                            market_data_dict.setdefault(splits[0],{}).setdefault("top_accounts",{}).setdefault(coin,{})["accounts"] = list(reversed(data))
                            market_data_dict.setdefault(splits[0],{}).setdefault("top_accounts",{}).setdefault(coin,{})["club10"] = list(reversed(data[-10:]))
                            market_data_dict.setdefault(splits[0],{}).setdefault("top_accounts",{}).setdefault(coin,{})["club100"] = list(reversed(data[-100:]))
                            market_data_dict.setdefault(splits[0],{}).setdefault("top_accounts",{}).setdefault(coin,{})["club1000"] = list(reversed(data[-1000:]))
        #aiq_balance=get_account_balance("aiq",aie_account)
        #aie_balance=get_account_balance("aie",aie_account)
        return render_template( 'pages/charts.html', dashboardwallets_dict = dashboardwallets_dict, linecharts_dict=market_data_dict, barcharts_dict=market_data_dict )

    except Exception as e:
        print (e.message, e.args)
        return render_template('layouts/auth-default.html',
                                content=render_template( 'pages/404.html' ) )
