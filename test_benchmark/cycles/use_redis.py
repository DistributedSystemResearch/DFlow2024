import json
import os
import threading

import redis
import time
store = redis.StrictRedis(host='172.17.0.1', port=6379, db=0)

x = 'a' * 18086755
print(x) 
key = 'world'
put_start = time.time() 
store[key] =x
put_time = time.time() - put_start 

get_start = time.time()
b = store[key]
get_time = time.time() - get_start 
print('put:',put_time,'get:',get_time)