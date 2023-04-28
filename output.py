#######################src/grouping/grouping.py的第277行~317行#########################

function_my_output={}
for arg in node.output_files:
    function_my_output[arg] = node.output_files[arg]['size'] #记录大小
    #记录每个函数的output的key和值
#arg类似(benchmark/generator/genome/flat_workflow.yaml) 67ca3d9d-ee56-4bd1-8ae9-05fc1db56d7a.gz

function_my_input = []
for arg in node.input_files:
    function_my_input.append(arg)
    #! 记录某个函数需要的所有输入,只需要记录其key就行
    #然后通过key去
#arg类似(benchmark/generator/genome/flat_workflow.yaml)
function_info['my_output'] = function_my_output
function_info['my_input'] = function_my_input

function_info_dict['node_name'] =function_info 
#################src/container/main.py###########################
import time
import string
import random

#todo:一定要修改对应的FaasFlow的src/main.py
def main():
    input_res = store.getAllInput(store.input) 
    #store.input是一个key
    #todo(01-13):这是针对科学计算应用，它的input也应该确立了
    for k in input_res.keys():
        print(k)
    output_res = {}
    for (k,v) in store.output.items():
        #store.output是一个dict
        #也就是functiion_output,key是类似arg类似(benchmark/generator/genome/flat_workflow.yaml) 67ca3d9d-ee56-4bd1-8ae9-05fc1db56d7a.gz
        #value是一个int型数据
        result = 'a' * v 
        output_res[k] = result
        #这里的k可能是某一个函数的input
    time.sleep(store.runtime)
    store.PutAllOutput(output_res)#output_res是一个dict,k是str,v是dict，这里也要修改FaasFlow的
#############################src/container/FreeStoreClient.py========================
from __future__ import print_function
import logging
import object_store_pb2
import object_store_pb2_grpc
import grpc
import json
import os 
import time 

class FreeStore():
    def __init__(self, workflow_name, function_name, request_id, input, output, keys, runtime, db_server):
        # to: where to store for outputs
        # keys: foreach key (split_key) specified by workflow_manager
        self.db = db_server['results']
        self.latency_db = db_server['workflow_latency']
        self.log_db = db_server['log']
        self.fetch_dict = {} #todo:这个用来干啥
        self.put_dict = {} #todo:这个用来干啥
        self.workflow_name = workflow_name #工作流名
        self.function_name = function_name #函数名
        self.request_id = request_id
        self.input = input
        self.output = output
        self.keys = keys #split_key
        self.runtime = runtime
        #192.168.1.50 this is lambda2 machine 
        #在lambda上要修改成自己的ip地址
        self.channel  = grpc.insecure_channel('192.168.1.50:9999',options=[
            ('grpc.max_send_message_length', -1),
            ('grpc.max_receive_message_length',-1),],) #4GB
        self.stub = object_store_pb2_grpc.LocalStoreServerStub(self.channel)
        if os.path.exists('work'):
            os.system('rm -rf work')
        os.mkdir('work')

    def Put(self,key,value):
        #value类型为dict 
        put_start = time.time()
        valueJsonToBytes = json.dumps(value).encode('utf-8')
        object_size = len(valueJsonToBytes)
        reply = self.stub.Put(object_store_pb2.PutRequest(object_id = key.encode(encoding = 'utf-8'), inband_data = valueJsonToBytes,object_size = object_size))
        put_end = time.time()
        self.latency_db.save({'request_id': self.request_id, 'function_name': self.function_name, 'phase': 'edge', 'time': put_end - put_start})
        return reply.ok

    def Get(self, key):
        reply = self.stub.Get(object_store_pb2.GetRequest(object_id = key.encode(encoding = 'utf-8')))
        get_time =reply.get_time 
        self.latency_db.save({'request_id': self.request_id, 'function_name': self.function_name, 'phase': 'edge', 'time': get_time})
        return json.loads(reply.inband_data),reply.object_size #reply.inband_data是dict 
    
    def PutStr(self,key,value):
        #key
        return None 
    
    def getAllInput(self,input_keys):
        #input是一个str list
        input_res = {}
        for key in input_keys:
            inband_data = self.Get(key)
            #inband_data是一个dict 
            input_res.update(inband_data)
        return input_res 
         #todo:getAllInput是得到workflow的某个函数节点需要的所有输出
    def PutAllOutput(self,output_res):
        #output_res是一个dict 
        #k是str,v也是dict
        for (k,v) in output_res.items():
            self.Put(k,v) #? k是str,v是dict,直接调用Put接口就OK了 
        #return 2 #todo:PutAllOutPut是将workflow某个函数节点产生的所有output 写入到FreeStore

########################src/workflow_manager/workersp.py=================

     # run a function on local，正常运行一个函数
def run_function_lambda(self, state: WorkflowState, function_name: str, func_ip:str) -> None:
    log.info('run function lambda: %s of: %s on func_ip:%s', function_name, state.request_id,func_ip)
    print('run function lambda, the function_name:', function_name ,' and func_ip:',func_ip)
    # end functions
    if function_name == 'END':
        return

    info = self.get_function_info(function_name)#得到函数名对应的函数信息
        # switch functions
    if function_name.startswith('virtual'): #todo what is this #todo(01-10,这个只适合video/illegal这两个benchmark)  
        self.run_switch_lambda(state, info,func_ip)
        return # do not need to check next
        
    if function_name in self.foreach_func:
        log.info('run function lambda,this function_name:%s is in self.foreach_func:%s ',function_name ,self.foreach_func)
        print('run function lambda,this function_name:',function_name,' is in self.foreach_func:',self.foreach_func)
        self.run_foreach_lambda(state, info,func_ip)
    elif function_name in self.merge_func:
        log.info('run function lambda,this function_name:%s is self.merge_func:%s',function_name,self.merge_func)
        print('run function lambda,this function_name:',function_name, '  is self.merge_func:',self.merge_func)
        self.run_merge_lambda(state, info,func_ip) #todo(01-10):这里可能需要修改
    else: # normal functions
        log.info('run function lambda, this function_name:%s is normal function',function_name)
        print('run function lambda, this function_name:',function_name,' is normal function')
        self.run_normal_lambda(state, info,func_ip)
    
def run_normal_lambda(self, state: WorkflowState, info: Any, func_ip:str) -> None:
    start = time.time()
    log.info('run normal_lambda,the function_name:%s',info['function_name'])

    print('run normal_lambda,the info[unction_name]:',info['function_name'])
    self.function_manager.run_lambda(info['function_name'], state.request_id,info['runtime'], info['my_input'], info['my_output'],info['to'], {},func_ip,self.workflow_name) #TODO(error) 
        #!在这里，info['my_input']是一个list,记录了某个函数需要的所有output
        #! info['my_output']是一个dict,k是一个字符串，value是一个int
    end = time.time()
    repo.save_latency({'request_id': state.request_id, 'function_name': info['function_name'], 'phase': 'all', 'time': end - start})
