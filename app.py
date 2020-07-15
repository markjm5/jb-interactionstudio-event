import os
import traceback
import json
import jwt
import requests
import xml.etree.ElementTree as ET
from datetime import datetime as dt
from os import environ
from flask import Flask, render_template, request, send_from_directory, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy

from urllib.request import urlopen
app = Flask(__name__, static_folder="static")

is_prod = os.environ.get('IS_PRODUCTION', None)

if is_prod:

    JWT_SIGNING_SECRET = os.environ.get('JWT_SIGNING_SECRET')
    CLIENT_ID = os.environ.get('CLIENT_ID')
    CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
    MC_AUTH_ENDPOINT = os.environ.get('MC_AUTH_ENDPOINT')    
    MC_HOST_ENDPOINT = os.environ.get('MC_HOST_ENDPOINT')    
    MC_SOAP_ENDPOINT = os.environ.get('MC_SOAP_ENDPOINT')   
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
    CLIENT_ID = Config.CLIENT_ID
    CLIENT_SECRET = Config.CLIENT_SECRET
    MC_AUTH_ENDPOINT = Config.MC_AUTH_ENDPOINT
    MC_HOST_ENDPOINT = Config.MC_HOST_ENDPOINT
    MC_SOAP_ENDPOINT = Config.MC_SOAP_ENDPOINT
    IS_ENDPOINT = Config.IS_ENDPOINT
    LOG_NOTIFICATION_URL = Config.LOG_NOTIFICATION_URL 
    app.debug = DEBUG
    APPLICATION_DOMAIN = Config.APPLICATION_DOMAIN
    EXECUTE_METHOD = "GET"

auth_header_json_data = { "grant_type": "client_credentials",
    "client_id" : CLIENT_ID,
    "client_secret" : CLIENT_SECRET
}

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))

#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#db = SQLAlchemy(app)

@app.route('/index.html', methods=['GET'])
def index_html():
    path_to_static = os.path.join(request.url_root, "static/")

    data = {'title': 'Python request', 'body': 'this is a GET request to index.html', 'data': request.data}

    notification1_response = requests.post(LOG_NOTIFICATION_URL, data)

    return render_template('index.html', static_path=path_to_static)


