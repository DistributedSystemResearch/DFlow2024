
from __future__ import print_function
import logging
import object_store_pb2
import object_store_pb2_grpc
import grpc
import json
import os 
import time 
import re 
class FreeStore():
    def __init__(self):
        # to: where to store for outputs
        # keys: foreach key (split_key) specified by workflow_manager
        """
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
        """
        #192.168.1.50 this is lambda2 machine 
        #在lambda上要修改成自己的ip地址
        self.channel  = grpc.insecure_channel('localhost:9999',options=[
            ('grpc.max_send_message_length', -1),
            ('grpc.max_receive_message_length',-1),],) #4GB
        self.stub = object_store_pb2_grpc.LocalStoreServerStub(self.channel)
        # if os.path.exists('work'):
        #     os.system('rm -rf work')
        # os.mkdir('work')

    def Put(self,key,value):
        #value类型为dict 
        put_start = time.time()
        valueJsonToBytes = json.dumps(value).encode('utf-8')
        object_size = len(valueJsonToBytes)
        reply = self.stub.Put(object_store_pb2.PutRequest(object_id = key.encode(encoding = 'utf-8'), inband_data = valueJsonToBytes,object_size = object_size))
        put_end = time.time()
 #       self.latency_db.save({'request_id': self.request_id, 'function_name': self.function_name, 'phase': 'edge', 'time': put_end - put_start})
        return reply.ok

    def Get(self, key):
        reply = self.stub.Get(object_store_pb2.GetRequest(object_id = key.encode(encoding = 'utf-8')))
        #get_time =reply.get_time 
        #print(reply.get_time)
#        self.latency_db.save({'request_id': self.request_id, 'function_name': self.function_name, 'phase': 'edge', 'time': get_time})
        return json.loads(reply.inband_data)

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
            self.Put(k,v) 
        #return 2 #todo:PutAllOutPut是将workflow某个函数节点产生的所有output 写入到FreeStore
    # def PutStr(self,key,value):
    #     object_size = len(value)
    #     valueToByte = 

def main():
    store = FreeStore()
    content  = store.Get("start")
    #print(content)
    print('********\n\n\n\n')
    #print('wwwwwwwwwwwwww',content['pg-dorian_gray.txt'])
    #print('type')
    filenames = content['filename']
    print(type(filenames))
    res = dict()
    res['filename'] = filenames
    for filename in filenames:
        temp = dict()
        words = content[filename]
        for w in re.split(r'\W+', words):
            if w not in temp:
                temp[w] = 1
            else:
                temp[w] = temp[w] +1
        res[filename] = temp 
    store.Put('count',res)
            
    #print('1',filename_content[1])
    #filenames=filename_content['filename'] #这个filenames有所有的文件
    #reIs is a dict,the k are the filename ,v are the filename's content
    """
    res = dict()
    res['filename'] = filenames
    for filename in filenames:
        temp = dict()
        content = filename_content[filename]
        for w in re.split(r'\W+', content):
            if w not in temp:
                temp[w] = 1
            else:
                temp[w] +=1
        res[filename] = temp #这个文件对于的map过程
    store.Put("count",res)
    """
main()
