from Store import Store,get_function_info

import config 
import redis
import couchdb
import uuid
import os
from repository import Repository 

db_server = couchdb.Server(config.COUCHDB_URL)
redis_server = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB)
latency_db = db_server['workflow_latency']
info_db = 'wordcount' + '_function_info'
start_info = get_function_info(db_server,'start',info_db)
print(start_info)
repo  = Repository()
request_id =  str(uuid.uuid4())
repo.create_request_doc(request_id)
all_keys = repo.get_keys(request_id)

print('all_keys:',all_keys)

print(repo)
start_input = start_info['input']
start_output = start_info['output']
start_to = start_info['to']
start_runtime = start_info['runtime']
keys = {}
workflow_name = 'wordcount'
function_name = 'start'

# foreach_keys  = [] 

# for arg in start_input:
#     if start_input[arg]['type'] == 'key':
#         foreach_keys.append(start_input[arg]['parameter'])

# keys = {}
# for i in range(len(all_keys[foreach_keys[0]])):
#     for k in foreach_keys:
#         keys[k] = all_keys[k][i]

# print("keys:",keys)

store = Store(workflow_name,function_name,request_id,start_input,start_output,start_to,keys,start_runtime,db_server,redis_server)
fn = list(os.listdir('./text'))
print(fn)
res = {"filename":fn}
for fname in fn:
    with open('./text/'+fname, 'r') as f:
            res[fname] = f.read()
print(len(res))
store.put(res, {})

#print(len(res))
func_name = "count"
count_info = get_function_info(db_server,func_name,info_db)
print('count_info',count_info)
count_input = count_info['input']
print('count_input',count_input)
count_output = count_info['output']
count_to = count_info['to']
count_runtime = count_info['runtime']


all_keys = repo.get_keys(request_id)
print('all_keys:',all_keys)
foreach_keys  = [] 

for arg in count_input:
     if count_input[arg]['type'] == 'key':
         foreach_keys.append(count_input[arg]['parameter'])


print("WWWWWW",all_keys[foreach_keys[0]])
for i in range(len(all_keys[foreach_keys[0]])):
    keys = {}
    for k in foreach_keys:
         keys[k] = all_keys[k][i]
    print("keys:",keys)
    store = Store(workflow_name,func_name,request_id,count_input,count_output,count_to,keys,count_runtime,db_server,redis_server)

    print('***********\n\n\n')
    fn = store.fetch(['filename']) #返回一个dict 
    print('1 fn:',fn,' and type(fn):',type(fn))
    fn = fn['filename']
    print(fn,'2 type(fn):',type(fn))
    print([fn])
    temp = store.fetch([fn]) #temp是一个dict,key是filename,value是filename的内容
    #print('temp:',temp,' and type(temp):',type(temp))
    content = temp[fn]
    
    #print(content)

    """
    def run_foreach(self, state: WorkflowState, info: Any) -> None:
        start = time.time()
        all_keys = repo.get_keys(state.request_id)  # {'split_keys': ['1', '2', '3'], 'split_keys_2': ...}
        foreach_keys = []  # ['split_keys', 'split_keys_2']
        for arg in info['input']:
            if info['input'][arg]['type'] == 'key':
                foreach_keys.append(info['input'][arg]['parameter'])
        jobs = [] #注:foreach_keys = ['filename'] # all_keys[foreach_keys[0]] = ['pg-dorian_gray.txt', 'pg-metamorphosis.txt', 'pg-huckleberry_finn.txt', 'pg-grimm.txt', 'pg-sherlock_holmes.txt', 'pg-frankenstein.txt', 'pg-tom_sawyer.txt', 'pg-being_ernest.txt']
        
        for i in range(len(all_keys[foreach_keys[0]])):
            keys = {}  # {'split_keys': '1', 'split_keys_2': '2'}
            for k in foreach_keys:
                keys[k] = all_keys[k][i]
            jobs.append(gevent.spawn(self.function_manager.run, info['function_name'], state.request_id,
                                     info['runtime'], info['input'], info['output'],
                                     info['to'], keys))
        gevent.joinall(jobs)
        end = time.time()
        repo.save_latency({'request_id': state.request_id, 'function_name': info['function_name'], 'phase': 'all', 'time': end - start})
    """