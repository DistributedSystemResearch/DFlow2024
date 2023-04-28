from baseline_cycles_00000001 import request_id 

import config 
import redis
import couchdb
import uuid
import os
import time 
import matplotlib.pyplot as plt


from Store import Store ,get_function_info 
db_server = couchdb.Server(config.COUCHDB_URL)
redis_server = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB)
info_db = 'cycles' + '_function_info'

key = {}

workflow_name = 'cycles'
function_name = 'cycles_00000002'


info = get_function_info(db_server,function_name,info_db)
input = info['input']
output = info['output']
runtime = info['runtime']
to = info['to']
print('to:',to)
#print('input:',input)
#print('output:',output)
print(input)
store = Store(workflow_name,function_name,request_id,input,output,to,key,runtime,db_server,redis_server)

get_start  =time.time() 
input_res = store.fetch(store.input.keys())
get_time = time.time() - get_start 

for k in input_res.keys():
    print(k)
for k, v in input_res.items():
    print('here',len(v))
output_res = {}
put_times  = [] 
put_times_sum = 0
final_res = [] 
for (k, v) in store.output.items():
    result = 'a' * v['size']
    res_record = {}
    output_res[k] = result
    sizelne = len(result )
    print('result len:',sizelne)
    res_record[k] = sizelne
    time.sleep(store.runtime)
    put_start = time.time()
    store.put(output_res, {})
    put_time = time.time()- put_start 
    put_times.append(put_time)
    res_record[k + 'put'] = put_time 
    final_res.append(res_record)
    put_times_sum = put_times_sum + put_time 

print("*&&&&&&&&&&&&&&&&&&&&&")
print('get_time:',get_time)
print('final_res:',final_res)
print('************')
print('put_times_sum:',put_times_sum)
print('put_times:',put_times)

