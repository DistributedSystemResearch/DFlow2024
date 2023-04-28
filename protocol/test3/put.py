import json
import time
import sys
sys.path.append("..")
from FreeStoreClient import Store
from kv import dict

from kv import dict1

def runPut(store):
    for key,value in dict.items():
        start = time.time()
        ok = store.Put(key,value)
        duration = time.time() - start
        print('In runPut,reply.ok',ok, ' and duration:', duration)

def runPut1(store):
    for key,value in dict1.items():
        start =time.time()
        ok = store.Put(key,value)
        duration = time.time() -  start 
        print("In runPut1,reply.ok:",ok, " and duration:",duration)

if __name__ == "__main__":
    store = Store()
    runPut(store)
    #runPut1(store)
