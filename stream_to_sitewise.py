#!/user/bin/env python
"""
This is part of the AWS Blog Creating OEE Dashboard for AWS IoT SiteWise article.  
Stream data into AWS IoT SiteWise from sample sensor data collected from a Bag Handling System (BHS)
"""

# Copyright Amazon.com, Inc. and its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT

########################################################################################################################
# Documentation
########################################################################################################################

# See the README.md file.



########################################################################################################################
# Imports
########################################################################################################################

import os
import sys
import json
import time
from datetime import datetime, timedelta
try:
    import pandas as pd
    import boto3
    import numpy as np
except ImportError as err:
    print(err)
    print("Please install the required module (ex: 'pip install <package>').")
    exit()

########################################################################################################################
# Confirm required Python version.
########################################################################################################################

if sys.version_info < (3, 7):
  print("Detected Python version ", sys.version_info.major, ".", sys.version_info.minor, sep='', end='')
  print(", but this script requires Python 3.7+. Aborting.")
  exit()


########################################################################################################################
# Main Script
########################################################################################################################

def main():

    #Stream data for April 2022
    local_directory = os.getcwd() + '/2022_april'
    boto3.setup_default_session(profile_name='default')
    session = boto3.session.Session()
    region = session.region_name
    iotSiteWiseClient = boto3.client(
                    'iotsitewise',
                    region_name= region
                )
    #Batch PUT API is allowed on max 10 properties per call, need two templates to split the data, first template is for the Vibration sensors data and the second for both photo-electric and speed sensors
    vibrationTemplateFile = 'carousel-vibration-template.json'
    speedPhotoTemplateFile = 'carousel-speed-photo-template.json'
    vfile = open(vibrationTemplateFile)
    vibrationData = json.load(vfile)
    spfile = open(speedPhotoTemplateFile)
    speedPhotoData = json.load(spfile)

    for day in range(1,31):
        for hour in range(24):
            dfSpeed = pd.read_pickle("{}/{}_{}_speed.pickle".format(local_directory,day,hour))
            dfVR = pd.read_pickle("{}/{}_{}_vibrationR.pickle".format(local_directory,day,hour))
            dfVL = pd.read_pickle("{}/{}_{}_vibrationL.pickle".format(local_directory,day,hour))
            dfPhoto = pd.read_pickle("{}/{}_{}_photo.pickle".format(local_directory,day,hour))
            #All Dataframes have the same length now
            interval_in_sec = 3600/dfVL.index.size
            #Not keeping historical data, assume that data is coming live from the sensors as it is read at 1 hour intervals
            timeStamp = datetime.now()
            print("Streaming data for Day {}, Hour {}".format(day,hour))
            for element in dfPhoto.index:
                #need to handle empty dataframes
                if dfVL.loc[element].get('Crest'):
                    vibrationData['entries'][0]['propertyValues'][0]['value']['doubleValue'] = float(dfVL.loc[element].get('Crest'))
                if dfVL.loc[element].get('Fatigue'):
                    vibrationData['entries'][1]['propertyValues'][0]['value']['doubleValue'] = float(dfVL.loc[element].get('Fatigue'))
                if dfVL.loc[element].get('Friction'):
                    vibrationData['entries'][2]['propertyValues'][0]['value']['doubleValue'] = float(dfVL.loc[element].get('Friction'))
                if dfVL.loc[element].get('Impact'):
                    vibrationData['entries'][3]['propertyValues'][0]['value']['doubleValue'] = float(dfVL.loc[element].get('Impact'))
                if dfVL.loc[element].get('Temperature'):
                    vibrationData['entries'][4]['propertyValues'][0]['value']['doubleValue'] = float(dfVL.loc[element].get('Temperature'))
                if dfVR.loc[element].get('Crest'):
                    vibrationData['entries'][5]['propertyValues'][0]['value']['doubleValue'] = float(dfVR.loc[element].get('Crest'))
                if dfVR.loc[element].get('Fatigue'):
                    vibrationData['entries'][6]['propertyValues'][0]['value']['doubleValue'] = float(dfVR.loc[element].get('Fatigue'))
                if dfVR.loc[element].get('Friction'):
                    vibrationData['entries'][7]['propertyValues'][0]['value']['doubleValue'] = float(dfVR.loc[element].get('Friction'))
                if dfVR.loc[element].get('Impact'):
                    vibrationData['entries'][8]['propertyValues'][0]['value']['doubleValue'] = float(dfVR.loc[element].get('Impact'))
                if dfVR.loc[element].get('Temperature'):
                    vibrationData['entries'][9]['propertyValues'][0]['value']['doubleValue'] = float(dfVR.loc[element].get('Temperature'))
                if dfPhoto.loc[element].get('Bag_Detected'):
                    #need extra check for non values used on aproximation to Photo Electric sensor
                    if np.isnan(dfPhoto.loc[element].get('Bag_Detected')):
                        speedPhotoData['entries'][0]['propertyValues'][0]['value']['booleanValue'] = False
                    else:
                        speedPhotoData['entries'][0]['propertyValues'][0]['value']['booleanValue'] = bool(dfPhoto.loc[element].get('Bag_Detected'))
                if dfPhoto.loc[element].get('Distance'):
                    #need extra check for non values used on aproximation to Photo Electric sensor
                    if np.isnan(dfPhoto.loc[element].get('Distance')):
                        speedPhotoData['entries'][1]['propertyValues'][0]['value']['doubleValue'] = 108
                    else:
                        speedPhotoData['entries'][1]['propertyValues'][0]['value']['doubleValue'] = float(dfPhoto.loc[element].get('Distance'))
                if dfSpeed.loc[element].get('PDV1'):
                    speedPhotoData['entries'][2]['propertyValues'][0]['value']['doubleValue'] = float(dfSpeed.loc[element].get('PDV1'))
                #Fix timestamps before sending data
                #AWS IoT SiteWise rejects any data with a timestamp dated to more than 7 days in the past or more than 10 minutes in the future.
                #Data is streamed as if it was current, this is done for testing purposes, in order to geenrate data that is accepted by IoT SiteWise
                epoch_time = int(timeStamp.timestamp())
                entriesVibration = vibrationData['entries']
                for entry in entriesVibration:
                    entry['propertyValues'][0]['timestamp']['timeInSeconds'] =  epoch_time
                entriesSpeedPhoto = speedPhotoData['entries']
                for entry in entriesSpeedPhoto:
                    entry['propertyValues'][0]['timestamp']['timeInSeconds'] =  epoch_time
                #Upload Data to IoT SiteWise
                print("Vibration request={}".format(entriesVibration))
                response = iotSiteWiseClient.batch_put_asset_property_value(
                    entries =  entriesVibration   
                )
                print("Vibration PUT API response={}".format(response['ResponseMetadata']['HTTPStatusCode']))
                print("Speed/Photo request={}".format(entriesSpeedPhoto))
                response = iotSiteWiseClient.batch_put_asset_property_value(
                    entries =  entriesSpeedPhoto   
                )
                print("Speed/Photo PUT API response={}".format(response['ResponseMetadata']['HTTPStatusCode']))
                #Get Ready for next cycle
                timeStamp = timeStamp + timedelta(seconds=interval_in_sec)
                print('...')
                time.sleep(interval_in_sec)

########################################################################################################################
# See: https://docs.python.org/3/library/__main__.html#idiomatic-usage
########################################################################################################################

if __name__ == '__main__':
  sys.exit(main())