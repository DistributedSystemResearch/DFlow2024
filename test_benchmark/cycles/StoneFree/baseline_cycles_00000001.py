from wsgiref.util import request_uri
import config 
import redis
import couchdb
import uuid
import os
import time 
import matplotlib.pyplot as plt
# # 这两行代码解决 plt 中文显示的问题
# plt.rcParams['font.sans-serif'] = ['SimHei']
# plt.rcParams['axes.unicode_minus'] = False


#from repository import Repository 
from FreeStoreClient import FreeStore ,get_function_info 
db_server = couchdb.Server(config.COUCHDB_URL)
redis_server = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB)
info_db = 'cycles' + '_function_info'
workflow_name = 'cycles'
function_name = 'baseline_cycles_00000001'
info = get_function_info(db_server,function_name,info_db)
input = info['my_input']
output = info['my_output']
runtime = info['runtime']
key = {}


to = info['to']
request_id = str(uuid.uuid4())
store = FreeStore(workflow_name,function_name,request_id,input,output,key,runtime,db_server)
get_start = time.time() 
input_res = store.getAllInput(store.input) #这里要设置 #todo:it may have bug(01-13)
    #它的input一部分来自global input，一部分来自它的前驱函数，input格式可以为dict,key是str,value是int 
    #对于global input,在grouping的时候已经存到了每台机器上的local store 
    #同样:我们也有弄好output
    #01-14,input是list
    #todo(01-13):这是针对科学计算应用，它的input也应该确立了
get_time = time.time() - get_start 

print('the get_time:',get_time )
for k,v in input_res.items():
    print(k,'len(v):',v)
output_res = {}
    #output是dict
put_times  = [] 
put_times_sum = 0
final_res = [] 

for (k,v) in store.output.items():
    print(type(v),v)
    
    result = 'a' * v #FIXME:v是一个int行
    temp = dict()
    res_record = {}
    temp[k] = result
    sizelne = len(result )
    res_record[k] = sizelne
    print('result len:',sizelne)
    output_res[k] =temp
    time.sleep(store.runtime)
put_start = time.time()
store.PutAllOutput(output_res)#output_res是一个dict,k是str,v是dict，这里也要修改FaasFlow的
put_time = time.time()-  put_start 

print('put_time:',put_time )



