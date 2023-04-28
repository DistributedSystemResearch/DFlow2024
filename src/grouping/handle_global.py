import config
import requests 
import json 

def SendGloablInput(global_input):
    #global_input是dict格式,要转为json 
    global_input = json.dumps(global_input) #转为json
    for ip in config.WORK_NODES:
        remote_url = ip
        response = requests.post(remote_url, json=global_input) 
        response.close() 
