import json
import time
import os
import logging
import boto3
import re
import datetime

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


# --- Helpers that build all of the responses ---

def get_slots(intent_request):
    return intent_request['sessionState']['intent']['slots']

def get_session_attributes(intent_request):
    sessionState = intent_request['sessionState']
    if 'sessionAttributes' in sessionState:
        return sessionState['sessionAttributes']
    return {}

def get_slot(intent_request, slotName):
    slots = get_slots(intent_request)
    if slots is not None and slotName in slots and slots[slotName] is not None:
        logger.debug('resolvedValue={}'.format(slots[slotName]['value']['resolvedValues']))
        return slots[slotName]['value']['interpretedValue']
    else:
        return None

def elicit_slot(session_attributes, intent_request, slots, slot_to_elicit, slot_elicitation_style, message):
    return {'sessionState': {'dialogAction': {'type': 'ElicitSlot',
                                              'slotToElicit': slot_to_elicit,
                                              'slotElicitationStyle': slot_elicitation_style
                                              },
                             'intent': {'name': intent_request['sessionState']['intent']['name'],
                                        'slots': slots,
                                        'state': 'InProgress'
                                        },
                             'sessionAttributes': session_attributes,
                             'originatingRequestId': '2d3558dc-780b-422f-b9ec-7f6a1bd63f2e'
                             },
            'sessionId': intent_request['sessionId'],
            'messages': [ message ],
            'requestAttributes': intent_request['requestAttributes']
            if 'requestAttributes' in intent_request else None
            }

def build_validation_result(isvalid, violated_slot, slot_elicitation_style, message_content):
    return {'isValid': isvalid,
            'violatedSlot': violated_slot,
            'slotElicitationStyle': slot_elicitation_style,
            'message': {'contentType': 'PlainText', 
            'content': message_content}
            }

def validate_reservation(intent_request):
    
    date = get_slot(intent_request, 'date')
    time = get_slot(intent_request, 'time')
    email = get_slot(intent_request, 'Email')
    cuisine = get_slot(intent_request, 'cuisine')
    people = get_slot(intent_request, 'people')
    location = get_slot(intent_request, 'Location')
    
    
    valid_cities = ['new york', 'manhattan']
    if location and location.lower() not in valid_cities:
        return build_validation_result(False, 'Location', 'SpellByWord', 'Location is not valid in other city. Please enter a location in New York')
    
    
    cuisines = ['chinese', 'italian', 'indian','mexican','american','sushi']
    if cuisine and cuisine.lower() not in cuisines:
        return build_validation_result(False,
                                       'cuisine',
                                       'SpellByWord',
                                       'This cuisine is not available') 
    
    if date:
        year, month, day = map(int, date.split('-'))
        date_to_check = datetime.date(year, month, day)
        if date_to_check < datetime.date.today():
            return build_validation_result(False,'date', 'SpellByWord','Please enter a valid Dining date')
        
        
    if time:
        year, month, day = map(int, date.split('-'))
        date_to_check = datetime.date(year, month, day)
        if date_to_check == datetime.date.today():
            current_datetime = datetime.datetime.now()
            input_datetime = datetime.datetime.combine(current_datetime.date(), datetime.datetime.strptime(time, '%H:%M').time())
            if input_datetime < current_datetime:
                return build_validation_result(False,'time', 'SpellByWord','Please enter a valid Dining Time')
    
    if people:
        if int(people)<0 or int(people)>20:
            return build_validation_result(False,
                                  'people',
                                  'SpellByWord',
                                  'Range of 1 to 20 people allowed') 
        
    if email:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return build_validation_result(False, 'Email', 'SpellByWord', 'Your email address is invalid')
    
    
    return {'isValid': True}


