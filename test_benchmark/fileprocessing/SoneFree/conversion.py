from wsgiref.util import request_uri
import config 
import redis
import couchdb
import uuid
import os
import time 
import matplotlib.pyplot as plt
import markdown
# # 这两行代码解决 plt 中文显示的问题
# plt.rcParams['font.sans-serif'] = ['SimHei']
# plt.rcParams['axes.unicode_minus'] = False


#from repository import Repository 
from FreeStoreClient import FreeStore ,get_function_info 
db_server = couchdb.Server(config.COUCHDB_URL)
redis_server = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB)
info_db = 'fileprocessing' + '_function_info'
info = get_function_info(db_server,'conversion',info_db)
input = info['input']
output = info['output']
runtime = info['runtime']
key = {}
workflow_name = 'fileprocessing'
function_name = 'conversion'

to = info['to']
request_id = str(uuid.uuid4())
store = FreeStore(workflow_name,function_name,request_id,input,output,key,runtime,db_server)
print(store)

all_the_time = [] 
times = {} 
get_time_start = time.time()

content = store.Get('start') #start是conversion函数的父函数，需要从start那里拿数据
get_time = time.time() - get_time_start 
times['conversion_get'] = get_time 
all_the_time.append(get_time )
print('conversion conrent:',len(content))
cal_start = time.time()

html = markdown.markdown(content) #html是str类型

cal_time = time.time() 

times['conversion-cal'] = cal_time  - cal_start 
all_the_time.append(cal_time)
print(len(html))
put_start = time.time() 

store.Put('conversion',html) #conversion是该函数名
put_time= time.time() - put_start
times['conversion-put'] = put_time 
all_the_time.append(put_time)

x_label = ['get time ','cal-time','put time ']
plt.bar(x_label,all_the_time)
plt.title('StoneFree-fileprocessing conversion- get vs cal vs put')
plt.show()
plt.savefig('StoneFree-fileprocessing-conversion.jpg')
print(times)