@app.route('/journeybuilder/execute/', methods=['POST', 'GET'])
def journeybuilder_execute():
    # Article for execute method not firing: https://salesforce.stackexchange.com/questions/51912/trouble-getting-journeybuilder-to-call-execute-url-on-custom-activity-platform
    # https://salesforce.stackexchange.com/questions/186332/one-to-many-data-binding-journey-custom-activity/186338
    # https://salesforce.stackexchange.com/questions/269769/sfmc-custom-activity-error-a-custom-activity-or-entry-source-failed-validation
    # https://salesforce.stackexchange.com/questions/185511/journey-builder-custom-activity-not-a-valid-argument?rq=1
    # https://salesforce.stackexchange.com/questions/185792/accessing-entry-event-data-journey-builder-custom-activity
    # https://salesforce.stackexchange.com/questions/283981/sfmc-journey-builder-custom-activity
    
    decrypted_token = ""
    
    if request.method == EXECUTE_METHOD:
        response = requests.post(LOG_NOTIFICATION_URL, "YAY!!!")
        try:
            decrypted_token = jwt.decode(request.data,JWT_SIGNING_SECRET, algorithms=['HS256'])
        except jwt.DecodeError as e:
            decrypted_token = {}

        #Debugging Logger
        data = {'title': 'Python request', 'body': 'This is a POST request to the Execute Command', 'decrypted token': json.dumps(decrypted_token), 'data': request.data}
        debug_logger(data)

        #decrypted_token = {"inArguments": [{"tokens": {"token": "0bICaQjRzb5eVIj1GdBUzh_e1OWp767KIb643uRgzAOuIhTpUQ9CohE2EByfDn_Zp7XJProiIl_CpHkO2kyTAf0ByXcY_OALoruBMe_oS_q_4gY9gK9n4nUtTgHmJGj406EVJt_ls5PBhhgLoE0Ey6gi5CW8DBrlgxt4j54oiW80ksznA6Yw1jW9Eei-zc3tOLWpChwAKDa2wTIzIV4-MQ8e0fgI06am2WbbLWrYT_x---ZhXKeD7rrUi1F2jhKwwB3RKLq62nt-etXF_U95A4w", "fuel2token": "4ik9NTfcH9PLnzARSuMvkWcG", "expires": 1594739767789, "stackKey": "S4"}, "contactIdentifier": "51", "unique_id_field": "EventID", "emailAddress": "mmukherjee@salesforce.com", "customer_key": "87BDC216-17C5-4827-8BD0-49FCE274BBCA", "is_template": "GenericUserEvent", "is_event_mappings": {"user_id": "UserID", "action": "Action", "source": "AdvisorName", "event_date": "EventDate"}}], "outArguments": [{"SegmentMembership": ""}], "activityObjectID": "e27bc19a-6265-4c14-9088-82981e5d59c5", "journeyId": "13624365-43b2-4998-a414-4ffbfb828db6", "activityId": "e27bc19a-6265-4c14-9088-82981e5d59c5", "definitionInstanceId": "65f09729-9bdb-45d5-8038-c5a8de875ff1", "activityInstanceId": "a85c9fb1-c38d-46bd-a76a-8a8052947028", "keyValue": "51", "mode": 0}

        #Retrieve important fields from request object
        emailAddress = decrypted_token['inArguments'][0]['emailAddress']
        contactIdentifier = decrypted_token['inArguments'][0]['contactIdentifier']
        entry_de_customer_key = decrypted_token['inArguments'][0]['customer_key']
        unique_id = decrypted_token['inArguments'][0]['unique_id_field']
        is_event_mappings = decrypted_token['inArguments'][0]['is_event_mappings']
        is_template = decrypted_token['inArguments'][0]['is_template']
        #action = "Filed A Case"

        #Get access token
        response = requests.post(MC_AUTH_ENDPOINT, auth_header_json_data)
        response_content = json.loads(response._content)
        access_token = json.loads(response._content)["access_token"]

        #Process here the decrypted data, and match it to evergage event api fields
        entry_de_name = retrieve_de_name(entry_de_customer_key, access_token)

        entry_de_fields = de_customer_key_to_fields(entry_de_customer_key, access_token)

        fields_values = retrieve_de_fields_values(entry_de_customer_key, entry_de_name, unique_id, entry_de_fields, contactIdentifier, access_token)

        #action = "Filed a Case"
        #user_id = fields_values['UserID']

        if is_template == "GenericUserEvent":
            # Retrieve the Data Extension Object Json
            with open(os.path.join(SITE_ROOT, "static/templates/", "template_IS_event.json")) as json_file:
                retrieve_json = json.load(json_file)

            #assign the actual value of each field to the vars that will be used to make the call to Interaction Studio
            user_id = get_event_value(is_event_mappings['user_id'], fields_values)
            action = get_event_value(is_event_mappings['action'], fields_values)
            event_source = get_event_value(is_event_mappings['source'], fields_values)
            event_date = get_event_value(is_event_mappings['event_date'], fields_values)

            #if an event date was assigned, use it for the event date in IS, otherwise use todays date
            if event_date == "":
                current_date = dt.today().strftime("%m-%d-%Y")
                current_date_millis = helper_unix_time_millis(current_date)
            else:
                my_dt = dt.strptime(event_date, '%m/%d/%Y %H:%M:%S %p')
                current_date_millis = helper_unix_time_millis(my_dt)

            # if Event Source or Action is empty, set them to a value
            if event_source == "":
                event_source = "Journey Builder"

            if action == "":
                action = "Journey Builder Action"

            #fields_values1 = {'UserName': 'Test','EmailAddress':'mmukherjee@salesforce.com', 'FirstName': 'Mark', 'LocalBranch': '', 'LastName': 'Mukherjee', 'EventDate': '6/14/2020 12:00:00 AM', 'SegmentMembership': '', 'Gender': 'M', 'Action': 'Email Sent', 'AdvisorName': 'Journey Builder Event', 'EventID': '51', 'EmailAddress': 'mmukherjee@salesforce.com', 'UserID': '1000000051'}

            ## Using the evergage example json, match field names from field_values to evergage fields. If we can find a match, assign the values.
            ## In doing so, dynamically create dict1
            dict1 = { 'action': action ,'user': {'id': user_id, 'attributes': fields_values}, 'source': {'channel': event_source, 'time': current_date_millis}}
            retrieve_json.update(dict1)

            #Debugging Logger
            data = {'title': 'Python request', 'body': 'This is a POST request to Interaction Studio', 'data': retrieve_json}
            debug_logger(data)

            #make an api call to evergage
            response = requests.post(IS_ENDPOINT, json=retrieve_json)

            #send the returned Next Best Action back to journey builder
            campaign_response = json.loads(response._content)['campaignResponses']

    jsonified_test = {"SegmentMembership": "this is a test"}    

    return jsonify(jsonified_test)


