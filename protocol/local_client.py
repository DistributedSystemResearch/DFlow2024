from __future__ import print_function
import logging
import object_store_pb2
import object_store_pb2_grpc
import grpc
import time

# #def PutDataToServer(stub):
# def Put(stub,key,value):
#     #todo:key and value are str
#     #todo:we should transfer to bytes
#     #todo:here we assume it's stream
#     #send_size = 4096
#     #todo:value may be small or big
#     #send_size = 4096
#     # value_size = len(value) #todo if the value
#     # send_size = value_size / 1024
#     # if(send_size < 4096):
#     #     send_size = 4096
#     # elif
#     send_size = 4 * 1024 * 1024 #4MB
#     value_size = len(value)
#     if value_size <= send_size:
#         #this is a small data
#         def PutSmallData():
#             for i in range(1):
#                 req = object_store_pb2.PutRequest(object_id = key,inband_data = value,object_size = value_size)
#                 yield  req
#         resp = stub.Put(PutSmallData())
#         print(resp.ok)
#     else:
#         nums = value_size / send_size
#         #this is a big data,we should use stream
#         slice_num = int(nums) #how many slice we should send
#         if  nums > slice_num:
#             slice_num = slice_num +1
#         def PutBigData():
#             for i in range(slice_num):
#             #todo:may be we should change the encode of str
#                 req = [object_store_pb2.PutRequest(object_id = "",inband_data = str.encode(value[i * send_size:(i+1) * send_size]))
#                        if (i !=(slice_num -1)) else
#                        object_store_pb2.PutRequest(object_id = str.encode(key),inband_data = str.encode(value[i * send_size:value_size])
#                                                ,object_size = value_size)]
#                 yield  req
#         resp = stub.Put(PutBigData())
#         print(resp.ok)
#
# def Get(stub,key):
#     req = object_store_pb2.GetRequest(object_id = str.encode(key)) #todo maybe this should change
#     resp_iter = stub.Get(req)
#     value = ""
#     object_size = 0
#     for resp in resp_iter:
#         #todo here the resp.inband_data is bytes,we should decode it to str
#         value += resp.inband_data
#         object_size = resp.object_size # this is the object_size of the all value
#     return value ,object_size

def Put(stub,key,value):
    # here the key is str
    # value : {'SJTU':'world'}
    #so we should transfer the key to bytes and transfer the value to json
    keyBytes = key.encode(encoding = "utf-8")
    valueJson = json.dumps(value).encode('utf-8')
    object_size =len(valueJson)
    reply = stub.Put(object_store_pb2.PutRequest( object_id = keyBytes,inband_data = valueJson,object_size = object_size ))
    print(reply.ok)

def Get(stub,key):
    #here the key are str,we should transfer to bytes
    keyBytes = key.encode(encoding = "utf-8")
    reply = stub.Get(object_store_pb2.GetRequest(object_id = keyBytes))
    #todo here the reply.value are bytes,we should transfer it to the dict
    valueDict = json.loads(reply.value)
    return valueDictob

def Test(i):
    print(i)

"""
channel = channel = grpc.insecure_channel(
    'localhost:5678',options=[
        ('grpc.max_send_message_length', -1),
        ('grpc.max_receive_message_length',-1),],)
stub = object_store_pb2_grpc.LocalStoreServerStub(channel)
在python client这样初始化stub就可以传4GB一下数据repl
"""