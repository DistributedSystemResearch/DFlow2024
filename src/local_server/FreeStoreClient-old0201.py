from __future__ import print_function
import logging
import object_store_pb2
import object_store_pb2_grpc
import grpc
import json
import os 
#这个是跑在host上的
class FreeStore():
    def __init__(self):
        # to: where to store for outputs
        # keys: foreach key (split_key) specified by workflow_manager
        self.channel  = grpc.insecure_channel('localhost:9999',options=[
            ('grpc.max_send_message_length', -1),
            ('grpc.max_receive_message_length',-1),],) #4GB
        self.stub = object_store_pb2_grpc.LocalStoreServerStub(self.channel)

    def Put(self,key,value):
        valueJsonToBytes = json.dumps(value).encode('utf-8')
        print('key:',key,' value:',value)
        object_size = len(valueJsonToBytes)
        reply = self.stub.Put(object_store_pb2.PutRequest(object_id = key.encode(encoding = 'utf-8'), inband_data = valueJsonToBytes,object_size = object_size))
        return reply.ok

    def Get(self, key):
        reply = self.stub.Get(object_store_pb2.GetRequest(object_id = key.encode(encoding = 'utf-8')))
        return json.loads(reply.inband_data),reply.object_size
        
    def PutGlobalInput(self,global_input):
        #此时gloal_input格式是key:value,
        #todo:global_input是json文件，我们先需要将其变为dict格式
        global_input = json.loads(global_input) #! 将json转为dict 
        #print('PutGlobalInput:')
        #value的格式是字典，科学计算value['size']  =8989
        for (key,value) in global_input.items():
            #key是str,value是int,把key和value变成一个json
            #print('key:',key, 'value:',value)
            data = {}
            data[key] = value #data的格式类似为data['hello'] = {'hello':3}
            valueJsonToBytes = json.dumps(data).encode('utf-8') #先转为json,然后转为bytes
            reply = self.stub.PutGlobalInput(object_store_pb2.PutGlobalInputRequest(object_id = key.encode(encoding = 'utf-8'), inband_data = valueJsonToBytes))
    
    def Close(self):
        self.channel.close()
        
            