@app.route('/journeybuilder/save/', methods=['POST'])
def journeybuilder_save():
    decrypted_token = ""

    if request.method == 'POST':

        try:
            decrypted_token = jwt.decode(request.data,JWT_SIGNING_SECRET, algorithms=['HS256'])
        except jwt.DecodeError as e:
            decrypted_token = {}

        data = {'title': 'Python request', 'body': 'This is a POST request to the Save Command', 'decrypted token': json.dumps(decrypted_token), 'data': request.data}


    response = requests.post(LOG_NOTIFICATION_URL, data)

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

        data = {'title': 'Python request', 'body': 'This is a POST request to the Publish Command', 'decrypted token': json.dumps(decrypted_token), 'data': request.data}

    response = requests.post(LOG_NOTIFICATION_URL, data)

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

        data = {'title': 'Python request', 'body': 'This is a POST request to the Stop Command', 'decrypted token': json.dumps(decrypted_token), 'data': request.data}

    response = requests.post(LOG_NOTIFICATION_URL, data)

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

        data = {'title': 'Python request', 'body': 'This is a POST request to the Validate Command', 'decrypted token': json.dumps(decrypted_token), 'data': request.data}

    response = requests.post(LOG_NOTIFICATION_URL, data)

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

@app.route('/journeybuilder/getdefields/', methods=['POST'])
def journeybuilder_get_de_fields():

    jsonified_text = {}

    if request.method == 'POST':
        de_customer_key = request.form["DECustomerKey"]

        response = requests.post(MC_AUTH_ENDPOINT, auth_header_json_data)
        response_content = json.loads(response._content)
        access_token = json.loads(response._content)["access_token"]

        #response = requests.post(LOG_NOTIFICATION_URL, de_customer_key)
        try:
            de_name = retrieve_de_name(de_customer_key, access_token)
            de_fields = de_customer_key_to_fields(de_customer_key, access_token)

            jsonified_text = {"error": "False","de_name": de_name, "de_fields": de_fields}  
        except:
            jsonified_text = {"error": "True"}

        data = {'title': 'Python request', 'body': 'This is a POST request to Get DE Fields'}

        response = requests.post(LOG_NOTIFICATION_URL, data)
    
    return jsonify(jsonified_text)


def debug_logger(data):

    #Debugging Logger
    response = requests.post(LOG_NOTIFICATION_URL, data)

    return response



def to_pretty_json(value):
    return json.dumps(value, sort_keys=True,
                      indent=4, separators=(',', ': '))

app.jinja_env.filters['tojson_pretty'] = to_pretty_json


def journey_id_to_event_key(journey_id, access_token):

    #Get authentication token
    #response = requests.post(MC_AUTH_ENDPOINT, auth_header_json_data)
    #access_token = json.loads(response._content)["access_token"]
    
    #To make post request, we need to wet the auth header
    authorization_headers = {'Content-Type': 'application/json', 'Authorization':  'Bearer ' + access_token}

    response = requests.get(MC_HOST_ENDPOINT + 'interactions/' + journey_id, headers=authorization_headers)
    account_journey_json_payload = json.loads(response._content)

    event_definition_key = account_journey_json_payload['triggers'][0]['metaData']['eventDefinitionKey']

    return event_definition_key


