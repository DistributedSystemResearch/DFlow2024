from gevent import monkey
monkey.patch_all()
import os
import gevent
import json
from typing import Dict
from threading import Thread
import config
from workersp import WorkerSPManager #note:this is StoneFree 
from mastersp import MasterSPManager
import docker
import subprocess
import logging
import sys
from flask import Flask, request
import multiprocessing
app = Flask(__name__)
docker_client = docker.from_env()
container_names = []
import sys
sys.path.append("..")
from my_log import log

def MyProcessing(remote_url,data):
    response = requests.post(remote_url, json=data) #todo 可能需要异步？

class Dispatcher:
    def __init__(self, data_mode: str, control_mode: str, info_addrs: Dict[str, str]) -> None:
        self.managers = {}
        self.control_node = control_mode #增加自己的控制模式
        #! 12-12,每个workflow一个managers
        log.info('DisPatcher,the info_addrs:%s',info_addrs)
        if control_mode == 'WorkerSP':
            self.managers = {name: WorkerSPManager(sys.argv[1] + ':' + sys.argv[2], name, data_mode, addr) for name, addr in info_addrs.items()}
        elif control_mode == 'MasterSP':
            self.managers = {name: MasterSPManager(sys.argv[1] + ':' + sys.argv[2], name, data_mode, addr) for name, addr in info_addrs.items()} #name对应于workflow_name,addr对应于该workflow的路径
        log.info('Dispatcher,len(self.managers):%s',len(self.managers))
    #! 记录一个函数的state 
    def get_state(self, workflow_name: str, request_id: str) -> WorkerSPManager:
        return self.managers[workflow_name].get_state(request_id) 
   
    def trigger_function(self, workflow_name, state, function_name, no_parent_execution):
        log.info('trigger_function, the self.control_node:%s',self.control_node)
        if self.control_node  == 'WorkerSP':
            self.managers[workflow_name].trigger_function_lambda(state, function_name, no_parent_execution)
        else:
            self.managers[workflow_name].trigger_function(state, function_name, no_parent_execution)
    #def trigger_function_lambda_next(self,workflow_name,)
    def trigger_function_lambda_next(self,workflow_name,state,function_name):
        if self.control_node  == 'WorkerSP':
            self.managers[workflow_name].trigger_function_lambda_next(state,function_name)#需要知道workflow_name
    
    
    def clear_db(self, workflow_name, request_id):
        self.managers[workflow_name].clear_db(request_id)
    
    def del_state(self, workflow_name, request_id, master):
        self.managers[workflow_name].del_state(request_id, master)

print('config.FUNCTION_INFO_ADDRS:',config.FUNCTION_INFO_ADDRS)

dispatcher = Dispatcher(data_mode=config.DATA_MODE, control_mode=config.CONTROL_MODE, info_addrs=config.FUNCTION_INFO_ADDRS)
route_done = {} 
route_done["genome"] = {}
route_done["fileprocessing"] = {}
route_done["cycles"] = {} 
route_done["epigenomics"] = {}
route_done["soykb"] = {} 
route_done["wordcount"] = {} 

 # a new request from outside
# the previous function was done
@app.route('/request', methods = ['POST'])
def req():
    data = request.get_json(force=True, silent=True)
    print(data)
    log.info('worker proxy.y receive the request')
    request_id = data['request_id']
    workflow_name = data['workflow_name']
    function_name = data['function_name']
    no_parent_execution = data['no_parent_execution'] 
    # get the corresponding workflow state and trigger the function
    state = dispatcher.get_state(workflow_name, request_id) #todo 这里不是很理解  # get_state返回某个WorkerSP
    ###12-12,每个workflow对应一个state,对应入度为0的函数，其no_parent_execution为true,表示没有父节点
    dispatcher.trigger_function(workflow_name, state, function_name, no_parent_execution)
    #p = multiprocessing.Process(target=dispatcher.)
    return json.dumps({'status': 'ok'})

#todo 12-14 lambda,一个来着container/proxy.py的请求
###告诉它，这个函数已经运行完了，可以起它后续节点的后续节点
@app.route('/finish', methods = ['POST'])
def done():
    #data的格式为["function_name":"Done", "request_id":request_id,]
    #update 格式应该为['function_name':function_name,'request_id':request_id,'workflow_name':workflow_name]

    data = request.get_json(force = True, silent = True)
    #print('finsh the worker proxy receive the data:%s',data)
    print('type(data):',type(data))
    func_name = data['function_name']
    workflow_name = data['workflow_name']
    request_id = data['request_id']
    state = dispatcher.get_state(workflow_name, request_id) 
    log.info('the rounte finish,the function_name:%s',func_name)
    print("route finish,the funct_name:",func_name)
    route_done[workflow_name][func_name] = 1 
    print("len(route_done):",len(route_done[workflow_name]))
    dispatcher.trigger_function_lambda_next(workflow_name,state,func_name) #只有workersp模式才会触发这个
    ###todo,12-14,或许以后需要更新
    return json.dumps({'status': 'ok'})

@app.route('/clear', methods = ['POST'])
def clear():
    data = request.get_json(force=True, silent=True)
    workflow_name = data['workflow_name']
    request_id = data['request_id']
    master = False
    if 'master' in data:
        master = True
        dispatcher.clear_db(workflow_name, request_id) # optional: clear results in center db
    dispatcher.del_state(workflow_name, request_id, master) # and remove state for every node
    return json.dumps({'status': 'ok'})

@app.route('/info', methods = ['GET'])
def info():
    return json.dumps(container_names)

@app.route('/clear_container', methods = ['GET'])
def clear_container():
    print('clearing containers')
    os.system('docker rm -f $(docker ps -aq --filter label=workflow)')
    return json.dumps({'status': 'ok'})


@app.route('/test', methods = ['POST'])
def test():
    print(request.get_json(force=True, silent=True))
    return json.dumps(container_names)

GET_NODE_INFO_INTERVAL = 0.1

def get_container_names():
    gevent.spawn_later(get_container_names)
    global container_names
    container_names = [container.attrs['Name'] for container in docker_client.containers.list()]

from gevent.pywsgi import WSGIServer
import logging
if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%H:%M:%S', level='INFO')
    print('sys.argv[1]',sys.argv[1])
    print('sys.argv[2]',sys.argv[2])
    server = WSGIServer((sys.argv[1], int(sys.argv[2])), app)
    print('server',server)
    log.info('server:%s',server)
    server.serve_forever()
    gevent.spawn_later(GET_NODE_INFO_INTERVAL)