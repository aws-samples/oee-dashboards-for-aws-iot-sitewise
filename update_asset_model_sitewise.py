import boto3
import json
import argparse

parser = argparse.ArgumentParser(description="Update IoT SiteWise Model",
                                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-p","--profile",help="Name of access profile", default= "default")
parser.add_argument("-a","--assetModelId", help="Asset Model ID")
parser.add_argument("-f","--property_file", help="JSON Model Property file")
parser.add_argument("-r","--region", help="AWS Region where the model is defined")
args = parser.parse_args()

assetModelId = args.assetModelId
boto3.setup_default_session(profile_name=args.profile)


iotSiteWiseClient = boto3.client(
    'iotsitewise',
    region_name= args.region
)

#Get full model with Describe asset
response = iotSiteWiseClient.describe_asset_model(
    assetModelId= assetModelId
)

asset_model = response

#Load new property file
f = open(args.property_file)
newProperty = json.load(f)

#Append item to properties list
asset_model['assetModelProperties'].append(newProperty)

#Update model
response = iotSiteWiseClient.update_asset_model(
    assetModelId            = asset_model['assetModelId'],
    assetModelName          = asset_model['assetModelName'],
    assetModelProperties    = asset_model['assetModelProperties'],
    assetModelHierarchies   = asset_model['assetModelHierarchies']
)
print(response)