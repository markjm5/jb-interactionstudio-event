import os
import sys
import traceback
import json
import jwt
import requests
import re
import xml.etree.ElementTree as ET
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime as dt
from os import environ
from flask import Flask, render_template, request, send_from_directory, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy

from urllib.request import urlopen
app = Flask(__name__, static_folder="static")

is_prod = os.environ.get('IS_PRODUCTION', None)

if is_prod:

    JWT_SIGNING_SECRET = os.environ.get('JWT_SIGNING_SECRET')
    IS_ENDPOINT = os.environ.get('IS_ENDPOINT')
    app.debug = False
    LOG_NOTIFICATION_URL = os.environ.get('LOG_NOTIFICATION_URL')
    APPLICATION_DOMAIN = os.environ.get('APPLICATION_DOMAIN')
    EXECUTE_METHOD = "POST"
else:
    from config_dev import Config
    app.config.from_object(Config)

    DEBUG = Config.DEBUG
    JWT_SIGNING_SECRET = Config.JWT_SIGNING_SECRET
    IS_ENDPOINT = Config.IS_ENDPOINT
    LOG_NOTIFICATION_URL = Config.LOG_NOTIFICATION_URL 
    app.debug = DEBUG
    APPLICATION_DOMAIN = Config.APPLICATION_DOMAIN
    EXECUTE_METHOD = "GET"

#auth_header_json_data = { "grant_type": "client_credentials",
#    "client_id" : CLIENT_ID,
#    "client_secret" : CLIENT_SECRET
#}

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))

#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#db = SQLAlchemy(app)

@app.route('/index.html', methods=['GET'])
def index_html():
    path_to_static = os.path.join(request.url_root, "static/")

    #Debugging Logger
    data = {'title': 'inArguments Request', 'body': 'this is a GET request to index.html', 'data': request.data}
    debug_logger(data)

    return render_template('index.html', static_path=path_to_static)


