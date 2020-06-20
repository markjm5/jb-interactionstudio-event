import os
import traceback
import json
import jwt
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from os import environ
from flask import Flask, render_template, request, send_from_directory, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy

from urllib.request import urlopen
app = Flask(__name__)

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

auth_header_json_data = { "grant_type": "client_credentials",
    "client_id" : CLIENT_ID,
    "client_secret" : CLIENT_SECRET
}

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))

#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#db = SQLAlchemy(app)

@app.route('/index.html', methods=['GET','POST'])
def index_html():
    path_to_css = os.path.join(request.url_root, "static/")

    if request.method == 'POST':
        data = {'title': 'Pyton request', 'body': 'This is the Execute Command POST'}
        debug_message = "this is a POST request to index.html"
    else:
        data = {'title': 'Pyton request', 'body': 'This is the Execute Command GET'}
        debug_message = "This is a test" #auth_header_json_data
    
    #journey_id = "87ebbd51-11c0-41c7-bd53-5dd16e93b712" 
    # event_definition_key = journey_id_to_event_key(journey_id)    
    # entry_de_customer_key = event_key_to_de_customer_key(event_definition_key)

    response = requests.post(MC_AUTH_ENDPOINT, auth_header_json_data)
    response_content = json.loads(response._content)

    #notification1_response = requests.post(LOG_NOTIFICATION_URL, response_content)

    access_token = json.loads(response._content)["access_token"]

    #entry_de_customer_key = "D5118761-5863-43DC-8022-941CE864DA83"
    #decrypted_token = "{\"inArguments\": [{\"tokens\": {\"token\": \"0bICaQjRzb5eVIj1GdBUzhwD4p91AuU60INp8kZUUlZ1rBLyNkAH7NqqdT4MRQkCWqBZDjJKYx7FAx_Waekwx4JyWHEHfU5saEdf01SARu-AijzK4Tyv_40MsOPQ1DdSp0pGg4tUWoNkGFhUMhKyZsyD-HWFFLXSRizG-La2sdNSlPoK2ce8RpTAKXgdkHNltS5HkxUVmBsfZvJBoLoRIBTqeMyECu6BqbbXNTbosJ77Pjhmij7fnP0jIj1O_DvEzlgTw3IfEZHd2C7RqKoukTg\", \"fuel2token\": \"4gOqoNhxXALlUcxZtK9S3j3U\", \"expires\": 1592483764291, \"stackKey\": \"S4\"}, \"emailAddress\": \"sgladden.10000.0003@hotmail.exacttargettest.com\", \"contactIdentifier\": \"sgladden.10000.0003@hotmail.exacttargettest.com\", \"message\": \"someMessage\"}], \"outArguments\": [{\"SegmentMembership\": \"\"}], \"activityObjectID\": \"3343520b-06fc-4f8e-bbac-c1af75bbb34d\", \"journeyId\": \"65f1d3c8-33ab-467a-a18a-b3d186e675ad\", \"activityId\": \"3343520b-06fc-4f8e-bbac-c1af75bbb34d\", \"definitionInstanceId\": \"af848d2e-8df1-4d9c-b915-9fedb8c0a4fe\", \"activityInstanceId\": \"48811206-f9fc-46d3-a633-4d3079638420\", \"keyValue\": \"sgladden.10000.0003@hotmail.exacttargettest.com\", \"mode\": 0}"

    #json_obj = json.loads(decrypted_token)

    #emailAddress = json_obj['inArguments'][0]['emailAddress']
    #contactIdentifier = json_obj['inArguments'][0]['contactIdentifier']
    #type = "Filed A Case"

    #entry_de_name = retrieve_de_name(entry_de_customer_key, access_token)

    #entry_de_fields = de_customer_key_to_fields(entry_de_customer_key, access_token)
    #unique_id = "EmailAddress"    

    #fields_values = retrieve_de_fields_values(entry_de_customer_key, entry_de_name, unique_id, entry_de_fields, contactIdentifier, access_token)

    #action = "Filed a Case"
    #user_id = fields_values['UserID']

    #if type == "Filed A Case":
        # Retrieve the Data Extension Object Json
    #    with open(os.path.join(SITE_ROOT, "static/templates/", "template_IS_event.json")) as json_file:
    #        retrieve_json = json.load(json_file)


    ## Using the evergage example json, match field names from field_values to evergage fields. If we can find a match, assign the values.
    ## In doing so, dynamically create dict1

    #current_date = "06-14-2020"
    #my_dt = datetime.strptime(current_date, '%m-%d-%Y')    
    #current_date_millis = helper_unix_time_millis(my_dt)

    # should be dynamically created. This is just a test to make sure we can post to evergage api
    #dict1 = { 'action': action ,'user': {'id': contactIdentifier, 'attributes': fields_values}, 'source': {'channel': 'Call Center', 'time': current_date_millis}}
    #retrieve_json.update(dict1)
    
    #make an api call to evergage
    #response = requests.post(IS_ENDPOINT, json=retrieve_json)

    return render_template('index.html', message="Custom Activity", debug_message=debug_message, css_path=path_to_css)

