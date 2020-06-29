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
    var json_is_template_fields_event = {"user_id":"true","action":"true","source":"false","event_date":"false"};

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

    function onRender() {
        // JB will respond the first time 'ready' is called with 'initActivity'
        connection.trigger('ready');

        connection.trigger('requestTokens');
        connection.trigger('requestEndpoints');

        // Disable the next button if a value isn't selected
        $('#submit').click(function() {
            var customer_key = getCustomerKey();

            var e = document.getElementById("select-01");
            var event_template = e.options[e.selectedIndex].value;

            //alert('m1:' + customer_key);
            //alert('m1a:' + event_template);

            var message = false;
            var url = "https://jb-interactionstudio-event.herokuapp.com/journeybuilder/getdefields/"; 

            var sendInfo = {
                DECustomerKey: customer_key,
            };
            var json_response = "Nada";
            if(customer_key.replace(/\s/g,'') == ""){

                $("#message").html("You cannot leave the Customer Key Empty. Please enter a valid Customer Key");
            }else{
                $.ajax({
                    type: "POST",
                    url: url,
                    dataType: "json",
                    success: function (msg) {
                        if (msg) {

                            json_response = JSON.parse(JSON.stringify(msg));    
                            //alert('m3:' + json_response);

                            //location.reload(true);
                            if(json_response.error == 'False'){
                                var element = document.getElementById("event_template_selection");

                                element.classList.remove("slds-has-error");
                                $("#template_type").html("\"" + event_template + "\"");

                                switch(event_template) {
                                    case 'GenericUserEvent':
                                        message = true;
                                        connection.trigger('updateButton', { button: 'next', enabled: Boolean(message) });
                                        $("#message").html("Success! Click Next to Continue");
                                        $("#message1").html("You have chosen the Data Extension " + JSON.stringify(json_response.de_name));

                                        var arr_de_fields = json_response.de_fields;
                                        var field_group = "";
                                        var dropdown_options = "";
                                        var i;

                                        for(i=0; i < arr_de_fields.length; i++){
                                            dropdown_options += "<option value=\"" + arr_de_fields[i].Name + "\">" + arr_de_fields[i].Name + ' (' + arr_de_fields[i].FieldType + ")</option>";
                                        }       

                                        var is_template_data = eval(json_is_template_fields_event);

                                        i=0;
                                        for (var key in is_template_data) {
                                            i++;
                                            if (is_template_data[key] == 'true') { // this will check if key is a required field
                                                field_group += "<div class=\"activity-detail slds-grid slds-m-bottom_medium\"><div class=\"deupdate-attribute-list\"><div class=\"slds-grid\"><div class=\"deupdate-field-dropdown slds-col slds-size_5-of-12\"><label class=\"slds-form-element__label\" for=\"de-field-" + i + "\"><abbr class=\"slds-required\" title=\"required\">* </abbr>Required</label><div id=\"dropdownc109\"><div class=\"slds-combobox_container\"><div class=\"slds-combobox slds-dropdown-trigger slds-dropdown-trigger_click slds-combobox-picklist\" aria-expanded=\"false\" aria-haspopup=\"listbox\" role=\"combobox\"><div class=\"slds-combobox__form-element slds-input-has-icon slds-input-has-icon_right\" role=\"none\"><input type=\"text\" class=\"slds-input slds-combobox__input\" id=\"is-template-" + i + "\" aria-controls=\"is-template-" + i + "\" autocomplete=\"off\" role=\"textbox\" placeholder=\"Select an Attribute\" readonly=\"\" value=\"" +  key + "\"></div></div></div></div></div><div class=\"slds-col slds-size_1-of-12 slds-text-align_center equals-symbol\">=</div><div class=\"slds-form-element\"><label class=\"slds-form-element__label\" for=\"de-field-" + i + "\"><abbr class=\"slds-required\" title=\"required\">* </abbr>Required</label><div class=\"slds-form-element__control\"><div class=\"slds-select_container\"><select class=\"slds-select\" name=\"select-icecream\" id=\"de-field-" + i + "\" required=\"\"><option value=\"\" disabled selected>Please select</option>" +  dropdown_options + "</select></div></div></div></div></div></div>";
                                            }else{
                                                field_group += "<div class=\"activity-detail slds-grid slds-m-bottom_medium\"><div class=\"deupdate-attribute-list\"><div class=\"slds-grid\"><div class=\"deupdate-field-dropdown slds-col slds-size_5-of-12\"><div id=\"dropdownc109\"><div class=\"slds-combobox_container\"><div class=\"slds-combobox slds-dropdown-trigger slds-dropdown-trigger_click slds-combobox-picklist\" aria-expanded=\"false\" aria-haspopup=\"listbox\" role=\"combobox\"><div class=\"slds-combobox__form-element slds-input-has-icon slds-input-has-icon_right\" role=\"none\"><input type=\"text\" class=\"slds-input slds-combobox__input\" id=\"is-template-" + i + "\" aria-controls=\"is-template-" + i + "\" autocomplete=\"off\" role=\"textbox\" placeholder=\"Select an Attribute\" readonly=\"\" value=\"" +  key + "\"></div></div></div></div></div><div class=\"slds-col slds-size_1-of-12 slds-text-align_center equals-symbol\">=</div><div class=\"slds-form-element\"><div class=\"slds-form-element__control\"><div class=\"slds-select_container\"><select class=\"slds-select\" name=\"select-icecream\" id=\"de-field-" + i + "\" required=\"\"><option value=\"\" disabled selected>Please select</option>" +  dropdown_options + "</select></div></div></div></div></div></div>";
                                            }
                                        }

                                        $("#summary-view").prepend(field_group);      // Append the new elements

                                        break;

                                    case 'ProductPurchase':
                                        message = true;
                                        connection.trigger('updateButton', { button: 'next', enabled: Boolean(message) });
                                        $("#message").html("Success! Click Next to Continue");
                                        $("#message1").html(JSON.stringify(json_response));
                                        break;

                                    default:
                                        message = false;
                                        $("#message").html("Please Select an Event Template");                                        
                                        var element = document.getElementById("event_template_selection");
                                        element.classList.add("slds-has-error");
                                }

                            }else{

                                $("#message").html("Could Not Find Data Extension. Please try again with a valid Customer Key");
                                connection.trigger('updateButton', { button: 'next', enabled: Boolean(message) });
                            }
                        } else {
                            $("#message").html("An error has occurred, please remove custom activity from journey and try again.");
                            connection.trigger('updateButton', { button: 'next', enabled: Boolean(message) });
                        }
                    },

                    data: sendInfo
                });
            }
            //connection.trigger('updateButton', { button: 'next', enabled: Boolean(message) });

        });

        
        /*
        // Toggle step 4 active/inactive
        // If inactive, wizard hides it and skips over it during navigation
        $('#toggleLastStep').click(function() {
            lastStepEnabled = !lastStepEnabled; // toggle status
            steps[3].active = !steps[3].active; // toggle active

            connection.trigger('updateSteps', steps);
        });*/
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
        //alert('inArguments: ' + JSON.stringify(inArguments));
        $("#message").html(JSON.stringify(inArguments));

        $.each(inArguments, function(index, inArgument) {
            $.each(inArgument, function(key, val) {
                if (key === 'message') {
                    message = val;
                }
            });
        });

        // If there is no message selected, disable the next button
        if (!message) {
            showStep(null, 1);
            connection.trigger('updateButton', { button: 'next', enabled: false });
            // If there is a message, skip to the summary step
        } else {
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

     // NEED TO LOOK AT THIS FUNCTION IN MORE DETAIL. THIS IS THE FUNCTION THAT SENDS THE PAYLOAD IN THE inArguments
     /*
     function save() {
        var postcardURLValue = $('#postcard-url').val();
        var postcardTextValue = $('#postcard-text').val();

        payload['arguments'].execute.inArguments = [{
            "tokens": authTokens,
            "emailAddress": "{{Contact.Attribute.PostcardJourney.EmailAddress}}"
        }];
        
        payload['metaData'].isConfigured = true;

        console.log(payload);
        connection.trigger('updateActivity', payload);
    }
    */

    function save() {
        var name = $("#select1").find('option:selected').html();
        var customerKey = getCustomerKey();
        var isTemplate = getISTemplate();
        var ISEventMappings = getISEventMappings();

        // 'payload' is initialized on 'initActivity' above.
        // Journey Builder sends an initial payload with defaults
        // set by this activity's config.json file.  Any property
        // may be overridden as desired.
        payload.name = name;
        //var req = new XMLHttpRequest();
        //req.open("POST", "https://mmdemofeedback.herokuapp.com/config.json");
        //var resp = req.send();
        console.log('Here1');
        /*resp['arguments'].execute.inArguments.push({"message":value});*/
        console.log('Here2');

        //payload['arguments'].execute.inArguments = resp['arguments'].execute.inArguments;
        payload['arguments'].execute.inArguments = [{
            "tokens": authTokens,
            "emailAddress": "{{InteractionDefaults.Email}}",        
            "contactIdentifier": "{{Contact.Key}}",    
            "customer_key": customerKey,
            "is_template": isTemplate,
            "is_event_mappings": ISEventMappings
        }];

        payload['metaData'].isConfigured = true;

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
        //alert("arrLen: " + array_length);
        //for (var key in is_template_data) {
            //i++;

        for(i=1; i < array_length + 1; i++){

            //val1 = $('#is-template-' + i + ':selected').text();
            var val1 = $('#is-template-' + i).val();
            var val2 = $('#de-field-' + i).val();

            //var val2 = $('#de-field-' + i + ':selected').text();

            //alert("is-template-" + i);
            //var e = document.getElementById("is-template-" + i);
            //alert("SelIndex: " + e.selectedIndex);
            //var is_template_value = e.options[e.selectedIndex].value;

            //var f = document.getElementById("de-field-" + i );
            //var de_field_value = f.options[f.selectedIndex].value;

            alert(val1 + ": " + val2);
        }

        //Need to write JS to retrieve mapping selections and put them into an array
        return $("#select-01").val();
    }

});