@app.route('/journeybuilder/execute/', methods=['POST', 'GET'])
def journeybuilder_execute():
    
    decrypted_token = ""
    
    if request.method == EXECUTE_METHOD:

        try:
            decrypted_token = jwt.decode(request.data,JWT_SIGNING_SECRET, algorithms=['HS256'])
        except jwt.DecodeError as e:
            decrypted_token = {}

        #Debugging Logger
        data = {'title': 'inArguments Request', 'body': 'This is a POST request to the Execute Command', 'decrypted token': json.dumps(decrypted_token)}
        debug_logger(data)

        if not is_prod:
            decrypted_token = {"inArguments": [{"tokens": {"token": "0bICaQjRzb5eVIj1GdBUzh0VhzAiY_0r2RGv3Ok4g3X2JMrrYaJLwfyR6T5e4BUDhDV5pdIs8PpB19dUOrDy93merVjgL8HJpz6BS58opkgJz6WKyVyDNPDM2cxzO04GYqxTKMVD3yC42q86V1W0iluviKdq4jveXQ1l5ebYWkZzkwtDBer0QKceS4I1QE8KjQgW43JJqXWc8ZkhAjqlfjbHTFE_wvg94SpQmwYnGk5emafrKXdIp_6AwRrsAbmwSCv3J8WHLtOtN3htuOVwJ5Q", "fuel2token": "4jzRKZK7erA0xBv6QaN3SaHm", "expires": 1595342819521, "stackKey": "S4"}, "contactIdentifier": "rmorris.10000.0000@gmail.exacttargettest.com", "emailAddress": "rmorris.10000.0000@gmail.exacttargettest.com", "is_template": "ProductPurchase", "is_event_mappings": {"user_id": "UserID", "action": "Action", "source": "", "event_date": "EventDate", "order_id": "OrderID", "currency": "Currency", "line_items": "LineItems"}, "de_field_mappings": {"EmailAddress": "rmorris.10000.0000@gmail.exacttargettest.com", "FirstName": "Rachel", "LastName": "Morris2", "Gender": "M", "UserID": "100000003", "SegmentMembership": "", "loyaltypoints": "", "loyaltytier": "", "Action": "Purchase", "EventDate": "7/4/2020 12:00:00 AM", "EventID": "11", "OrderID": "100031", "Currency": "USD", "LineItems": "[{_id: MarkTest,price: 90.00,quantity: 1}]"}}], "outArguments": [{"SegmentMembership": ""}], "activityObjectID": "e869451f-60a0-401c-a065-196e241190d0", "journeyId": "feca1ca9-e848-4a1a-90b4-a4bcd1c0b391", "activityId": "e869451f-60a0-401c-a065-196e241190d0", "definitionInstanceId": "a66b2125-0c11-4180-ad83-2db789125e7d", "activityInstanceId": "20015f46-d17a-437a-92d3-139029e9ba55", "keyValue": "rmorris.10000.0000@gmail.exacttargettest.com", "mode": 0}

        #Retrieve important fields from request object
        emailAddress = decrypted_token['inArguments'][0]['emailAddress']
        contactIdentifier = decrypted_token['inArguments'][0]['contactIdentifier']

        is_event_mappings = decrypted_token['inArguments'][0]['is_event_mappings']

        fields_values = decrypted_token['inArguments'][0]['de_field_mappings']

        is_template = decrypted_token['inArguments'][0]['is_template']
        
        # Retrieve the Data Extension Object Json
        with open(os.path.join(SITE_ROOT, "static/templates/", "template_IS_event.json")) as json_file:
            retrieve_json = json.load(json_file)

        #assign the actual value of each field to the vars that will be used to make the call to Interaction Studio
        user_id = get_event_value(is_event_mappings['user_id'], fields_values)
        event_source = get_event_value(is_event_mappings['source'], fields_values)
        event_date = get_event_value(is_event_mappings['event_date'], fields_values)

        #if an event date was assigned, use it for the event date in IS, otherwise use todays date
        if not event_date.strip():

            current_date = dt.today().strftime("%m-%d-%Y")
            my_dt = dt.strptime(current_date, '%m-%d-%Y')

            current_date_millis = helper_unix_time_millis(my_dt)
        else:
            my_dt = dt.strptime(event_date, '%m/%d/%Y %H:%M:%S %p')
            current_date_millis = helper_unix_time_millis(my_dt)

        # if Event Source or Action is empty, set them to a value
        if not event_source.strip():
            event_source = "Journey Builder"

        ## Using the evergage example json, match field names from field_values to evergage fields. If we can find a match, assign the values.
        ## In doing so, dynamically create dict1
        dict1 = {}

        if is_template == 'GenericUserEvent':
            action = get_event_value(is_event_mappings['action'], fields_values)
            first_name = get_event_value(is_event_mappings['first_name'], fields_values)
            last_name = get_event_value(is_event_mappings['last_name'], fields_values)
            userName = "%s %s" % (first_name, last_name)

            if userName.strip():
                fields_values["userName"] = userName

            if not action.strip():
                action = "Journey Builder Action"

            dict1 = { 'action': action ,'user': {'id': user_id, 'attributes': fields_values}, 'source': {'channel': event_source, 'time': current_date_millis}}

        if is_template == 'ProductView':
            action = get_event_value(is_event_mappings['action'], fields_values)
            source_url = get_event_value(is_event_mappings['source_url'], fields_values)
            page_type = get_event_value(is_event_mappings['page_type'], fields_values)

            product_id = get_event_value(is_event_mappings['product_id'], fields_values)
            product_name = get_event_value(is_event_mappings['product_name'], fields_values)
            product_url = get_event_value(is_event_mappings['product_url'], fields_values)
            product_imageUrl = get_event_value(is_event_mappings['product_imageUrl'], fields_values)
            product_description = get_event_value(is_event_mappings['product_description'], fields_values)
            product_price = get_event_value(is_event_mappings['product_price'], fields_values)
            product_currency = get_event_value(is_event_mappings['product_currency'], fields_values)
            product_inventoryCount = get_event_value(is_event_mappings['product_inventoryCount'], fields_values)

            #create the partial dictionaries
            source_dict = {'channel': event_source, 'time': current_date_millis}
            product_dict = {'_id': product_id}

            if source_url.strip():
                source_dict["url"] = source_url
                
            if page_type.strip():
                source_dict["pageType"] = page_type

            if product_name.strip():
                product_dict["name"] = product_name

            if product_url.strip():
                product_dict["url"] = product_url

            if product_imageUrl.strip():
                product_dict["imageUrl"] = product_imageUrl

            if product_description.strip():
                product_dict["description"] = product_description

            if product_price.strip():
                product_dict["price"] = product_price

            if product_currency.strip():
                product_dict["currency"] = product_currency

            if product_inventoryCount.strip():
                product_dict["inventoryCount"] = product_inventoryCount

            dict1 = { 'action': action ,'user': {'id': user_id}, 'itemAction': 'View Item','catalog': { 'Product': product_dict }, 'source': source_dict}


        if is_template == 'ProductPurchase':
            dict1 = { 'action': 'Purchase' ,'user': {'id': user_id}, 'source': {'channel': event_source, 'time': current_date_millis}}

            order_id = get_event_value(is_event_mappings['order_id'], fields_values)
            currency = get_event_value(is_event_mappings['currency'], fields_values)
            totalValue = 0
            line_items_arr = []
            dict2 = {}

            if order_id and currency:
                line_items = get_event_value(is_event_mappings['line_items'], fields_values)
                if line_items:
                    line_items = line_items.strip().replace(" ","")
                    line_items = line_items.strip(']').strip('[').split('},{')

                    for i in line_items:
                        line_item_val = i.strip('{').strip('}')
                        line_item_val = line_item_val.split(',')
                        line_item_dict = {}
                        for jj in line_item_val:
                            val = jj.split(':')
                            line_item_dict[val[0]] = val[1]
                            if val[0].lower() == 'price':
                                totalValue += float(val[1])         
                                line_item_dict[val[0]] = float(val[1])
                            elif val[0].lower() == 'quantity':
                                line_item_dict[val[0]] = int(val[1])
                            else:
                                line_item_dict[val[0]] = val[1]

                        line_items_arr.append(line_item_dict)

                    dict2 = {}
                    dict3 = {'orderId': order_id, 'totalValue': float(totalValue), 'currency': currency, 'lineItems': line_items_arr }
                    dict2["Product"] = dict3

            if dict2:
                dict1["order"] = dict2

        retrieve_json.update(dict1)

        #Debugging Logger
        data = {'title': 'Interaction Studio Request', 'body': 'This is a POST request to Interaction Studio', 'data': json.dumps(retrieve_json)}
        debug_logger(data)
        #import pdb; pdb.set_trace()
        #make an api call to evergage
        response = requests.post(IS_ENDPOINT, json=retrieve_json)

        campaign_response = []
        #send the returned Next Best Action back to journey builder
        if response.status_code == 200:
            try:
                campaign_response = json.loads(response._content)['campaignResponses']
            except TypeError:
                campaign_response = []
        else:
            data = {'title': 'ERROR', 'body': response.content}
            debug_logger(data)

    jsonified_test = {"SegmentMembership": campaign_response}    

    return jsonify(jsonified_test)


