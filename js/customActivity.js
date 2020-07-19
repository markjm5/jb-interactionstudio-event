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
    var pks = [];
    var de_name = "";
    var arr_de_fields = [];

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

                $("#message1").html("You cannot leave the Customer Key Empty. Please enter a valid Customer Key");
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
                                        $("#message1").html("Success! Click Next to Continue");
                                        $("#message2").html(JSON.stringify(json_response.de_name));

                                        $("#summary-view").empty();

                                        arr_de_fields = json_response.de_fields;
                                        var field_group = "";
                                        var dropdown_options = "";
                                        var i;

                                        for(i=0; i < arr_de_fields.length; i++){
                                            dropdown_options += "<option value=\"" + arr_de_fields[i].Name + "\">" + arr_de_fields[i].Name + ' (' + arr_de_fields[i].FieldType + ")</option>";
                                            if(arr_de_fields[i].IsPrimaryKey === 'true'){
                                                pks.push(arr_de_fields[i].Name)
                                            }
                                        }       

                                        var is_template_data = eval(json_is_template_fields_event);

                                        i=0;
                                        for (var key in is_template_data) {
                                            i++;
                                            if (is_template_data[key] == 'true') { // this will check if key is a required field
                                                field_group += "<div class=\"activity-detail slds-grid slds-m-bottom_medium\"><div class=\"deupdate-attribute-list\"><div class=\"slds-grid\"><div class=\"deupdate-field-dropdown slds-col slds-size_5-of-12\"><label class=\"slds-form-element__label\" for=\"de-field-" + i + "\"><abbr class=\"slds-required\" title=\"required\">* </abbr>Required</label><div id=\"dropdownc109\"><div class=\"slds-combobox_container\"><div class=\"slds-combobox slds-dropdown-trigger slds-dropdown-trigger_click slds-combobox-picklist\" aria-expanded=\"false\" aria-haspopup=\"listbox\" role=\"combobox\"><div class=\"slds-combobox__form-element slds-input-has-icon slds-input-has-icon_right\" role=\"none\"><input type=\"text\" class=\"slds-input slds-combobox__input\" id=\"is-template-" + i + "\" aria-controls=\"is-template-" + i + "\" autocomplete=\"off\" role=\"textbox\" placeholder=\"Select an Attribute\" readonly=\"\" value=\"" +  key + "\"></div></div></div></div></div><div class=\"slds-col slds-size_1-of-12 slds-text-align_center equals-symbol\"></div><div class=\"slds-form-element\"><label class=\"slds-form-element__label\" for=\"de-field-" + i + "\"><abbr class=\"slds-required\" title=\"required\">* </abbr>Required</label><div class=\"slds-form-element__control\"><div class=\"slds-select_container\"><select class=\"slds-select\" name=\"select-icecream\" id=\"de-field-" + i + "\" required=\"\"><option value=\"\" disabled selected>Please select</option>" +  dropdown_options + "</select></div></div></div></div></div></div>";
                                            }else{
                                                field_group += "<div class=\"activity-detail slds-grid slds-m-bottom_medium\"><div class=\"deupdate-attribute-list\"><div class=\"slds-grid\"><div class=\"deupdate-field-dropdown slds-col slds-size_5-of-12\"><div id=\"dropdownc109\"><div class=\"slds-combobox_container\"><div class=\"slds-combobox slds-dropdown-trigger slds-dropdown-trigger_click slds-combobox-picklist\" aria-expanded=\"false\" aria-haspopup=\"listbox\" role=\"combobox\"><div class=\"slds-combobox__form-element slds-input-has-icon slds-input-has-icon_right\" role=\"none\"><input type=\"text\" class=\"slds-input slds-combobox__input\" id=\"is-template-" + i + "\" aria-controls=\"is-template-" + i + "\" autocomplete=\"off\" role=\"textbox\" placeholder=\"Select an Attribute\" readonly=\"\" value=\"" +  key + "\"></div></div></div></div></div><div class=\"slds-col slds-size_1-of-12 slds-text-align_center equals-symbol\"></div><div class=\"slds-form-element\"><div class=\"slds-form-element__control\"><div class=\"slds-select_container\"><select class=\"slds-select\" name=\"select-icecream\" id=\"de-field-" + i + "\" required=\"\"><option value=\"\" disabled selected>Please select</option>" +  dropdown_options + "</select></div></div></div></div></div></div>";
                                            }
                                        }

                                        $("#summary-view").prepend(field_group);      // Append the new elements

                                        break;

                                    case 'ProductPurchase':
                                        message = true;
                                        connection.trigger('updateButton', { button: 'next', enabled: Boolean(message) });
                                        $("#message1").html("Success! Click Next to Continue");
                                        $("#message2").html(JSON.stringify(json_response));
                                        break;

                                    default:
                                        message = false;
                                        $("#message1").html("Please Select an Event Template");                                        
                                        var element = document.getElementById("event_template_selection");
                                        element.classList.add("slds-has-error");
                                }

                            }else{

                                $("#message1").html("Could Not Find Data Extension. Please try again with a valid Customer Key");
                                connection.trigger('updateButton', { button: 'next', enabled: Boolean(message) });
                            }
                        } else {
                            $("#message1").html("An error has occurred, please remove custom activity from journey and try again.");
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

        //$("#message").html(JSON.stringify(inArguments));
        $("#message").html("1. Enter the Customer Key of the Entry Data Extension<br>2. Select an IS Template<br>3. Click SAVE EVENT SETTINGS<br>4. Click NEXT");

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
        var DEFieldMappings = getDEFieldMappings();
        
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

        //payload['arguments'].execute.inArguments = resp['arguments'].execute.inArguments;
        payload['arguments'].execute.inArguments = [{
            "tokens": authTokens, 
            "contactIdentifier": "{{Contact.Key}}",
            "emailAddress": "{{InteractionDefaults.Email}}",  
            "customer_key": customerKey,
            "is_template": isTemplate,
            "is_event_mappings": ISEventMappings,
            "de_field_mappings": DEFieldMappings
        }];

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

        alert('de_name: '+ de_name);
        alert('de_fields: ' + JSON.stringify(arr_de_fields));

        for(i=0; i < arr_de_fields.length; i++){

            var val1 = arr_de_fields[i].Name;
            var val2 = 'Contact.Attribute.' + de_name + '."' + val1 + '"';

            alert(val2);

            /*
            dropdown_options += "<option value=\"" + arr_de_fields[i].Name + "\">" + arr_de_fields[i].Name + ' (' + arr_de_fields[i].FieldType + ")</option>";
            if(arr_de_fields[i].IsPrimaryKey === 'true'){
                pks.push(arr_de_fields[i].Name)
            }
            */
        }       

        return de_field_mapping_dict;

    }

});