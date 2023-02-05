# -*- coding: utf-8 -*-

# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Amazon Software License (the "License"). You may not use this file except in
# compliance with the License. A copy of the License is located at
#
#    http://aws.amazon.com/asl/
#
# or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific
# language governing permissions and limitations under the License.

import boto3
import json
import time
from alexa.skills.smarthome import AlexaResponse
import itertools


def lambda_handler(request, context):

    # Dump the request for logging - check the CloudWatch logs
    print('lambda_handler request  -----')
    print(json.dumps(request))

    if context is not None:
        print('lambda_handler context  -----')
        print(context)

    # Validate we have an Alexa directive
    if 'directive' not in request:
        aer = AlexaResponse(
            name='ErrorResponse',
            payload={'type': 'INVALID_DIRECTIVE',
                     'message': 'Missing key: directive, Is the request a valid Alexa Directive?'})
        return send_response(aer.get())

    # Check the payload version
    payload_version = request['directive']['header']['payloadVersion']
    if payload_version != '3':
        aer = AlexaResponse(
            name='ErrorResponse',
            payload={'type': 'INTERNAL_ERROR',
                     'message': 'This skill only supports Smart Home API version 3'})
        return send_response(aer.get())

    # Crack open the request and see what is being requested
    name = request['directive']['header']['name']
    namespace = request['directive']['header']['namespace']

    # Handle the incoming request from Alexa based on the namespace

    if namespace == 'Alexa.Authorization':
        if name == 'AcceptGrant':
            # Note: This sample accepts any grant request
            # In your implementation you would use the code and token to get and store access tokens
            grant_code = request['directive']['payload']['grant']['code']
            grantee_token = request['directive']['payload']['grantee']['token']
            aar = AlexaResponse(namespace='Alexa.Authorization', name='AcceptGrant.Response')
            return send_response(aar.get())

    if namespace == 'Alexa.Discovery':
        response = AlexaResponse(namespace='Alexa.Discovery', name='Discover.Response')

        # Load any capability definitions (e.g., PowerController, ModeController, ToggleController, etc)
        capabilities = []

        ## PowerController
        range_controller_capabilities = load_capability_definition("RangeController")
        capabilities.append(range_controller_capabilities)

        # Flatten capabilities into a single list
        capabilities = list(itertools.chain.from_iterable(capabilities))
        
        # Add the base Alexa interface
        base_interface = {
          "type": "AlexaInterface",
          "interface": "Alexa",
          "version": "3"
        }
        capabilities.append(base_interface)

        response.add_payload_endpoint(
            endpoint_id='AC', 
            friendly_name='Air Condition', 
            capabilities=capabilities
        )
        
        response = response.get()
        return send_response(response)
            

    # if namespace == 'Alexa.PowerController':
    #     # Note: This sample always returns a success response for either a request to TurnOff or TurnOn
    #     endpoint_id = request['directive']['endpoint']['endpointId']
    #     power_state_value = 'OFF' if name == 'TurnOff' else 'ON'
    #     correlation_token = request['directive']['header']['correlationToken']
    #     bearer_token = request['directive']['endpoint']['scope']['token']

    #     # Check for an error when setting the state
    #     state_set = set_device_state(endpoint_id + '_PWR_SET', value=power_state_value)
    #     if not state_set:
    #         return AlexaResponse(
    #             name='ErrorResponse',
    #             payload={'type': 'ENDPOINT_UNREACHABLE', 'message': 'Unable to reach endpoint database.'}).get()

    #     apcr = AlexaResponse(namespace='Alexa', name='Response', correlation_token=correlation_token, endpoint_id=endpoint_id, token=bearer_token)
    #     apcr.add_context_property(namespace='Alexa.PowerController', name='powerState', value=power_state_value)
    #     return send_response(apcr.get())
        

    # if namespace == 'Alexa.RangeController':
    #     print('Range Controller related is triggered')
        
    #     max_air_temp = 30
    #     min_air_temp = 17
        
    #     max_air_fan = 7
    #     min_air_fan = 1

    #     endpoint_id = request['directive']['endpoint']['endpointId']
    #     instance = request['directive']['header']['instance']
    #     correlation_token = request['directive']['header']['correlationToken']
    #     bearer_token = request['directive']['endpoint']['scope']['token']
    #     name = request['directive']['header']['name']
        
    
    #     if instance == 'Temperature':
    #         endpoint_id = endpoint_id + '_TEMP_SET'
    #     elif instance == 'Fan.Speed':
    #         endpoint_id = endpoint_id + '_FAN_SET'
    #     else:
    #         return AlexaResponse(
    #             name='ErrorResponse',
    #             payload={'type': 'INVALID_REQUEST_EXCEPTION', 'message': 'Instance is not valid'}).get()
        
        
        
    #     apcr = AlexaResponse(namespace='Alexa', name='Response', correlation_token=correlation_token, endpoint_id=endpoint_id, token=bearer_token)
                    
    #     if name == 'AdjustRangeValue':
    #         range_value_delta = request['directive']['payload']['rangeValueDelta']
    #         current_value = int(float(get_device_state(endpoint_id)))
    #         desired_value = 0
    #         if instance == 'Temperature':
    #             if current_value + range_value_delta >= min_air_temp and current_value + range_value_delta <= max_air_temp:
    #                 desired_value = current_value + range_value_delta
    #             elif current_value + range_value_delta < min_air_temp:
    #                 desired_value = min_air_temp
    #             elif current_value + range_value_delta > max_air_temp:
    #                 desired_value = max_air_temp
    #         elif instance == 'Fan.Speed':
    #             if current_value + range_value_delta >= min_air_fan and current_value + range_value_delta <= max_air_fan:
    #                 desired_value = current_value + range_value_delta
    #             elif current_value + range_value_delta < min_air_fan:
    #                 desired_value = min_air_fan
    #             elif current_value + range_value_delta > max_air_fan:
    #                 desired_value = max_air_fan
    #         state_set = set_device_state(endpoint_id, str(int(desired_value)))
    #         if not state_set:
    #             return AlexaResponse(
    #                 name='ErrorResponse',
    #                 payload={'type': 'ENDPOINT_UNREACHABLE', 'message': 'Unable to reach endpoint database.'}).get()
    #         apcr.add_context_property(namespace='Alexa.RangeController', name='rangeValue', value=desired_value, instance=instance)

            
    #     elif name == 'SetRangeValue':
    #         range_value = int(request['directive']['payload']['rangeValue'])
    #         state_set = set_device_state(endpoint_id, value=str(range_value))
    #         if not state_set:
    #             return AlexaResponse(
    #                 name='ErrorResponse',
    #                 payload={'type': 'ENDPOINT_UNREACHABLE', 'message': 'Unable to reach endpoint database.'}).get()
    
    #         apcr.add_context_property(namespace='Alexa.RangeController', name='rangeValue', value=range_value, instance=instance)
            
    #     return send_response(apcr.get())


