from __future__ import print_function
import logging
import object_store_pb2
import object_store_pb2_grpc
import grpc
import json
import os 
import time 
from typing import Any, List

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
        print('In Put,type(value):',type(value))
        valueJsonToBytes = json.dumps(value).encode('utf-8')
        object_size = len(valueJsonToBytes)
        print('object_id:',key,' and the object_size:',object_size)
        reply = self.stub.Put(object_store_pb2.PutRequest(object_id = key.encode(encoding = 'utf-8'), inband_data = valueJsonToBytes,object_size = object_size))
        put_end = time.time()
        self.latency_db.save({'request_id': self.request_id, 'function_name': self.function_name, 'phase': 'edge', 'time': put_end - put_start})
        return reply.ok

    def Get(self, key):
        start = time.time()
        reply = self.stub.Get(object_store_pb2.GetRequest(object_id = key.encode(encoding = 'utf-8')))
        duration = time.time() -start
        get_time =reply.get_time  
        self.latency_db.save({'request_id': self.request_id, 'function_name': self.function_name, 'phase': 'edge', 'time': get_time})
        res = json.loads(reply.inband_data)
        print('in Get,type(res):',type(res))
        return res
    
    def PutStr(self,key,value):
        #key
        return None 
    
    def getAllInput(self,input_keys):
        #input是一个str list
        input_res = {}
        for key in input_keys:
            inband_data = self.Get(key) #this is a int ,we should update it 
            #inband_data是一个dict 
            input_res[key] = inband_data
        return input_res 
         #todo:getAllInput是得到workflow的某个函数节点需要的所有输出
    def PutAllOutput(self,output_res):
        #output_res是一个dict 
        #k是str,v也是dict
        for (k,v) in output_res.items():
            self.Put(k,v) #? k是str,v是dict,直接调用Put接口就OK了 
        #return 2 #todo:PutAllOutPut是将workflow某个函数节点产生的所有output 写入到FreeStore


def get_function_info(couch, function_name: str, mode: str) -> Any:
    db = couch[mode]
    for item in db.find({'selector': {'function_name': function_name}}):
        return item
