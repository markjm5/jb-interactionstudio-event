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

6. Select ‘Add Component’ button<br><br>

7. Select ‘Journey Builder Activity’ and click Next<br><br>

8. Enter the following:

 Field | Value  |
| ------ | --------- |
| Name | *Something intuitive*|
| Description | *Leave blank* |
| Category | Customer Updates |
| Endpoint URL | *Nothing has been deployed to Heroku up to this point, however, we need to create this Activity in order to get the application key. For the time being (since this is a required field), enter in: https://herokuapp.com/ixn/activities/generic-activity and click Save.*|


### Begin the Heroku deploy process

### Add Component to your Journey Builder Package in Marketing Cloud

### Validate your Heroku Deploy

## Step 2 - Create your Data Extension in Marketing Cloud

## Step 3 - Create and Activate a Journey in Marketing Cloud

<p>Please click the button below to deploy this application to Heroku.</p>

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)