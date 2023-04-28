from __future__ import print_function
import logging
import object_store_pb2
import object_store_pb2_grpc
import grpc
import json

class Store():
    def __init__(self):
        self.channel  = grpc.insecure_channel('localhost:9999',options=[
            ('grpc.max_send_message_length', -1),
            ('grpc.max_receive_message_length',-1),],) #4GB
        self.stub = object_store_pb2_grpc.LocalStoreServerStub(self.channel)

    def Put(self,key,value):
        #value is dict
        #keyBytes = key.encode(encoding = 'utf-8')
        valueJsonToBytes = json.dumps(value).encode('utf-8')
        object_size = len(valueJsonToBytes)
        reply = self.stub.Put(object_store_pb2.PutRequest(object_id = key.encode(encoding = 'utf-8'), inband_data = valueJsonToBytes,object_size = object_size))
        return reply.ok

    def Get(self, key):
        reply = self.stub.Get(object_store_pb2.GetRequest(object_id = key.encode(encoding = 'utf-8')))
        return json.loads(reply.inband_data),reply.object_size
    def GetStr(self,key):
        reply = self.stub.Get(object_store_pb2.GetRequest(object_id = key.encode(encoding = 'utf-8')))
        return reply.inband_data

    def Stream(self,key,value):
        #key and value is str
        valueSize = len(value)
        sliceSize  =2 * 1024 * 1024 #4M
        key = key.encode('utf-8')
        nums = int(valueSize / sliceSize)
        def put_message():
            for i in range(nums):
                #inband_data =[ data = value[i*sliceSize:valueSize] if ( i == (nums-1)) else 
                req = [object_store_pb2.PutRequest(object_id = key,inband_data = value[i*sliceSize : (i+1) * sliceSize].encode('utf-8')) if (i != (nums-1)) else  object_store_pb2.PutRequest(object_id = key,inband_data = value[i*sliceSize : valueSize].encode('utf-8'))][0]
                yield req 
        
        reply = self.stub.PutStream(put_message())
    
    def PutStr(self,key,value):
        valueJsonToBytes =value.encode('utf-8')
        object_size = len(valueJsonToBytes)
        reply = self.stub.Put(object_store_pb2.PutRequest(object_id = key.encode(encoding = 'utf-8'), inband_data = valueJsonToBytes,object_size = object_size))
        return reply.ok