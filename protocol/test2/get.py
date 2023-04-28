import json
import sys
import time
sys.path.append("..")
from FreeStoreClient import Store
from kv import dict,dict1 

def runGet(store):
    for key,value in dict.items():
        print(len(json.dumps(value)))
        start = time.time()
        getValue, object_size = store.Get(key)
        duration =  time.time() - start
        assert(object_size == len(json.dumps(value)))
        assert(value == getValue)
        
        print('In runGet,the duration:',duration)
        #print('In runGet, object_size == len(json.dumps(value)',object_size == len(json.dumps(value)))
        #print('In runGet, value == getValue',value == getValue)

def runGet1(store):
    for key,value in dict1.items():
        start = time.time()
        getValue, object_size = store.Get(key)
        assert(object_size == len(json.dumps(value)))
        assert(value == getValue)
        duration =  time.time() - start
        print('In runGet1,the duration:',duration)

if __name__ == "__main__":
    store = Store()
    #print(type(store))
    #store.testStore()
    #print('ok')
    #runGet(store)
    runGet1(store)