def event_key_to_de_customer_key(event_definition_key, access_token):

    #Get authentication token
    #response = requests.post(MC_AUTH_ENDPOINT, auth_header_json_data)
    #access_token = json.loads(response._content)["access_token"
    #To make post request, we need to wet the auth header
    authorization_headers = {'Content-Type': 'application/json', 'Authorization':  'Bearer ' + access_token}

    response = requests.get(MC_HOST_ENDPOINT + 'eventDefinitions/key:' + event_definition_key, headers=authorization_headers)
    event_definition_json_payload = json.loads(response._content)

    entry_de_id = event_definition_json_payload['dataExtensionId']

    customer_key = retrieve_de_customer_key(entry_de_id, access_token)

    return customer_key

def retrieve_de_customer_key(entry_de_id, access_token):

    # Retrieve the Data Extension Object ID
    retrieve_de_object_xml = os.path.join(SITE_ROOT, "static/templates/", "template_retrieveDEObject.xml")

    #tree = return_formatted_xml_tree(retrieve_de_object_xml, event_definition_key, access_token)
    #import pdb; pdb.set_trace()
    
    tree = ET.parse(retrieve_de_object_xml)
    to_element = tree.findall("./{http://www.w3.org/2003/05/soap-envelope}Header/{http://schemas.xmlsoap.org/ws/2004/08/addressing}To")[0]
    fueloauth_element = tree.findall("./{http://www.w3.org/2003/05/soap-envelope}Header/{http://exacttarget.com}fueloauth")[0]
    value_element = tree.findall("./{http://www.w3.org/2003/05/soap-envelope}Body/{http://exacttarget.com/wsdl/partnerAPI}RetrieveRequestMsg/{http://exacttarget.com/wsdl/partnerAPI}RetrieveRequest/{http://exacttarget.com/wsdl/partnerAPI}Filter/{http://exacttarget.com/wsdl/partnerAPI}Value")[0]
    body_element = tree.findall("./{http://www.w3.org/2003/05/soap-envelope}Body")[0]
    retrieverequestmsg_element = tree.findall("./{http://www.w3.org/2003/05/soap-envelope}Body/{http://exacttarget.com/wsdl/partnerAPI}RetrieveRequestMsg")[0]

    to_element.text = MC_SOAP_ENDPOINT
    fueloauth_element.text = access_token
    value_element.text = entry_de_id

    body_element.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    body_element.set("xmlns:xsd", "http://www.w3.org/2001/XMLSchema")
    retrieverequestmsg_element.set("xmlns","http://exacttarget.com/wsdl/partnerAPI")

    ET.register_namespace("s","http://www.w3.org/2003/05/soap-envelope")
    ET.register_namespace("a","http://schemas.xmlsoap.org/ws/2004/08/addressing")
    ET.register_namespace("u","http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd")
    
    headers = {'Content-Type': 'text/xml'} # set what your server accepts
    #response = requests.post(MC_SOAP_ENDPOINT, data=ET.tostring(tree.getroot()), headers=headers).text

    tree1 = ET.fromstring(requests.post(MC_SOAP_ENDPOINT, data=ET.tostring(tree.getroot()), headers=headers).text)
    customer_key = tree1.findall("./{http://www.w3.org/2003/05/soap-envelope}Body/{http://exacttarget.com/wsdl/partnerAPI}RetrieveResponseMsg/{http://exacttarget.com/wsdl/partnerAPI}Results/{http://exacttarget.com/wsdl/partnerAPI}CustomerKey")[0].text

    return customer_key