def make_restaurant_reservation(intent_request):
    """
    Performs dialog management and fulfillment for checking an account
    with a postal code. Besides fulfillment, the implementation for this 
    intent demonstrates the following:
    1) Use of elicitSlot in slot validation and re-prompting.
    2) Use of sessionAttributes to pass information that can be used to
        guide a conversation.
    """
    print("Debug: Entered make_restaurant_reservation" )
    slots = get_slots(intent_request)
    date = get_slot(intent_request, 'date')
    time = get_slot(intent_request, 'time')
    email = get_slot(intent_request, 'Email')
    cuisine = get_slot(intent_request, 'cuisine')
    people = get_slot(intent_request, 'people')
    location = get_slot(intent_request, 'Location')
    
    session_attributes = get_session_attributes(intent_request)
    
    
    
    if intent_request['invocationSource'] == 'DialogCodeHook':
        # Validate the slots. If any aren't valid, 
        # re-elicit for the value.
        validation_result = validate_reservation(intent_request)
        print("Debug: Validation result is: ", validation_result)
        if not validation_result['isValid']:
            slots[validation_result['violatedSlot']] = None
            
            return elicit_slot(
                session_attributes,
                intent_request,
                slots,
                validation_result['violatedSlot'],
                validation_result['slotElicitationStyle'],
                validation_result['message']
            )
        
    
    print(slots)
    if not location or not date or not time or not people or not email or not cuisine:
        return delegate(intent_request, slots)
    
    else:
        #sqs 
        sqs_client = boto3.client('sqs')
        queue_url = "https://sqs.us-east-1.amazonaws.com/200667660421/DiningQueue"
        
        response = sqs_client.send_message(
            QueueUrl=queue_url,
            MessageAttributes={
                    'Location': {
                        'DataType': 'String',
                        'StringValue': location
                    },
                    'Cuisine': {
                        'DataType': 'String',
                        'StringValue': cuisine
                    },
                    'People': {
                        'DataType': 'Number',
                        'StringValue': str(people)
                    },
                    'Date': {
                        'DataType': 'String',
                        'StringValue': date
                    },
                    'Time': {
                        'DataType': 'String',
                        'StringValue': time
                    },
                    'Email': {
                        'DataType': 'String',
                        'StringValue': email
                    }
                },
            MessageBody=('Information about user inputs of Dining Chatbot.'),
            )
        
        print("response", response)
        
        return close(
            intent_request,
            session_attributes,
            'Fulfilled',
            {'contentType': 'PlainText',
             'content': 'I have received your request and will be sending the suggestions shortly. Have a Great Day !!'
             }
        )
        
def delegate(intent_request, slots):
    return {
    "sessionState": {
        "dialogAction": {
            "type": "Delegate"
        },
        "intent": {
            "name": intent_request['sessionState']['intent']['name'],
            "slots": slots,
            "state": "ReadyForFulfillment"
        },
        'sessionId': intent_request['sessionId'],
        "requestAttributes": intent_request['requestAttributes'] if 'requestAttributes' in intent_request else None
    }
}
    
def close(intent_request, session_attributes, fulfillment_state, message):
    intent_request['sessionState']['intent']['state'] = fulfillment_state
    return {
        'sessionState': {
            'sessionAttributes': session_attributes,
            'dialogAction': {
                'type': 'Close'
            },
            'intent': intent_request['sessionState']['intent'],
            'originatingRequestId': '2d3558dc-780b-422f-b9ec-7f6a1bd63f2e'
        },
        'messages': [ message ],
        'sessionId': intent_request['sessionId'],
        'requestAttributes': intent_request['requestAttributes'] if 'requestAttributes' in intent_request else None
    }

# --- Intents ---

def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """
    intent_name = intent_request['sessionState']['intent']['name']
    response = None

    # Dispatch to your bot's intent handlers
    if intent_name == 'DiningSuggestionsIntent':
        response = make_restaurant_reservation(intent_request)

    return response

# --- Main handler ---

def lambda_handler(event, context):
    """
    Route the incoming request based on the intent.

    The JSON body of the request is provided in the event slot.
    """

    # By default, treat the user request as coming from 
    # Eastern Standard Time.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    
    logger.debug('event={}'.format(json.dumps(event)))
    response = dispatch(event)
    logger.debug("response={}".format(json.dumps(response)))
    
    return response