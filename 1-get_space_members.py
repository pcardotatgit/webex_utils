import requests
from crayons import *
mytoken =""
myroom = ""
maxmembers =800
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
# FUNCTION that retrieves a list of Space members (displayName + email address)
def get_memberships(mytoken, myroom, maxmembers):
    headers = {'Authorization': 'Bearer ' + mytoken, 'content-type': 'application/json; charset=utf-8'}
    payload = {'roomId': myroom, 'max': maxmembers}
    resultjson = list()
    while True:
        try:
            result = requests.get('https://webexapis.com/v1/memberships', headers=headers, params=payload)
            if "Link" in result.headers:  # there's MORE members
                headerLink = result.headers["Link"]
                myCursor = headerLink[headerLink.find("cursor=") + len("cursor="):headerLink.rfind("==>")]
                payload = {'roomId': myroom, 'max': maxmembers, 'cursor': myCursor}
                resultjson += result.json()["items"]
                continue
            else:
                resultjson += result.json()["items"]
                print(f"          Number of space members: {len(resultjson)}")
                print()
                #print(resultjson)
                with open('member_mails.txt','w') as file:
                    for item in resultjson:
                        print(yellow(item['personEmail'],bold=True))
                        file.write(item['personEmail']+'\n')
                with open('members.txt','w',encoding='utf-8') as file:
                    for item in resultjson:
                        print(cyan(item['personDisplayName'],bold=True))
                        file.write(item['personEmail']+';'+item['personDisplayName']+'\n')                            
                break
        except requests.exceptions.RequestException as e:  # For problems like SSLError/InvalidURL
            if e.status_code == 429:
                print("          Code 429, waiting for : " + str(sleepTime) + " seconds: ", end='', flush=True)
                for x in range(0, sleepTime):
                    time.sleep(1)
                    print(".", end='', flush=True)  # Progress indicator
            else:
                print(" *** ERROR *** getting space members. Error message: {result.status_code}\n {e}")
                break
    return resultjson
    
if __name__=="__main__":
    with open('config.txt','r') as file:
        text_content=file.read()
    ctr_client_id,ctr_client_password,host,SecureX_Webhook_url,myRoom,myToken,host_for_token = parse_config(text_content)
    print()
    print('BOT_ACCESS_TOKEN : ',myToken)
    print('DESTINATION_ROOM_ID : ',myRoom)
    print()
    get_memberships(myToken, myRoom, maxmembers)
    