def retrieve_de_name(de_customer_key, access_token):

    # Retrieve the Data Extension Object ID
    retrieve_de_object_xml = os.path.join(SITE_ROOT, "static/templates/", "template_retrieveDEObject.xml")

    #tree = return_formatted_xml_tree(retrieve_de_object_xml, event_definition_key, access_token)
    #import pdb; pdb.set_trace()
    
    tree = ET.parse(retrieve_de_object_xml)
    to_element = tree.findall("./{http://www.w3.org/2003/05/soap-envelope}Header/{http://schemas.xmlsoap.org/ws/2004/08/addressing}To")[0]
    fueloauth_element = tree.findall("./{http://www.w3.org/2003/05/soap-envelope}Header/{http://exacttarget.com}fueloauth")[0]
    value_element = tree.findall("./{http://www.w3.org/2003/05/soap-envelope}Body/{http://exacttarget.com/wsdl/partnerAPI}RetrieveRequestMsg/{http://exacttarget.com/wsdl/partnerAPI}RetrieveRequest/{http://exacttarget.com/wsdl/partnerAPI}Filter/{http://exacttarget.com/wsdl/partnerAPI}Value")[0]
    property_element = tree.findall("./{http://www.w3.org/2003/05/soap-envelope}Body/{http://exacttarget.com/wsdl/partnerAPI}RetrieveRequestMsg/{http://exacttarget.com/wsdl/partnerAPI}RetrieveRequest/{http://exacttarget.com/wsdl/partnerAPI}Filter/{http://exacttarget.com/wsdl/partnerAPI}Property")[0]
    body_element = tree.findall("./{http://www.w3.org/2003/05/soap-envelope}Body")[0]
    retrieverequestmsg_element = tree.findall("./{http://www.w3.org/2003/05/soap-envelope}Body/{http://exacttarget.com/wsdl/partnerAPI}RetrieveRequestMsg")[0]

    to_element.text = MC_SOAP_ENDPOINT
    fueloauth_element.text = access_token
    property_element.text = "CustomerKey"
    value_element.text = de_customer_key

    body_element.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    body_element.set("xmlns:xsd", "http://www.w3.org/2001/XMLSchema")
    retrieverequestmsg_element.set("xmlns","http://exacttarget.com/wsdl/partnerAPI")

    ET.register_namespace("s","http://www.w3.org/2003/05/soap-envelope")
    ET.register_namespace("a","http://schemas.xmlsoap.org/ws/2004/08/addressing")
    ET.register_namespace("u","http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd")
    
    headers = {'Content-Type': 'text/xml'} # set what your server accepts

    tree1 = ET.fromstring(requests.post(MC_SOAP_ENDPOINT, data=ET.tostring(tree.getroot()), headers=headers).text)
    de_name = tree1.findall("./{http://www.w3.org/2003/05/soap-envelope}Body/{http://exacttarget.com/wsdl/partnerAPI}RetrieveResponseMsg/{http://exacttarget.com/wsdl/partnerAPI}Results/{http://exacttarget.com/wsdl/partnerAPI}Name")[0].text

    return de_name


def de_customer_key_to_fields(de_customer_key, access_token):

    #Get authentication token
    #response = requests.post(MC_AUTH_ENDPOINT, auth_header_json_data)
    #access_token = json.loads(response._content)["access_token"]
    
    #To make post request, we need to wet the auth header
    authorization_headers = {'Content-Type': 'application/json', 'Authorization':  'Bearer ' + access_token}

    # Retrieve the Data Extension Object ID
    retrieve_de_fields_xml = os.path.join(SITE_ROOT, "static/templates/", "template_retrieveDEFields.xml")

    #tree = return_formatted_xml_tree(retrieve_de_fields_xml, de_customer_key, access_token)
    
    tree = ET.parse(retrieve_de_fields_xml)
    to_element = tree.findall("./{http://www.w3.org/2003/05/soap-envelope}Header/{http://schemas.xmlsoap.org/ws/2004/08/addressing}To")[0]
    fueloauth_element = tree.findall("./{http://www.w3.org/2003/05/soap-envelope}Header/{http://exacttarget.com}fueloauth")[0]
    value_element = tree.findall("./{http://www.w3.org/2003/05/soap-envelope}Body/{http://exacttarget.com/wsdl/partnerAPI}RetrieveRequestMsg/{http://exacttarget.com/wsdl/partnerAPI}RetrieveRequest/{http://exacttarget.com/wsdl/partnerAPI}Filter/{http://exacttarget.com/wsdl/partnerAPI}Value")[0]
    body_element = tree.findall("./{http://www.w3.org/2003/05/soap-envelope}Body")[0]
    retrieverequestmsg_element = tree.findall("./{http://www.w3.org/2003/05/soap-envelope}Body/{http://exacttarget.com/wsdl/partnerAPI}RetrieveRequestMsg")[0]

    to_element.text = MC_SOAP_ENDPOINT
    fueloauth_element.text = access_token
    value_element.text = de_customer_key

    body_element.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    body_element.set("xmlns:xsd", "http://www.w3.org/2001/XMLSchema")
    retrieverequestmsg_element.set("xmlns","http://exacttarget.com/wsdl/partnerAPI")

    ET.register_namespace("s","http://www.w3.org/2003/05/soap-envelope")
    ET.register_namespace("a","http://schemas.xmlsoap.org/ws/2004/08/addressing")
    ET.register_namespace("u","http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd")
    

    headers = {'Content-Type': 'text/xml'} # set what your server accepts
    #response = requests.post(MC_SOAP_ENDPOINT, data=ET.tostring(tree.getroot()), headers=headers).text
    tree1 = ET.fromstring(requests.post(MC_SOAP_ENDPOINT, data=ET.tostring(tree.getroot()), headers=headers).text)

    results_elements = tree1.findall('.//{http://exacttarget.com/wsdl/partnerAPI}Results')

    fields = []

    for field_name in results_elements:
        field = {}

        try:
            field["Name"] = field_name.find("./{http://exacttarget.com/wsdl/partnerAPI}Name").text
        except AttributeError as err:
            pass

        try:
            field["MaxLength"] = field_name.find("./{http://exacttarget.com/wsdl/partnerAPI}MaxLength").text
        except AttributeError as err:
            pass

        try:
            field["IsRequired"] = field_name.find("./{http://exacttarget.com/wsdl/partnerAPI}IsRequired").text
        except AttributeError as err:
            pass

        try:
            field["Ordinal"] = field_name.find("./{http://exacttarget.com/wsdl/partnerAPI}Ordinal").text
        except AttributeError as err:
            pass

        try:
            field["IsPrimaryKey"] = field_name.find("./{http://exacttarget.com/wsdl/partnerAPI}IsPrimaryKey").text
        except AttributeError as err:
            pass

        try:
            field["FieldType"] = field_name.find("./{http://exacttarget.com/wsdl/partnerAPI}FieldType").text
        except AttributeError as err:
            pass

        fields.append(field)

    return fields


