from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import paho.mqtt.client as mqtt
import logging
import time
import json
import datetime 
AllowedActions = ['both', 'publish', 'subscribe']

def replyToPing(sequence):
    pingData = {}

    pingData['sequence'] = sequence
    pingData['message'] = "Ping response."

    message = {}
    message['device_mac'] = "D4:25:8B:D9:E7:2F"
    message['timestamp'] = str(datetime.datetime.now())
    message['event_id'] = 1
    message['event'] = pingData
    messageJson = json.dumps(message)
    myAWSIoTMQTTClient.publishAsync("pl19/event", messageJson, 1)

    print(' * Ping answered!')

def sendLog(data, message, event_id, id):
    pingData = {}

    pingData['id'] = id
    pingData['value'] = data
    pingData['message'] = message

    message = {}
    message['device_mac'] = "D4:25:8B:D9:E7:2F"
    message['timestamp'] = str(datetime.datetime.now())
    message['event_id'] = event_id
    message['event'] = pingData
    messageJson = json.dumps(message)
    print("sending log: ")
    print(messageJson)
    myAWSIoTMQTTClient.publishAsync("pl19/event", messageJson, 1)



# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, rc):
    print("Client subscribed!")
    client.subscribe("+/event/+", qos=1)


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print("message received!")    
    if(str(msg.topic[-6:]) == "status"):
        sendLog((msg.payload).decode('utf-8'), "Status changed", 2, str(msg.topic[:15]))
    elif(str(msg.topic[-7:]) == "status"):
        sendLog((msg.payload).decode('utf-8'), "Desired temp changed", 3, str(msg.topic[:15]))
    elif(str(msg.topic[-7:]) == "setname"):
        sendLog((msg.payload).decode('utf-8'), "Room name changed", 4, str(msg.topic[:15]))
    elif(str(msg.topic[-5:]) == "state"):
        sendLog((msg.payload).decode('utf-8'), "ESP state", 5, str(msg.topic[:15]))


        

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("127.0.0.1", 1883)


# Custom MQTT message callback
def customCallback(client, userdata, message):
    messageContent = json.loads(message.payload.decode('utf-8'))
    messageData = messageContent['event']
    if messageContent['event_id'] == 0:
        print("* Received ping!")
        replyToPing(messageData['sequence'])
    else:
        print(json.dumps(messageData))



host = "a3cezb6rg1vyed-ats.iot.us-west-2.amazonaws.com"
rootCAPath = "root-CA.crt"
certificatePath = "PL-student.cert.pem"
privateKeyPath = "PL-student.private.key"
port = 8883
clientId = "pl19-18"
topic = "pl19/event"



# Configure logging
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)

# Init AWSIoTMQTTClient
myAWSIoTMQTTClient = None
myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
myAWSIoTMQTTClient.configureEndpoint(host, port)
myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

myAWSIoTMQTTClient.connect()
myAWSIoTMQTTClient.subscribe("pl19/notification", 1, customCallback)
print(" * Ping subscribed!")


time.sleep(2)

while True:
    time.sleep(5)
