define([
    'postmonger'
], function(
    Postmonger
) {
    'use strict';

    var connection = new Postmonger.Session();
    var payload = {};
    var authTokens = {};
    var lastStepEnabled = false;
    var json_is_template_fields_event = {"user_id":"true","action":"true","source":"false","event_date":"false", "first_name":"false", "last_name":"false"};
    //var pks = [];
    var arr_de_fields = [];
    //var customer_key = "";
    var eventDefinitionKey;
    var de_schema = [];
    //TODO: We don't need to put the customer key of the DE into a text field. We can just use postmonger to get the DE name and Key 
    // from the entry evnet https://salesforce.stackexchange.com/questions/221821/get-the-name-of-the-data-extension-you-are-working-with-custom-activity
    
    var steps = [ // initialize to the same value as what's set in config.json for consistency
        { "label": "Step 1", "key": "step1" },
        { "label": "Step 2", "key": "step2" }
    ];
    var currentStep = steps[0].key;

    $(window).ready(onRender);

    connection.on('initActivity', initialize);
    connection.on('requestedTokens', onGetTokens);
    connection.on('requestedEndpoints', onGetEndpoints);

    connection.on('clickedNext', onClickedNext);
    connection.on('clickedBack', onClickedBack);
    connection.on('gotoStep', onGotoStep);
    connection.on('requestedTriggerEventDefinition', eventDefinitionModel);    
    connection.on('requestedSchema', requestedSchemaModel);    
    connection.on('requestedInteraction', requestedInteractionModel);    

    function eventDefinitionModel(eventDefinitionModel) {
        if(eventDefinitionModel){
            alert('here2');
    
            eventDefinitionKey = eventDefinitionModel.eventDefinitionKey;
            //alert('event def model' + JSON.stringify(eventDefinitionModel));
            console.log(">>>Event Definition Key " + eventDefinitionKey);
            /*If you want to see all*/
            console.log('>>>Request Trigger', 
            JSON.stringify(eventDefinitionModel));
        }
    
    }

    function requestedSchemaModel(data) {
        // save schema
        alert('here1');
        console.log('>>>Request Schema', JSON.stringify(data.schema));
        var i;
        for(i=0; i < data.schema.length; i++){
            alert('test: ' + JSON.stringify(data.schema[i]));
            de_schema.push(data.schema[i]);
        }       

        alert('Length: ' + de_schema.length);
     }    

     function requestedInteractionModel(interaction) {
        // save schema
        alert('here3');
        console.log('>>>Request Interaction', JSON.stringify(interaction));
     }    


    function onRender() {
        // JB will respond the first time 'ready' is called with 'initActivity'
        connection.trigger('ready');

        connection.trigger('requestTokens');
        connection.trigger('requestEndpoints');

        connection.trigger('requestSchema');
        connection.trigger('requestTriggerEventDefinition');    
        connection.trigger('requestInteraction');    

        var message = false;

        alert(JSON.stringify(de_schema));

        connection.trigger('updateButton', { button: 'next', enabled: Boolean(message) });

    }


    //var element = document.getElementById("event_template_selection");
    //element.classList.add("slds-has-error");
    /*
    $('#combobox-id-1').click(function() {

        //alert("Second Submit Button Clicked");
        var element = document.getElementById("combobox1");
        element.classList.add("slds-is-open");

    });
    */

    function initialize (data) {
        if (data) {
            payload = data;
        }

        var message;
        var hasInArguments = Boolean(
            payload['arguments'] &&
            payload['arguments'].execute &&
            payload['arguments'].execute.inArguments &&
            payload['arguments'].execute.inArguments.length > 0
        );

        var inArguments = hasInArguments ? payload['arguments'].execute.inArguments : {};

        //$("#message").html(JSON.stringify(inArguments));
        //$("#message").html("1. Enter the Customer Key of the Entry Data Extension<br>2. Select an IS Template<br>3. Click SAVE EVENT SETTINGS<br>4. Click NEXT");

        $.each(inArguments, function(index, inArgument) {
            $.each(inArgument, function(key, val) {
                if(key === 'customer_key'){
                    $('#activity-name-input').val(val);
                }

                if(key === 'is_template'){
                    $('#select-01').val(val);
                    
                }

                if(key === 'is_event_mappings'){
                    //alert('key:val - ' + key + ': ' + val);
                    var json_selected_fields = [];
                    var field_group = "";
                    var i = 0;
                    $.each(val, function(key1, val1) {
                        //message = val;
                        i++;
                        field_group += "<div class=\"activity-detail slds-grid slds-m-bottom_medium\"> <div class=\"deupdate-attribute-list\"> <div class=\"slds-grid\"> <div class=\"deupdate-field-dropdown slds-col slds-size_5-of-12\"> <div id=\"dropdownc109\"> <div class=\"slds-combobox_container\"> <div class=\"slds-combobox slds-dropdown-trigger slds-dropdown-trigger_click slds-combobox-picklist\" aria-expanded=\"false\" aria-haspopup=\"listbox\" role=\"combobox\"> <div class=\"slds-combobox__form-element slds-input-has-icon slds-input-has-icon_right\" role=\"none\"> <input type=\"text\" class=\"slds-input slds-combobox__input\" id=\"is-template-" + i + "\" aria-controls=\"dropdownc109-input\" autocomplete=\"off\" role=\"textbox\" placeholder=\"Select an Attribute\" readonly=\"\" value=\"" + key1 + "\"> </div> </div> </div> </div> </div> <div class=\"slds-col slds-size_1-of-12 slds-text-align_center equals-symbol\"></div> <div class=\"deupdate-field-dropdown slds-col slds-size_5-of-12\"> <div id=\"dropdownc109\"> <div class=\"slds-combobox_container\"> <div class=\"slds-combobox slds-dropdown-trigger slds-dropdown-trigger_click slds-combobox-picklist\" aria-expanded=\"false\" aria-haspopup=\"listbox\" role=\"combobox\"> <div class=\"slds-combobox__form-element slds-input-has-icon slds-input-has-icon_right\" role=\"none\"> <input type=\"text\" class=\"slds-input slds-combobox__input\" id=\"de-field-" + i + "\" aria-controls=\"de-field-" + i + "\" autocomplete=\"off\" role=\"textbox\" placeholder=\"Select an Attribute\" readonly=\"\" value=\"" + val1 + "\"> </div> </div> </div> </div> </div> </div> </div> </div> </div>";
                    });
                    $("#summary-view").prepend(field_group);
                    //alert(JSON.stringify(json_selected_fields));
                }
            });
        });
        
        //alert(Object.keys(inArguments[0])[3]);
        // If there is no message selected, disable the next button
        if (document.getElementById('activity-name-input').value === "") {
            //alert('value NOT selected!');

            showStep(null, 1);
            connection.trigger('updateButton', { button: 'next', enabled: false });
            // If there is a message, skip to the summary step
        } else {
            //alert('value selected!');
            $("#select1").find('option[value='+ message +']').attr('selected', 'selected');
            //$("#message").html(message);
            showStep(null, 1);
        }
    }

    function onGetTokens (tokens) {
        // Response: tokens = { token: <legacy token>, fuel2token: <fuel api token> }
        // console.log(tokens);
        authTokens = tokens;
    }

    function onGetEndpoints (endpoints) {
        // Response: endpoints = { restHost: <url> } i.e. "rest.s1.qa1.exacttarget.com"
        // console.log(endpoints);
    }

    function onClickedNext () {
        //alert('onClickedNext');
        if (currentStep.key === 'step2') {
            save();
        } else {
            connection.trigger('nextStep');
        }
    }

    function onClickedBack () {
        connection.trigger('prevStep');
    }

    function onGotoStep (step) {
        showStep(step);
        connection.trigger('ready');
    }

    function showStep(step, stepIndex) {
        if (stepIndex && !step) {
            step = steps[stepIndex-1];
        }

        currentStep = step;
        
        $('.step').hide();

        switch(currentStep.key) {
            case 'step1':
                $("#step1").show();
                connection.trigger('updateButton', {
                    button: 'next',
                    enabled: Boolean(getCustomerKey())
                });
                connection.trigger('updateButton', {
                    button: 'back',
                    visible: false
                });
                break;
            case 'step2':
                $("#step2").show();
                connection.trigger('updateButton', {
                    button: 'back',
                    visible: true
                });
                connection.trigger('updateButton', {
                    button: 'next',
                    text: 'done',
                    visible: true
                });
                break;
        }
        
    } 
    
    function save() {
        var name = $("#select1").find('option:selected').html();
        var customerKey = getCustomerKey();
        var isTemplate = getISTemplate();
        var ISEventMappings = getISEventMappings();
        //var DEFieldMappings = getDEFieldMappings();
        var in_args_dict = {};
        var de_name = $('#message2').text();
        var de_field_values_dict = {};
        var i;

        // 'payload' is initialized on 'initActivity' above.
        // Journey Builder sends an initial payload with defaults
        // set by this activity's config.json file.  Any property
        // may be overridden as desired.
        payload.name = name;
        //var req = new XMLHttpRequest();
        //req.open("POST", "https://mmdemofeedback.herokuapp.com/config.json");
        //var resp = req.send();
        console.log('Here1');
        //payload['arguments'].execute.inArguments = [{"message":customerKey}];
        console.log('Here2');

        //obsolete - example of using event
        //in_args_dict["test"] = '{{Event.APIEvent-78cb2bff-796b-d3ce-b911-f2e81f1621ed."Gender"}}';

        //in_args_dict["test1"] = '{{Contact.Attribute."Cumulus_IS_Members2"."Gender"}}';
        //in_args_dict["test2"] = '{{Contact.Attribute.Persona."Gender"}}';
        
        //in_args_dict["test1"] = '{{Event.' + eventDefinitionKey + '."Gender"}}';

        in_args_dict["tokens"] = authTokens;
        in_args_dict["contactIdentifier"] =  "{{Contact.Key}}";
        in_args_dict["emailAddress"] = "{{InteractionDefaults.Email}}";
        in_args_dict["customer_key"] = customerKey;
        in_args_dict["is_template"] = isTemplate;
        in_args_dict["is_event_mappings"] = ISEventMappings;
        in_args_dict["entry_de_name"] = de_name;
        
        for(i=0; i < arr_de_fields.length; i++){
            var val1 = arr_de_fields[i].Name;
            de_field_values_dict[val1] = "{{Event." + eventDefinitionKey + ".\"" + val1 + "\"}}";
        }       

        in_args_dict["de_field_mappings"] = de_field_values_dict;

        //payload['arguments'].execute.inArguments = resp['arguments'].execute.inArguments;
        /*payload['arguments'].execute.inArguments = [{
            "tokens": authTokens, 
            "contactIdentifier": "{{Contact.Key}}",
            "emailAddress": "{{InteractionDefaults.Email}}",  
            "customer_key": customerKey,
            "is_template": isTemplate,
            "is_event_mappings": ISEventMappings,
            "de_field_mappings": DEFieldMappings
        }];*/

        payload['arguments'].execute.inArguments = [];
        payload['arguments'].execute.inArguments.push(in_args_dict);

        payload['metaData'].isConfigured = true;

        console.log(payload);

        connection.trigger('updateActivity', payload);
    }
    

    function getCustomerKey() {  

        return $("#activity-name-input").val();
    }
    function getISTemplate() {  

        return $("#select-01").val();
    }

    function getISEventMappings() {  

        var is_template_data = eval(json_is_template_fields_event);
        var array_length = Object.keys(is_template_data).length;
        var i;
        var field_mapping_dict = {};

        for(i=1; i < array_length + 1; i++){

            var val1 = $('#is-template-' + i).val();
            var val2 = $('#de-field-' + i).val();

            //alert(val1 + ": " + val2);
            if(!val2){
                field_mapping_dict[val1] = '';
            }else {
                field_mapping_dict[val1] = val2;
            }
        }

        //Need to write JS to retrieve mapping selections and put them into an array
        return field_mapping_dict; //$("#select-01").val();
    }

    function getDEFieldMappings() {  
        var de_name = $('#message2').text();
        var de_field_mapping_dict = {};
        var i;
        
        //alert('customer_key: ' + customer_key);
        //alert('de_name: '+ de_name);
        //alert('de_fields: ' + JSON.stringify(arr_de_fields));

        for(i=0; i < arr_de_fields.length; i++){

            var val1 = arr_de_fields[i].Name;
            var val2 = '{{Contact.Attribute.' + de_name + '.' + val1 + '}}';

            //alert(val2);

            de_field_mapping_dict[val1] = val2; 
        }       
        alert(JSON.stringify(de_field_mapping_dict));

        return JSON.stringify(de_field_mapping_dict);

    }

});