def retrieve_de_fields_values(de_customer_key, de_name, unique_id, de_fields, contactIdentifier, access_token):

    #Get authentication token
    #response = requests.post(MC_AUTH_ENDPOINT, auth_header_json_data)
    #access_token = json.loads(response._content)["access_token"]
    
    #To make post request, we need to wet the auth header
    authorization_headers = {'Content-Type': 'application/json', 'Authorization':  'Bearer ' + access_token}

    # Retrieve the Data Extension Object ID
    retrieve_de_fields_xml = os.path.join(SITE_ROOT, "static/templates/", "template_retrieveDERow.xml")

    tree = ET.parse(retrieve_de_fields_xml)

    to_element = tree.findall("./{http://www.w3.org/2003/05/soap-envelope}Header/{http://schemas.xmlsoap.org/ws/2004/08/addressing}To")[0]
    fueloauth_element = tree.findall("./{http://www.w3.org/2003/05/soap-envelope}Header/{http://exacttarget.com}fueloauth")[0]
    value_element = tree.findall("./{http://www.w3.org/2003/05/soap-envelope}Body/{http://exacttarget.com/wsdl/partnerAPI}RetrieveRequestMsg/{http://exacttarget.com/wsdl/partnerAPI}RetrieveRequest/{http://exacttarget.com/wsdl/partnerAPI}Filter/{http://exacttarget.com/wsdl/partnerAPI}Value")[0]
    property_element = tree.findall("./{http://www.w3.org/2003/05/soap-envelope}Body/{http://exacttarget.com/wsdl/partnerAPI}RetrieveRequestMsg/{http://exacttarget.com/wsdl/partnerAPI}RetrieveRequest/{http://exacttarget.com/wsdl/partnerAPI}Filter/{http://exacttarget.com/wsdl/partnerAPI}Property")[0]
    retrieverequest_element = tree.findall("./{http://www.w3.org/2003/05/soap-envelope}Body/{http://exacttarget.com/wsdl/partnerAPI}RetrieveRequestMsg/{http://exacttarget.com/wsdl/partnerAPI}RetrieveRequest")[0]
    objecttype_element = tree.findall("./{http://www.w3.org/2003/05/soap-envelope}Body/{http://exacttarget.com/wsdl/partnerAPI}RetrieveRequestMsg/{http://exacttarget.com/wsdl/partnerAPI}RetrieveRequest/{http://exacttarget.com/wsdl/partnerAPI}ObjectType")[0]
    body_element = tree.findall("./{http://www.w3.org/2003/05/soap-envelope}Body")[0]
    retrieverequestmsg_element = tree.findall("./{http://www.w3.org/2003/05/soap-envelope}Body/{http://exacttarget.com/wsdl/partnerAPI}RetrieveRequestMsg")[0]
    
    to_element.text = MC_SOAP_ENDPOINT
    fueloauth_element.text = access_token
    value_element.text = contactIdentifier
    objecttype_element.text = "DataExtensionObject[%s]" % de_name

    property_element.text = unique_id

    for key in de_fields:
        #if key["FieldType"] == "EmailAddress":
        #    property_element.text = key["Name"]

        c = ET.Element("Properties")
        c.text = key["Name"]
        retrieverequest_element.insert(1,c)

    body_element.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    body_element.set("xmlns:xsd", "http://www.w3.org/2001/XMLSchema")
    retrieverequestmsg_element.set("xmlns","http://exacttarget.com/wsdl/partnerAPI")

    ET.register_namespace("s","http://www.w3.org/2003/05/soap-envelope")
    ET.register_namespace("a","http://schemas.xmlsoap.org/ws/2004/08/addressing")
    ET.register_namespace("u","http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd")
    
    #import pdb; pdb.set_trace()

    headers = {'Content-Type': 'text/xml'} # set what your server accepts

    tree1 = ET.fromstring(requests.post(MC_SOAP_ENDPOINT, data=ET.tostring(tree.getroot()), headers=headers).text)
    
    tree1_properties_element = tree1.findall("./{http://www.w3.org/2003/05/soap-envelope}Body/{http://exacttarget.com/wsdl/partnerAPI}RetrieveResponseMsg/{http://exacttarget.com/wsdl/partnerAPI}Results/{http://exacttarget.com/wsdl/partnerAPI}Properties")[0]

    field_values = {}

    for child in tree1_properties_element:

        attr_name = child[0].text
        attr_value = child[1].text

        field_values[attr_name] = helper_xstr(attr_value)

    return field_values