@app.route('/journeybuilder/getdefields/', methods=['POST'])
def journeybuilder_get_de_fields():

    if request.method == 'POST':
        de_customer_key = request.form["DECustomerKey"]

    response = requests.post(LOG_NOTIFICATION_URL, de_customer_key)

    #retrieve_de_name(de_customer_key, access_token):
    #de_customer_key_to_fields(de_customer_key, access_token):
    jsonified_test = {"fname": "Mark", "lname": "Mukherjee"}  

    return jsonify(jsonified_test)


@app.route('/journeybuilder/execute/', methods=['POST'])
def journeybuilder_execute():
    # Article for execute method not firing: https://salesforce.stackexchange.com/questions/51912/trouble-getting-journeybuilder-to-call-execute-url-on-custom-activity-platform
    # https://salesforce.stackexchange.com/questions/186332/one-to-many-data-binding-journey-custom-activity/186338
    # https://salesforce.stackexchange.com/questions/269769/sfmc-custom-activity-error-a-custom-activity-or-entry-source-failed-validation
    # https://salesforce.stackexchange.com/questions/185511/journey-builder-custom-activity-not-a-valid-argument?rq=1
    # https://salesforce.stackexchange.com/questions/185792/accessing-entry-event-data-journey-builder-custom-activity
    
    decrypted_token = ""
    
    if request.method == 'POST':

        try:
            decrypted_token = jwt.decode(request.data,JWT_SIGNING_SECRET, algorithms=['HS256'])
        except jwt.DecodeError as e:
            decrypted_token = {}

        #The data we will use to send to Evergage
        # decrypted_token = json.dumps(decrypted_token)

        #Process here the decrypted token, and match it to evergage event api fields

        #Fire evergage event api here

        data = {'title': 'Python request', 'body': 'This is a POST request to the Execute Command', 'decrypted token': json.dumps(decrypted_token), 'data': request.data}

        response = requests.post(LOG_NOTIFICATION_URL, data)

    jsonified_test = { "SegmentMembership": "{this is a test}"}    
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

    jsonified_test = { "SegmentMembership": "{this is a test}"}    
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

    jsonified_test = { "SegmentMembership": "{this is a test}"}    
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

    jsonified_test = { "SegmentMembership": "{this is a test}"}    
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

    jsonified_test = { "SegmentMembership": "{this is a test}"}    
    return jsonify(jsonified_test)


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)

@app.route('/config.json', methods=['GET'])
def send_config_json():

    #SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "static/", "config.json")
    data = json.load(open(json_url))

    return render_template('showjson.jade', data=data)

################################################################################################################
#                                              Helper Functions                                                #
################################################################################################################

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
    epoch = datetime.utcfromtimestamp(0)
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


if __name__ == '__main__':
    app.run()