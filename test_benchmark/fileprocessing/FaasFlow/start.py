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
from Store import Store ,get_function_info 
db_server = couchdb.Server(config.COUCHDB_URL)
redis_server = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB)
info_db = 'fileprocessing' + '_function_info'
info = get_function_info(db_server,'start',info_db)
input = info['input']
output = info['output']
runtime = info['runtime']
key = {}
workflow_name = 'fileprocessing'
function_name = 'start'

to = info['to']
request_id = str(uuid.uuid4())
store = Store(workflow_name,function_name,request_id,input,output,to,key,runtime,db_server,redis_server)
print(store)

fn = 'sample.md'

all_the_time = [] 
times = {} 
cal_start = time.time()
with open('./text/' + fn,'r') as f:
    content = f.read()

cal_duration = time.time() - cal_start
all_the_time.append(cal_duration)
times['cal'] = cal_duration
store_start = time.time()
store.put({'file': content}, {})
store_duration = time.time() - store_start

print('len(content):',len(content))
all_the_time.append(store_duration)
times['store'] = store_duration
print(times)
print(all_the_time)

print(times)
print(len(content))
x_label = ['cal time ','store time ']
plt.bar(x_label,all_the_time)
plt.title('fileprocessing start- cal vs store')
plt.show()

plt.savefig('fileprocessing-start.jpg')   #图片的存储