def send_response(response):
    # TODO Validate the response
    print('lambda_handler response -----')
    print(json.dumps(response))
    return response

# aws_dynamodb = boto3.client('dynamodb', region_name='ap-northeast-1')

# def get_device_state(endpoint_id):
#     response = aws_dynamodb.get_item(
#         TableName='byd_demo_tsp_db',
#         Key={'vin': {'S': '1G1AF1F57A7192174'}},
#         AttributesToGet=[endpoint_id],
#         ConsistentRead=True
#         )
#     return list(response['Item'][endpoint_id].values())[0]


# def set_device_state(endpoint_id, value):
    
#     response = aws_dynamodb.update_item(
#         TableName='byd_demo_tsp_db',
#         Key={'vin': {'S': '1G1AF1F57A7192174'}},
#         ExpressionAttributeValues={
#             ':r': {"S":value},
#             ':t': {"S":str(int(round(time.time() * 1000)))}
            
#         },
#         UpdateExpression="set " + endpoint_id + " = :r, " + 'TS = :t'  )
#     print(response)
#     if response['ResponseMetadata']['HTTPStatusCode'] == 200:
#         return True
#     else:
#         return False


def load_capability_definition(capability):
    with open(f'./capabilities/{capability}.json') as f:
        controller = json.load(f)

    capabilities = []

    if isinstance(controller, dict):
        capabilities.append(controller)
    elif isinstance(controller, list):
        for i in range(len(controller)):
            capabilities.append(controller[i])

    return capabilities