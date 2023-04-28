import json
from os import putenv
import time
import sys
sys.path.append("..")
from FreeStoreClient import Store
from kv import dict

from kv import dict1,keys

def A_Put(store):
    PutKeys = []
    #PutKeys.append(keys[1]) #1MB
    PutKeys.append(keys[3]) #64MB
    for key in PutKeys:
        value =dict[key]
        start  =time.time()
        ok = store.Put(key,value)
        duration = time.time()  - start 
        print('In APut.py, key:',key,'value:',len(value),'\n In APut.py,the duration:',duration,' ok:',ok,'\n*********\n')
        
"""
def runPut(store):
    PutKeys = []
    PutKeys.append(keys[1]) #1MB
    PutKeys.append(keys[3]) #128,MB
    for key,value in dict.items():
        start = time.time()
        ok = store.Put(key,value)
        duration = time.time() - start
        print('In runPut,reply.ok',ok, ' and duration:', duration)

"""

"""
def runPut1(store):
    for key,value in dict1.items():
        start =time.time()
        ok = store.Put(key,value)
        duration = time.time() -  start 
        print("In runPut1,reply.ok:",ok, " and duration:",duration)
"""

if __name__ == "__main__":
    store = Store()
    #runPut(store)
    A_Put(store)
    #runPut1(store)
