'''
    delete every webex message in the target room from IDs stored into messages_id_to_delete.txt
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
    
    
def delete_messages(webextoken, webexspaceid,messageId):
    headers = {'Authorization': 'Bearer ' + webextoken, 'content-type': 'application/json; charset=utf-8'}
    url=f'https://webexapis.com/v1/messages/{messageId}'
    result = requests.delete(url, headers=headers)
    print(result)
    if result.status_code==204:
        print(green('Message Succesfuly Deleted',bold=True))
    else:
        print(red('Error, message not Deleted',bold=True))
    return

def main(webextoken, webexspaceid):
    with open('messages_id_to_delete.txt','r') as file:
        for id in file:
            messageId=id.replace('\n','')
            print('Deleting message : ',id)
            delete_messages(webextoken, webexspaceid,messageId)

if __name__ == "__main__":
    with open('config.txt','r') as file:
        text_content=file.read()
    ctr_client_id,ctr_client_password,host,SecureX_Webhook_url,myRoom,myToken,host_for_token = parse_config(text_content)
    print()
    print('BOT_ACCESS_TOKEN : ',myToken)
    print('DESTINATION_ROOM_ID : ',myRoom)
    print()
    print("\n\n--------------------DELETING MESSAGES----------------------------\n ")
    main(myToken,myRoom)
