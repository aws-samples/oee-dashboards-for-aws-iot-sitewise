# OEE Dashboards for AWS IoT SiteWise

## About

This project is a compliment to the AWS Blog  **Creating OEE Dashboard for AWS IoT SiteWise article**.  The blog article primarily provides the steps for creating an AWS IoT SiteWise model (including its attributes, measurements, and transforms) via the AWS Management Console, and then secondarily touches on doing so programmatically via the AWS IoT SiteWise APIs.  This project illustrates the latter and then also provides sample data that can be streamed into AWS IoT SiteWise as part of a simulation. 

## Prerequisites

1. Non-production AWS account
2. Sufficiently privileged identity for the AWS account on [IoT SiteWise](https://docs.aws.amazon.com/iot-sitewise/latest/userguide/security_iam_id-based-policy-examples.html) 
3. AWS Command Line Interface (CLI)
4. Python 3.7 (or higher)
5. AWS SDK for Python (Boto3)
6. Pandas Python Module
7. Git
8. Read AWS Blog [Creating OEE Dashboards for AWS IoT SiteWise](update-link.com)
9. Create the AWS IoT SiteWise model as described in the blog article

## Getting started

There are several ways to follow the instructions provided here, for simplicity we recommend using [CloudShell](https://aws.amazon.com/cloudshell/), however feel free to use whatever alternative you prefer, as long as you are aware of the requirements associated with each the options.  Select an AWS Region you desire to work on and keep it consistent across the instructions provided here. 

1. CloudShell: 
  - Launch the AWS CloudShell from the AWS Console, using this option you will have the following components already installed: AWS Command Line Interface, Python3, Boto3 Python library, Git.
  - Install the Pandas Python Library (includes Numpy) using the following commands:
     ```
     python3 -m ensurepip --upgrade 
     pip3 install pandas
     ``` 

2. [Cloud9](https://aws.amazon.com/cloud9/): 
  - Create a Cloud9 environment from the AWS Console and launch a terminal, using this option you will have the following components already installed: AWS Command Line Interface, Python3, Boto3 Python library, Git. 
  - Install the Pandas Python Library (includes Numpy) using the following command:
     ```
     pip3 install pandas
     ``` 

3. Use your own workstation, you will need to manually install the following components:
- AWS Command Line Interface: [visit](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html) for more details on the installation. Additionally, configure the credentials for the [CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html)
- Python 3.7 or higher: [visit](https://www.python.org/downloads/) 
- Python Library requirements: see [requirements.txt](requirements.txt) for a complete list.
- Git: [visit](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)

## Clone the project
From your terminal run:
```
git clone https://github.com/aws-samples/oee-dashboards-for-aws-iot-sitewise
```

We will be referencing files downloaded to the directory **oee-dashboards-for-aws-iot-sitewise/**


## Modify an AWS IoT SiteWise Model Programmatically
In order to create new measurements, transforms and/or metrics on a AWS IoT SiteWise model, we need to identify the model ID and the property IDs of the variables that make up the formula.

### Identify the model ID

1. Go to [IoT SiteWise on the AWS Console](https://console.aws.amazon.com/iotsitewise/), select the appropiate AWS Region on the top right hand corner of the console. Be consistent with the region as you continue following the instructions.

2. On the left-hand side tree click on Models under Build and find the model on the list, then click on it to display its properties.

![Get Model ID](/images/model-list.png)

3. You can also obtain the model ID using the AWS CLI by running this:
```
aws iotsitewise list-asset-models --region [AWS Region]
```
The output will include all models available, you can alternatively filter it using jq, replace 'Carousel' for your model name
```
aws iotsitewise list-asset-models --region [AWS Region] | jq .'assetModelSummaries[] | select(.name=="Carousel")'
```

The output should look like this:
```
{
  "id": "8fce91e9-62dd-472d-9d13-81b13fec04f6",
  "arn": "arn:aws:iotsitewise:us-west-2:XXXXXXXXXXXX:asset-model/8fce91e9-62dd-472d-9d13-81b13fec04f6",
  "name": "Carousel",
  "description": "Bag Carousel",
  "creationDate": "2022-11-15T13:36:53-07:00",
  "lastUpdateDate": "2022-12-14T14:43:40-07:00",
  "status": {
    "state": "ACTIVE"
  }
}
```

### Prepare the JSON property file
Look at the equipment_state.json file for an example of how a new transform called 'Equipment_State' is defined referencing other existing measurements in the asset model. Multiple properties can be defined in a single file.
Make sure you update the **propertyId** values in this file accordingly, for more information on how to identify the propertyId for your particular model please see the AWS Blog [Creating OEE Dashboards for AWS IoT SiteWise](update-link.com).

### Update Asset Model
Proceed to modify the model running the following command:
```
python3 update_asset_model_sitewise.py --assetModelId [Asset Model ID] --property_file equipment_state.json --region [AWS Region]
```

The output should look like this:
```
{
    'ResponseMetadata': {
        'RequestId': 'f8e5291c-ba9c-4fdc-93c0-90a32cc09192', 
        'HTTPStatusCode': 202, 
        'HTTPHeaders': {
            'date': 'Wed, 14 Dec 2022 21:43:40 GMT', 
            'content-type': 'application/json', 
            'content-length': '41', 
            'connection': 'keep-alive', 
            'x-amzn-requestid': 'f8e5291c-ba9c-4fdc-93c0-90a32cc09192'
        }, 
        'RetryAttempts': 0
    }, 
    'assetModelStatus': {
        'state': 'UPDATING'
    }
}
```

After the script returns a successful response, the new property ID created can be obtained directly from the AWS console as described before or by using the AWS CLI. To query the updated model definition and obtain the new property ID use the following command.
```
aws iotsitewise describe-asset-model --asset-model-id [model ID] --region [AWS Region] | jq .'assetModelProperties[] |
select(.name=="Equipment_State")'.id
```

## Bag Handling System (BHS) Data Simulation
You can capture and stream data to AWS IoT SiteWise from a physical BHS as described on the AWS Blog [Creating OEE Dashboards for AWS IoT SiteWise](update-link.com). Alternatively , you can do it by using historical data captured from a physical system. The sample data is provided in this repository in order for you to run a simulation of a BHS and stream data to AWS IoT SiteWise as if sensor data was being generated in real time.

### Setting up the environment for data streaming to AWS IoT SiteWise
1. From the environment where you cloned the project, navigate to the sample data `sensor_data.tar.gz` location.
```
cd oee-dashboards-for-aws-iot-sitewise/
```
2.  Extract the sensor data file:
```
tar -xvzf sensor_data.tar.gz
```
This will create the 2022_april directory. 

**NOTE:** if you have been following the instructions on the AWS Blog [Creating OEE Dashboards for AWS IoT SiteWise](update-link.com) you will have an Asset already created in AWS IoT SiteWise, including attributes and measurements. 

![Get Model ID](/images/asset-measurements.png)

3. Edit the files **carousel-speed-photo-template.json** and **carousel-vibration-template.json** with the AssetID and Measurement IDs obtained in the previous sections. Do not modify other fields as the required information will be updated accordingly by the main python script as data is streamed to IoT SiteWise.

### Running the Python Script to stream data to AWS IoT SiteWise
1. From the same location where the project files are, run the python script:
```
python3 stream_to_sitewise.py
```
2. The output of the command should look like this:
```
...
Streaming data for Day 1, Hour 0
Vibration request=[{'entryId': 'VibrationL-Crest', 'assetId': 'b50a2f9f-e2d6-42c1-97b2-591169a4f270', 'propertyId': '2e2d8591-91a6-47b7-b30b-f12862caa666', 'propertyValues': [{'value': {'doubleValue': 28.0}, 'timestamp': {'timeInSeconds': 1671137565}}]}, {'entryId': 'VibrationL-Fatigue', 'assetId': 'b50a2f9f-e2d6-42c1-97b2-591169a4f270', 'propertyId': '93768415-741d-4e77-bc87-5c52f02ef29e', 'propertyValues': [{'value': {'doubleValue': 5.9}, 'timestamp': {'timeInSeconds': 1671137565}}]}, {'entryId': 'VibrationL-Friction', 'assetId': 'b50a2f9f-e2d6-42c1-97b2-591169a4f270', 'propertyId': '48dd8aaf-a2b5-48a8-ad32-3b449933cb71', 'propertyValues': [{'value': {'doubleValue': 7.9}, 'timestamp': {'timeInSeconds': 1671137565}}]}, {'entryId': 'VibrationL-Impact', 'assetId': 'b50a2f9f-e2d6-42c1-97b2-591169a4f270', 'propertyId': '98d359c5-bde1-4077-a7bd-f3e809a7f22b', 'propertyValues': [{'value': {'doubleValue': 22.200000000000003}, 'timestamp': {'timeInSeconds': 1671137565}}]}, {'entryId': 'VibrationL-Temperature', 'assetId': 'b50a2f9f-e2d6-42c1-97b2-591169a4f270', 'propertyId': 'e3f1c4e0-a05c-4652-b640-7e3402e8d6a1', 'propertyValues': [{'value': {'doubleValue': 25.8}, 'timestamp': {'timeInSeconds': 1671137565}}]}, {'entryId': 'VibrationR-Crest', 'assetId': 'b50a2f9f-e2d6-42c1-97b2-591169a4f270', 'propertyId': 'f15f4954-2219-4e28-8930-0758d807c259', 'propertyValues': [{'value': {'doubleValue': 39.0}, 'timestamp': {'timeInSeconds': 1671137565}}]}, {'entryId': 'VibrationR-Fatigue', 'assetId': 'b50a2f9f-e2d6-42c1-97b2-591169a4f270', 'propertyId': '74f6e25e-f8c9-4248-9daf-dacc4ec82e9e', 'propertyValues': [{'value': {'doubleValue': 4.1000000000000005}, 'timestamp': {'timeInSeconds': 1671137565}}]}, {'entryId': 'VibrationR-Friction', 'assetId': 'b50a2f9f-e2d6-42c1-97b2-591169a4f270', 'propertyId': 'd37f29a9-99de-429a-9c7e-b73dacf4b4b4', 'propertyValues': [{'value': {'doubleValue': 4.4}, 'timestamp': {'timeInSeconds': 1671137565}}]}, {'entryId': 'VibrationR-Impact', 'assetId': 'b50a2f9f-e2d6-42c1-97b2-591169a4f270', 'propertyId': '3c2617a3-dfb4-48ba-b2fe-79bccbddcf2d', 'propertyValues': [{'value': {'doubleValue': 17.1}, 'timestamp': {'timeInSeconds': 1671137565}}]}, {'entryId': 'VibrationR-Temperature', 'assetId': 'b50a2f9f-e2d6-42c1-97b2-591169a4f270', 'propertyId': 'b9554855-b50f-4b56-a5f2-572fbd1a8967', 'propertyValues': [{'value': {'doubleValue': 35.6}, 'timestamp': {'timeInSeconds': 1671137565}}]}]
Vibration PUT API response=200
Speed/Photo request=[{'entryId': 'Photo-Bag_Detected', 'assetId': 'b50a2f9f-e2d6-42c1-97b2-591169a4f270', 'propertyId': '5b586474-7bff-4549-89e3-d07a858c6f2b', 'propertyValues': [{'value': {'booleanValue': True}, 'timestamp': {'timeInSeconds': 1671137565}}]}, {'entryId': 'Photo-Distance', 'assetId': 'b50a2f9f-e2d6-42c1-97b2-591169a4f270', 'propertyId': '4b4fa2a4-90cc-47ec-b06e-47837d05bf84', 'propertyValues': [{'value': {'doubleValue': 52.0}, 'timestamp': {'timeInSeconds': 1671137565}}]}, {'entryId': 'Speed-PDV1', 'assetId': 'b50a2f9f-e2d6-42c1-97b2-591169a4f270', 'propertyId': 'd17d07c7-442d-4897-911b-4b267519ae3d', 'propertyValues': [{'value': {'doubleValue': 31.5}, 'timestamp': {'timeInSeconds': 1671137565}}]}]
Speed/Photo PUT API response=200
...
```
3. You can go to the AWS Console in IoT SiteWise and verify that data is arriving to the service by looking at the Asset,on the Measurements tab, verifying the timestamp on the ***Latest value timestamp*** column.
![Get Model ID](/images/data-arrival.png)

**NOTE**: When you execute the script from a Cloud9 environment and leave it running for a while it is very likely that it will fail on its own at a later time, since the AWS Cloud9 default profile uses temporarily credentials for authorizing API calls to AWS; therefore when they expire the script fails to authorize the AWS IoT SiteWise API calls. To avoid this problem, please take a look at the [this article](https://docs.aws.amazon.com/cloud9/latest/user-guide/credentials.html) for solutions on how to preserve the authentication for a longer period of time.
