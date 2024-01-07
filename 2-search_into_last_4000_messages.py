'''
    Display the messages which contain the search string and save the message IDs into a file named messages_id.txt.
    The script prompt you for the searched string.
'''
# coding=utf-8
import json
import requests
import time
from crayons import *

myToken = ""
myRoom = ""

# maxMessagesPerRun=400 and maxRuns=10 ---> will retrieve a maximum of 10*400 = 4,000 messages
# Do not set maxMessagesPerRun > 500
maxMessagesPerRun = 400     # number of messages retrieved per batch
maxRuns = 10                # the number of runs
maxWaitTime = 5             # Number of seconds before starting the next batch

def parse_config(text_content):
    text_lines=text_content.split('\n')
    conf_result=['','','','','','','']
    for line in text_lines:
        print(green(line,bold=True))
        if 'ctr_client_id' in line:
            words=line.split('=')
            if len(words)==2:
                conf_result[0]=line.split('=')[1]
                conf_result[0]=conf_result[0].replace('"','')
                conf_result[0]=conf_result[0].replace("'","")
            else:
                conf_result[0]=""
        elif 'ctr_client_password' in line:
            words=line.split('=')
            if len(words)==2:
                conf_result[1]=line.split('=')[1]
                conf_result[1]=conf_result[1].replace('"','')
                conf_result[1]=conf_result[1].replace("'","")
            else:
                conf_result[1]=""        
        elif '.eu.amp.cisco.com' in line:
            conf_result[2]="EU" 
            conf_result[2]=conf_result[2].replace('"','')
            conf_result[2]=conf_result[2].replace("'","")  
            conf_result[6]="https://visibility.eu.amp.cisco.com"
        elif '.intel.amp.cisco.com' in line:
            conf_result[2]="US"  
            conf_result[2]=conf_result[2].replace('"','')
            conf_result[2]=conf_result[2].replace("'","")  
            conf_result[6]="https://visibility.amp.cisco.com"
        elif '.apjc.amp.cisco.com' in line:
            conf_result[2]="APJC"
            conf_result[2]=conf_result[2].replace('"','')
            conf_result[2]=conf_result[2].replace("'","") 
            conf_result[6]="https://visibility.apjc.amp.cisco.com"
        elif 'SecureX_Webhook_url' in line:
            words=line.split('=')
            if len(words)==2:        
                print(yellow(words))        
                conf_result[3]=words[1]
                conf_result[3]=conf_result[3].replace('"','')
                conf_result[3]=conf_result[3].replace("'","")                
            else:
                conf_result[3]=""
        elif 'webex_bot_token' in line:
            words=line.split('=')
            if len(words)==2:
                conf_result[5]=line.split('=')[1]
                conf_result[5]=conf_result[5].replace('"','')
                conf_result[5]=conf_result[5].replace("'","")
            else:
                conf_result[5]=""        
        elif 'webex_room_id' in line:
            words=line.split('=')
            if len(words)==2:
                conf_result[4]=line.split('=')[1]
                conf_result[4]=conf_result[4].replace('"','')
                conf_result[4]=conf_result[4].replace("'","")
            else:
                conf_result[4]=""        
    print(yellow(conf_result))
    return conf_result
    
def get_messages(webextoken, webexspaceid):
    headers = {'Authorization': 'Bearer ' + webextoken, 'content-type': 'application/json; charset=utf-8'}
    payload = {'roomId': webexspaceid, 'max': maxMessagesPerRun}
    JSONdata = list()   # all message (dictionaries) are stored in a list:
    currentRun = 0
    while currentRun < maxRuns:  # for each batch of messages to be retrieved:
        currentRun += 1
        try:    # Get Spark messages (with 'max' set to the variable 'maxMessagesPerRun' (per batch))
            result = requests.get('https://webexapis.com/v1/messages', headers=headers, params=payload)
        except requests.exceptions.RequestException as e:
            print(" **  WARNING: An error occurred " + e)
            break
        try:
            # Add new messages to the JSON list:
            JSONdata.extend(json.loads(result.text)['items'])

            # Get the oldest message ID of this run. This is where we start our next run.
            myBeforeMessage = result.headers.get('Link').split("beforeMessage=")[1].split(">")[0]

            # Change the Spark GET request message to include the (updated) last message ID:
            payload = {'roomId': webexspaceid, 'max': maxMessagesPerRun, 'beforeMessage': myBeforeMessage}

            # Print the progress:
            print(" run: " + str(currentRun) + " --- total number of retrieved messages: " + str(len(JSONdata)))

            # Wait x number of seconds before retrieving more messages
            print("             ... waiting " + str(maxWaitTime) + " seconds before next API call ... \n")
            time.sleep(maxWaitTime)
        except:
            break
    return JSONdata

if __name__ == "__main__":
    with open('config.txt','r') as file:
        text_content=file.read()
    ctr_client_id,ctr_client_password,host,SecureX_Webhook_url,myRoom,myToken,host_for_token = parse_config(text_content)
    print()
    print('BOT_ACCESS_TOKEN : ',myToken)
    print('DESTINATION_ROOM_ID : ',myRoom)
    print()
    searched_text=input('Text to Search into text messages : ')
    print("\n\n --------------------READING MESSAGES----------------------------\n ")

    WebexMessages = get_messages(myToken, myRoom)
    #print(WebexMessages)

    print("\nNumber of messages retrieved: " + str(len(WebexMessages)))

    print("\n\n -------------------------------------------------------\n\n ")

    with open('messages_id.txt','w') as file:
        for msg in WebexMessages:
            if 'personEmail' in msg and searched_text in msg['text'] :  
                print(yellow("Message from > " + str(msg['personEmail']) + "  -- created: " + msg['created'],bold=True))
                print()
                print(cyan(msg['text'],bold=True))
                line_out=msg['id']+'\n'
                file.write(line_out)
    print("\n -------------------- finished ----------------------------\n\n ")
