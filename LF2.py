import json
import os
import random
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from boto3.dynamodb.conditions import Key, Attr
from requests_aws4auth import AWS4Auth
from botocore.vendored import requests
from botocore.exceptions import ClientError

REGION = 'us-east-1'
HOST = 'search-restaurants-5kpgambytwibyr5olcotdk2dfm.us-east-1.es.amazonaws.com'
INDEX = 'restaurants'


def lambda_handler(event, context):
    print('Received event: ' + json.dumps(event))
    
    # Grab data from SQS
    sqs = boto3.client('sqs')
    s_queue_s = sqs.get_queue_url(QueueName='DiningQueue')
    queue_url = s_queue_s['QueueUrl']
    response_from_sqs = sqs.receive_message(
        QueueUrl=queue_url,
        AttributeNames=[
            'SentTimestamp'
        ],
        MaxNumberOfMessages=1,
        MessageAttributeNames=[
            'All'
        ],
        VisibilityTimeout=0,
        WaitTimeSeconds=0
    )
    print(response_from_sqs)
    
    
    # if SQS is not empty
    if response_from_sqs:
    
        cuisine = response_from_sqs['Messages'][0]["MessageAttributes"]['Cuisine']["StringValue"]
        date = response_from_sqs['Messages'][0]["MessageAttributes"]['Date']["StringValue"]
        location = response_from_sqs['Messages'][0]["MessageAttributes"]['Location']["StringValue"]
        email = response_from_sqs['Messages'][0]["MessageAttributes"]['Email']["StringValue"]
        people = response_from_sqs['Messages'][0]["MessageAttributes"]['People']["StringValue"]
        time = response_from_sqs['Messages'][0]["MessageAttributes"]['Time']["StringValue"]
        
        
        Business_ID_list = query(cuisine)
       
       
       # DynamoDB part
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('yelp-restaurants')
        recommend_list = []
        for Business_ID in Business_ID_list:
            response_from_DB = table.query(
                KeyConditionExpression=Key('Business_ID').eq(Business_ID)
                )
            
            recommend_restaurant = response_from_DB['Items'][0]["Name"]
            recommend_address = response_from_DB['Items'][0]["Address"]
            recommend_list.append({
                "name": recommend_restaurant,
                "address": recommend_address
            })
        
        
        message_to_user = "Hello! Here are my " + cuisine + " restaurant suggestions for "+ people +" people, for "+date+" at "+time+" : 1. "+recommend_list[0]["name"]+" located at "+ recommend_list[0]["address"]+", 2. "+recommend_list[1]["name"]+" located at "+ recommend_list[1]["address"]+", 3. "+recommend_list[2]["name"]+" located at "+ recommend_list[2]["address"]+". Enjoy your meal!"                               
        
        # SES part
        
        send_email(email, message_to_user)
        
        
        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=response_from_sqs['Messages'][0]['ReceiptHandle']
        )
        
        
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': '*',
            },
            'body': json.dumps({'results': message_to_user})
        }
    else:
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': '*',
            },
            'body': json.dumps("SQS queue is now empty")
        }

def query(term):
    print(term)
    q = {'size': 20, 'query': {'multi_match': {'query': term}}}
    
    client = OpenSearch(hosts=[{
        'host': HOST,
        'port': 443
    }],
                        http_auth=get_awsauth(REGION, 'es'),
                        use_ssl=True,
                        verify_certs=True,
                        connection_class=RequestsHttpConnection)
    
    res = client.search(index=INDEX, body=q)
    hits = res['hits']['hits']
    result = []
    while len(result) !=3:
        index = random.randint(0,19)
        RestaurantID = hits[index]['_source']['RestaurantID']
        if RestaurantID not in result:
            result.append(RestaurantID)
    
    return result


def send_email(email, body_text):
    
    # Replace sender@example.com with your "From" address.
    # This address must be verified with Amazon SES.
    SENDER = "ez2347@columbia.edu"
    
    # Replace recipient@example.com with a "To" address. If your account 
    # is still in the sandbox, this address must be verified.
    RECIPIENT = email
    
    # Specify a configuration set. If you do not want to use a configuration
    # set, comment the following variable, and the 
    # ConfigurationSetName=CONFIGURATION_SET argument below.
    #CONFIGURATION_SET = "ConfigSet"
    
    # If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
    AWS_REGION = "us-east-1"
    
    # The subject line for the email.
    SUBJECT = "Dining Suggestion Based On your Given Information"
    
    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = (body_text)
                
    # The HTML body of the email.
    
    # The character encoding for the email.
    CHARSET = "UTF-8"
    
    # Create a new SES resource and specify a region.
    client = boto3.client('ses',region_name=AWS_REGION)
    
    # Try to send the email.
    try:
        #Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
            # If you are not using a configuration set, comment or delete the
            # following line
            #ConfigurationSetName=CONFIGURATION_SET,
        )
    # Display an error if something goes wrong.	
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
    
    
    
def get_awsauth(region, service):
    cred = boto3.Session().get_credentials()
    return AWS4Auth(cred.access_key,
                    cred.secret_key,
                    region,
                    service,
                    session_token=cred.token)
