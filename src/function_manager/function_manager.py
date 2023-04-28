import logging
import gevent
import docker
import os
from function_info import parse
from port_controller import PortController
from function import Function
import random
import requests,multiprocessing

import sys
sys.path.append("..")
from my_log import log

repack_clean_interval = 5.000 # repack and clean every 5 seconds
dispatch_interval = 0.005 # 200 qps at most

# def MyProcessing(remote_url,data):
#     response = requests.post(remote_url, json=data) #todo 可能需要异步？

# the class for scheduling functions' inter-operations
class FunctionManager:
    def __init__(self, config_path, min_port,host_addr):
        self.function_info = parse(config_path)
        print('FunctionManager, the config_path:',config_path)
        log.info('FunctionManager, the config_path:%s',config_path)
        log.info('FunctionManager, the self.function_info:%s',self.function_info)
        print('FunctionManager, the self.function_info:',self.function_info)
        self.port_controller = PortController(min_port, min_port + 4999)
        self.client = docker.from_env()
        self.host_addr = host_addr
        self.functions = {
            x.function_name: Function(self.client, x, self.port_controller)
            for x in self.function_info
        } #? self.functions是一个字典，key是function name,value是Funcion @每个函数都有不同的req和info
        self.init()
       
    def init(self):
        print("Clearing previous containers.")
        os.system('docker rm -f $(docker ps -aq --filter label=workflow)')

        gevent.spawn_later(repack_clean_interval, self._clean_loop) #todo 这是什么
        gevent.spawn_later(dispatch_interval, self._dispatch_loop) #todo 这是什么
    
    def _clean_loop(self):
        gevent.spawn_later(repack_clean_interval, self._clean_loop)
        for function in self.functions.values():
            gevent.spawn(function.repack_and_clean)

    def _dispatch_loop(self):
        # log.info('function_manager,_dispatch_loop')
        #print('function_manager,_dispatch_loop')
        gevent.spawn_later(dispatch_interval, self._dispatch_loop)
        for function in self.functions.values():
            gevent.spawn(function.dispatch_request)
    
    def run(self, function_name, request_id, runtime, input, output, to, keys):
        #todo:12-11，这个参数key是干啥的
        # print('run', function_name, request_id, runtime, input, output, to, keys)
        if function_name not in self.functions:
            raise Exception("No such function!")
        return self.functions[function_name].send_request(request_id, runtime, input, output, to, keys)

    def run_lambda(self, function_name, request_id, runtime, input, output, to, keys,ip,workflow_name:str):
        #ip表示这个函数在哪台机器是运行
        #todo:12-11，这个参数key是干啥的
        # print('run', function_name, request_id, runtime, input, output, to, keys)
        #print('FunctionManager,the run_lambda,function_name:',function_name, 'and ip:%s and workflow_name:',workflow_name)

        log.info('1FunctionManager,the run_lambda,function_name:%s and ip:%s and workflow_name:%s',function_name,ip,workflow_name)
        if function_name not in self.functions:
            raise Exception("No such function!")
        #return self.functions[function_name].send_request_lambda(request_id, function_name,runtime, input, output, to, keys,ip,workflow_name)
        resp = self.functions[function_name].send_request_lambda(request_id, function_name,runtime, input, output, to, keys,ip,workflow_name)
        #打印出ip和host_addr 
        data = {
            'request_id':request_id,
            'function_name':function_name,
            'workflow_name':workflow_name
        }
        # remote_url =  'http://{}/finish'.format(ip) 
        logging.info("2FunctionManager, the run_lambda,ip:%s and self.host_addr:%s",ip,self.host_addr)
        # p = multiprocessing.Process(target = MyProcessing,args = (remote_url,data,))
        # p.start() #开始多进程通信
        #要不要join?
        return resp