from __future__ import print_function
import logging
import object_store_pb2
import object_store_pb2_grpc
import grpc
import json
import os 
import time 
import gevent 

class FreeStore():
    def __init__(self, workflow_name, function_name, request_id, input, output, keys, runtime, db_server,global_input):
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
        self.GetData = {}
        #self.global_input_db = db_server[workflow_name +'_global_input']
        self.global_input = global_input #这个workflow的全局输入
        self.put_times  = 0
        self.get_times = 0
        #192.168.1.50 this is lambda2 machine 
        #在lambda上要修改成自己的ip地址

        self.channel  = grpc.insecure_channel('172.16.187.16:9999',options=[
            ('grpc.max_send_message_length', -1),
            ('grpc.max_receive_message_length',-1),],) #4GB
        self.stub = object_store_pb2_grpc.LocalStoreServerStub(self.channel)
        if os.path.exists('work'):
            os.system('rm -rf work')
        os.mkdir('work')

    def Put(self,key,value, flag= True):
        #value类型为dict 
        put_start = time.time()
        #print('1In Put,type(value):',type(value),'\n len(value):\n',len(value))
        valueJsonToBytes = json.dumps(value).encode('utf-8')
        #print('2 In put,the valueJsonToBytes:',valueJsonToBytes)
        #print('2.5 In put,the valueJsonToBytes:',type(valueJsonToBytes), 'and len(valueJsonToBytes):',len(valueJsonToBytes))
        #print('3 In put,********end')
        object_size = len(valueJsonToBytes)
        request_id_bytes = self.request_id.encode(encoding = 'utf-8')
        #print('object_id:',key,' and the object_size:',object_size)
        reply = self.stub.Put(object_store_pb2.PutRequest(object_id = key.encode(encoding = 'utf-8'), inband_data = valueJsonToBytes,object_size = object_size,request_id = request_id_bytes))
        put_end = time.time()
        self.put_times += put_end -put_start 
        #if flag:
            #self.latency_db.save({'request_id': self.request_id, 'function_name': self.function_name, 'phase': 'edge', 'time': put_end - put_start})
        return reply.ok

    def Get(self, key):
        start = time.time()
        request_id_bytes = self.request_id.encode(encoding = 'utf-8')
        reply = self.stub.Get(object_store_pb2.GetRequest(object_id = key.encode(encoding = 'utf-8'),request_id = request_id_bytes))
        duration = time.time() -start
        get_time =reply.get_time  
        self.get_times += get_time
        #self.latency_db.save({'request_id': self.request_id, 'function_name': self.function_name, 'phase': 'edge', 'time': get_time})
        #print("1 in Get,type(reply.inband_date):",type(reply.inband_data),'2 and len(reply.inband_data):',len(reply.inband_data))
        #print("1.2  in Get,key:",key," and reply.inband_data:",reply.inband_data)
        res = json.loads(reply.inband_data)
        #print('1.3 in Get,type(res):',type(res))
        return res 
    

    
    #key和value都是str
    def PutStr(self,key,value):
        #key
        keyToBytes = key.encode(encoding = 'utf-8')
        #object_size = len(ValueToBytes)
        request_id_bytes = self.request_id.encode(encoding = 'utf-8')
        reply = self.stub.Put(object_store_pb2.PutRequest(object_id = key.encode(encoding = 'utf-8'), inband_data =value,object_size = len(value),request_id = request_id_bytes))
        return reply.ok 
    
    def getAllInput(self,input_keys):
        #input是一个str list
        input_res = {}
        input_from_global = []
        input_from_parent = []
        for key in input_keys:
            if key in self.global_input:#来自全局输入
                input_from_global.append(key)
            else:
                #来自父节点
                input_from_parent.append(key)
        #先批量处理全局输入
        for key in input_from_global:
            inband_data = self.Get(key)
            input_res[key] = inband_data
        for key in input_from_parent:
            inband_data = self.getStr(key)
            input_res[key] = inband_data
        return input_res
        """
        #input_key是一部分来自全局输入，一部分来自父节点的输出
        for key in input_keys:
            if key in self.global_input: #来自全局输入
                inband_data = self.Get(key)
                input_res[key] = inband_data #inband_data是一个dict 
            else: #this key is 来自父节点
                inband_data = self.getStr(key) #inband_data的形势为"aaaaaaa"
                input_res[key] = inband_data
        return input_res
        """
    def getStr(self,key):
        #key是str,
        #b"abcde".decode("utf-8")
        keyBytes =key.encode(encoding = 'utf-8') 
        request_id_bytes = self.request_id.encode(encoding = 'utf-8')
        reply = self.stub.Get(object_store_pb2.GetRequest(object_id = keyBytes,request_id = request_id_bytes))
        #reply.inband_data is bytes 
        #print('In getStr,type(reply.inband_data):',type(reply.inband_data))
        #print('In getStr,reply.inband_data',reply.inband_data)
        return reply.inband_data #this is a bytes 

    #value全都是一种类型:x:'aaaaa'
    def PutAllOutput(self,output_res):
        start = time.time()
        for (k,v) in output_res.items():
            #print("In PutAllOutput,the key:",k,' and type(v):',type(v),'\n v:',v)
            #print('******end\n\n\n')
            self.PutStr(k,v)
        duration = time.time() - start 
        self.latency_db.save({'request_id': self.request_id, 'function_name': self.function_name, 'phase': 'edge', 'time': duration})
        #output_res是一个dict 
        #out_put是dict,key是str,value也是str 

        #return 2 #todo:PutAllOutPut是将workflow某个函数节点产生的所有output 写入到FreeStore
    def Close(self):
        self.channel.close()