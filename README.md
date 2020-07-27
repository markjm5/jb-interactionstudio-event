<!-- Headings -->
# Interaction Studio Event Custom Activity

<p>Please follow the below steps for configuring this custom activity in Journey Builder.</p>

## Step 0 - Get Heroku

[Verify you have a Heroku account.](https://www.heroku.com)

## Step 1 - Initial Setup

### Create a package inside of Marketing Cloud, with a Jourey Builder component.

1. Go to Setup<br><br>

2. Go to Platform Tools > Apps > Installed Packages<br><br>

3. Click on the 'New' button<br><br>

4. Enter something descriptive as your Package name<br><br>

5. Click 'Save'<br><br> 

**IMPORTANT: Copy and paste the JWT SIGNING SECRET into a separate notepad document. We will need it bit later** 

6. Click the ‘Add Component’ button<br><br>

7. Select ‘Journey Builder Activity’ and click Next<br><br>

8. Enter the following for your Package Component:

 Field | Value  |
| ------ | --------- |
| Name | *Something intuitive*|
| Description | *Leave blank* |
| Category | Customer Updates |
| Endpoint URL | *Nothing has been deployed to Heroku up to this point, however, we need to create this Activity in order to get the application key. For the time being (since this is a required field), enter in: https://herokuapp.com/ixn/activities/generic-activity and click Save. We will return to this Endpoint URL field shortly to update it.*|


## Step 2 - Deploy the Heroku Application

1. Click the button below to deploy this application to Heroku (**You must be logged into your Heroku Account beforehand**).

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

2. When you click on the ‘Deploy to Heroku’ button to begin the deployment process, you will presented with the following variables. Because most of them are required, **you must configure** them before you deploy the app within Heroku (ensure you are authenticated to your Heroku account for this to work).<br><br>

![](static/documentation/1.png)<br><br>

3. Fill out the form variables:

 Variable Name | Description | Required |
| ------ | --------- | --------- |
| App Name | The name of the App on Heroku. Give it a descriptive name | Yes |
| APPLICATION_DOMAIN | Using the aforementioned App Name, provide the fully qualified Heroku App URL | Yes |
| IS_ENDPOINT | API URL for Interaction Studio Events. In the format https://[ACCOUNT].evergage.com/api2/event/[DATASET] | Yes |
| IS_PRODUCTION | Used for debugging purposes. By default its set to True. Keep the default.| Yes |
| JWT_SIGNING_SECRET | Paste the JWT Signing Secret from Step 1| Yes |
| LOG_NOTIFICATION_URL | Used for debugging purposes. Sends app log details to an external system such as Request.Bin. Leave it Empty| No |

<br><br>4. After you have completed all of the required form fields - click on the *Deploy app* button at the bottom of the page.<br><br>
5. Validate that the app is deployed successfully (You will see a success message like the one below)
<br>![](static/documentation/4.png)<br><br>

## Step 3 - Validate your Heroku Deploy

1. Test this URL after deployment:<br>

http://[YOUR_APP_NAME_HERE].herokuapp.com/config.json


<br>![](static/documentation/2.png)<br><br>

2. You can paste the contents of that file into an online JSON formatting tool to check that it looks like this:

```javascript
{
   "workflowApiVersion":"1.1",
   "metaData":{
      "icon":"static/icon1.png",
      "iconSmall":"static/iconSmall1.png",
      "category":"customer"
   },
   "key":"REST1",
   "type":"REST",
   "lang":{
      "en-US":{
         "name":"IS Event v1",
         "description":"An example REST activity using workflow API v1.1 format."
      }
   },
   "arguments":{
      "execute":{
         "outArguments":[
            {
               "SegmentMembership":""
            }
         ],
         "url":"https://[YOUR_APP_NAME].herokuapp.com/journeybuilder/execute/",
         "verb":"POST",
         "body":"",
         "header":"",
         "format":"json",
         "useJwt":true,
         "timeout":10000
      }
   },
   "configurationArguments":{
      "save":{
         "url":"https://[YOUR_APP_NAME].herokuapp.com/journeybuilder/save/",
         "verb":"POST",
         "useJwt":true
      },
      "publish":{
         "url":"https://[YOUR_APP_NAME].herokuapp.com/journeybuilder/publish/",
         "verb":"POST",
         "useJwt":true
      },
      "stop":{
         "url":"https://[YOUR_APP_NAME].herokuapp.com/journeybuilder/stop/",
         "verb":"POST",
         "useJwt":true
      },
      "validate":{
         "url":"https://[YOUR_APP_NAME].herokuapp.com/journeybuilder/validate/",
         "verb":"POST",
         "useJwt":true
      }
   },
   "wizardSteps":[
      {
         "label":"Step 1",
         "key":"step1"
      },
      {
         "label":"Step 2",
         "key":"step2"
      }
   ],
   "userInterfaces":{
      "configModal":{
         "height":300,
         "width":800,
         "fullscreen":true
      }
   },
   "schema":{
      "arguments":{
         "execute":{
            "outArguments":[
               {
                  "SegmentMembership":{
                     "dataType":"Text",
                     "direction":"out",
                     "access":"visible"
                  }
               }
            ]
         }
      }
   }
}
```

3. Go back to your Journey Builder component that was created in Step 1, and update the Endpoint URL from https://herokuapp.com/ixn/activities/generic-activity to the URL of your newly deployed Heroku App, ie. http://[YOUR_APP_NAME_HERE].herokuapp.com/ (http://[your_app_name_here].herokuapp.com/) <br><br>

4. Locate the activity in Journey Builder

<br>![](static/documentation/3.png)<br><br>

## Step 4 - Using the Custom Activity

1. When creating a new Journey, ensure that you have selected an Entry Source first with a corresponding Data Extension. The IS Entry Custom Acivity will only work with an Entry Source Data Extension.<br><br>

2. After selecting an Entry Source, drag the IS Event custom activity onto the journey canvas. Click on the custom activity to open the settings.<br><br>

3. Once the custom activity settings are opened, you will notice there are 2 steps. In Step 1, you will need to select from a list of templates, which are:

Template | Description  |
| ------ | --------- |
| Generic User Event | Used to sent any generic Event across to IS. Some examples could be email sent/opened, sms sent/opened etc.  |
| Product View | Used to send Events across where the customer has viweed a particular product. The product does not need to pre-exist in IS beforehand but rather gets created on the fly. The product details specified in this template will be used to create a new product in IS if it does not exist already. |
| Product Purchase | Used to send a Product Purchase event across to IS. |

Once you have selected your template, click ‘Next’<br><br>

4. In Step 2, map the fields from your Entry Data Extension to the IS Event Template. Below is a reference guide for each field in each of the templates:

 Template| Field | Type | Description  |
| ------ | --------- |--------- |--------- |
| Generic User Event | user_id | Text/Numeric | An identifier for the user  |
|        | action    | Text | An Action such as *Sent Email* or *Viewed Page* |
|        | source    | Text | The source of the Event, such as *Journey Builder* |
|        | event_date | Date | Either a historical date, or if left blank the current date will be used |
|        | first_name | Text | First name of the subscriber |
|        | last_name | Text | Last name of the subscriber |
| Product View | user_id | Text/Numeric | An identifier for the user  |
|        | action | Text | An Action such as *Sent Email* or *Viewed Page* |
|        | source    | Text | The source of the Event, such as *Journey Builder* |
|        | source_url | Url |  |
|        | page_type | Text |  |
|        | event_date | Date | Either a historical date, or if left blank the current date will be used |
|        | product_id | Text/Numeric |  |
|        | product_name | Text |  |
|        | product_url | Url |  |
|        | product_imageUrl | Url |  |
|        | product_description | Text |  |
|        | product_price | Decimal |  |
|        | product_currency | Text |  |
|        | product_inventoryCount | Integer |  |
| Product Purchase | user_id | Text/Numeric | An identifier for the user  |
|        | source    | Text | The source of the Event, such as *Journey Builder* |
|        | event_date | Date | Either a historical date, or if left blank the current date will be used |
|        | order_id | Text/Numeric | An identifier for the order |
|        | currency | Text |           |
|        | line_items | Json | Each line item in the order. Needs to match the below specification |
|        | | | `[{` |
|        | | | ` _id: freedom-card,` |
|        | | | ` price: 25.00,` |
|        | | | ` quantity: 2` |
|        | | | `},` |
|        | | | `{` |
|        | | | ` _id: student-card,` |
|        | | | ` price: 25.00,` |
|        | | | ` quantity: 2` |
|        | | | `},` |
|        | | | `{...}`|
|        | | | `]`|

5. Click ‘Done’ once you have finished mapping the fields. 

6. Activate the Journey.

Whenever a contact enters the Journey and reaches the IS Event Custom Activity, their details will be sent to Interaction Studio using the template mapping rules that have been configured. 