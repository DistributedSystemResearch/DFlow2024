# from local_client import Put
# from local_client import Get 
# from local_client import Test

# Test(3)
import json
from keyvalue import dict
import sys
sys.path.append("..")
from FreeStoreClient import Store


#for k in dict:
"""
channel = grpc.insecure_channel('localhost:5678')
stub = route_guide_pb2_grpc.RouteGuideStub(channel)
for key,value in dict.items():

"""

def runPut(store):
    for key,value in dict.items():
        ok = store.Put(key,value)
        print('In runPut,reply.ok',ok)

def runGet(store):
    for key,value in dict.items():
        getValue, object_size = store.Get(key)
        assert(object_size == len(json.dumps(value)))
        assert(value == getValue)
        print('In runGet, object_size == len(json.dumps(value)',object_size == len(json.dumps(value)))
        print('In runGet, value == getValue',value == getValue)

if __name__ == "__main__":
    store = Store()
    #store.testStore()
    #print('ok')
    runPut(store)
    runGet(store)

"""
测试1::测试本机，先Put,然后Get,数据量大小可大32MB
"""