def helper_unix_time_millis(dt):
    epoch = dt.utcfromtimestamp(0)
    return (dt - epoch).total_seconds() * 1000.0

def helper_xstr(s):
    if s is None:
        return ''
    return str(s)    

def return_formatted_xml_tree(tree, value, access_token):
    #Currently not being used

    to_element = tree.findall("./{http://www.w3.org/2003/05/soap-envelope}Header/{http://schemas.xmlsoap.org/ws/2004/08/addressing}To")[0]
    fueloauth_element = tree.findall("./{http://www.w3.org/2003/05/soap-envelope}Header/{http://exacttarget.com}fueloauth")[0]
    value_element = tree.findall("./{http://www.w3.org/2003/05/soap-envelope}Body/{http://exacttarget.com/wsdl/partnerAPI}RetrieveRequestMsg/{http://exacttarget.com/wsdl/partnerAPI}RetrieveRequest/{http://exacttarget.com/wsdl/partnerAPI}Filter/{http://exacttarget.com/wsdl/partnerAPI}Value")[0]
    body_element = tree.findall("./{http://www.w3.org/2003/05/soap-envelope}Body")[0]
    retrieverequestmsg_element = tree.findall("./{http://www.w3.org/2003/05/soap-envelope}Body/{http://exacttarget.com/wsdl/partnerAPI}RetrieveRequestMsg")[0]

    to_element.text = MC_SOAP_ENDPOINT
    fueloauth_element.text = access_token
    value_element.text = value

    body_element.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    body_element.set("xmlns:xsd", "http://www.w3.org/2001/XMLSchema")
    retrieverequestmsg_element.set("xmlns","http://exacttarget.com/wsdl/partnerAPI")

    ET.register_namespace("s","http://www.w3.org/2003/05/soap-envelope")
    ET.register_namespace("a","http://schemas.xmlsoap.org/ws/2004/08/addressing")
    ET.register_namespace("u","http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd")

    return formatted_xml_tree


def get_event_value(event_field, list_of_values):

    try:
        value = list_of_values[event_field]
    except KeyError:
        value = ""

    return value



if __name__ == '__main__':
    app.run()