@app.route('/journeybuilder/save/', methods=['POST'])
def journeybuilder_save():
    decrypted_token = ""

    if request.method == 'POST':

        try:
            decrypted_token = jwt.decode(request.data,JWT_SIGNING_SECRET, algorithms=['HS256'])
        except jwt.DecodeError as e:
            decrypted_token = {}

        data = {'title': 'inArguments Request', 'body': 'This is a POST request to the Save Command', 'decrypted token': json.dumps(decrypted_token)}
        debug_logger(data)

    jsonified_test = { "SegmentMembership": "this is a test"}    
    return jsonify(jsonified_test)


@app.route('/journeybuilder/publish/', methods=['POST'])
def journeybuilder_publish():
    decrypted_token = ""

    if request.method == 'POST':

        try:
            decrypted_token = jwt.decode(request.data,JWT_SIGNING_SECRET, algorithms=['HS256'])
        except jwt.DecodeError as e:
            decrypted_token = {}

        data = {'title': 'inArguments Request', 'body': 'This is a POST request to the Publish Command', 'decrypted token': json.dumps(decrypted_token)}
        debug_logger(data)

    jsonified_test = { "SegmentMembership": "this is a test"}    
    return jsonify(jsonified_test)

@app.route('/journeybuilder/stop/', methods=['POST'])
def journeybuilder_stop():
    decrypted_token = ""

    if request.method == 'POST':

        try:
            decrypted_token = jwt.decode(request.data,JWT_SIGNING_SECRET, algorithms=['HS256'])
        except jwt.DecodeError as e:
            decrypted_token = {}

        data = {'title': 'inArguments Request', 'body': 'This is a POST request to the Stop Command', 'decrypted token': json.dumps(decrypted_token)}
        debug_logger(data)

    jsonified_test = { "SegmentMembership": "this is a test"}    
    return jsonify(jsonified_test)



@app.route('/journeybuilder/validate/', methods=['POST'])
def journeybuilder_validate():
    decrypted_token = ""

    if request.method == 'POST':

        try:
            decrypted_token = jwt.decode(request.data,JWT_SIGNING_SECRET, algorithms=['HS256'])
        except jwt.DecodeError as e:
            decrypted_token = {}

        data = {'title': 'inArguments Request', 'body': 'This is a POST request to the Validate Command', 'decrypted token': json.dumps(decrypted_token)}
        debug_logger(data)

    jsonified_test = { "SegmentMembership": "this is a test"}    
    return jsonify(jsonified_test)


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)

@app.route('/config.json', methods=['GET'])
def send_config_json():

    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))

    application_domain = APPLICATION_DOMAIN

    return render_template('showjson.jade', application_domain=application_domain)


@app.route('/static/salesforce-lightning-design-system-static-resource-2.11.9/icons/action/<path:path>')
def send_static(path):
    return send_from_directory('static/salesforce-lightning-design-system-static-resource-2.11.9/icons/action/', path)


################################################################################################################
#                                              Helper Functions                                                #
################################################################################################################


def debug_logger(data):

    #Check if a notification url was specified
    if LOG_NOTIFICATION_URL.strip():
        response = requests.post(LOG_NOTIFICATION_URL, data)
    else:
        return None

    logging_string = "INFO: %s %s\n\n" % (dt.now(), data)

    #Set logging properties
    sys.stderr.write(logging_string)

    return response

def to_pretty_json(value):
    return json.dumps(value, sort_keys=True,
                      indent=4, separators=(',', ': '))

app.jinja_env.filters['tojson_pretty'] = to_pretty_json


def helper_unix_time_millis(dt):
    epoch = dt.utcfromtimestamp(0)
    return (dt - epoch).total_seconds() * 1000.0

def helper_xstr(s):
    if s is None:
        return ''
    return str(s)    

def get_event_value(event_field, list_of_values):

    #import pdb; pdb.set_trace()

    try:
        value = list_of_values[event_field]
    except KeyError:
        value = ""

    return value


if __name__ == '__main__':
    app.run()
