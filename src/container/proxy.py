import logging
import os
import time
import couchdb
from flask import Flask, request
from gevent.pywsgi import WSGIServer
from FreeStoreClient import FreeStore
import config
import requests
import json 
import multiprocessing 

default_file = 'main.py'
work_dir = '/proxy'
couchdb_url = config.COUCHDB_URL
db_server = couchdb.Server(couchdb_url)
latency_db = db_server['workflow_latency']


class Runner:
    def __init__(self):
        self.code = None
        self.workflow = None
        self.function = None
        self.ctx = {}
        self.global_input = None 

    def init(self, workflow, function):
        print('init...')

        # update function status
        self.workflow = workflow
        self.function = function #函数名
        self.global_input_db = db_server[self.workflow +'_global_input']
        self.global_input = self.global_input_db[self.workflow] #这个workflow的全局输入
        os.chdir(work_dir)

        # compile first
        filename = os.path.join(work_dir, default_file) 
        #? 12-13,default_file是·main.py
        with open(filename, 'r') as f:
            self.code = compile(f.read(), filename, mode='exec')

        print('init finished...')

    # ##todo:这个需要增加参数，一是函数名，二是函数在哪台机器即ip上运行
    # def run(self, request_id, runtime, input, output, to, keys):
    #     # FaaSStore
    #     #注:这里的input已经有了，在grouping的时候已经存在了store里了
    #     store = Store(self.workflow, self.function, request_id, input, output, to, keys, runtime, db_server, redis_server)
    #     #todo:12-14,这里需要用到hoplite store，将其替换为我自己的hoplite Store
    #     self.ctx = {'workflow': self.workflow, 'function': self.function, 'store': store}
    #     # pre-exec
    #     exec(self.code, self.ctx)

    #     # run function
    #     start = time.time()
    #     out = eval('main()', self.ctx)
    #     end = time.time()
    #     #todo-12-14,这里需要向A所在的ip发一个消息，告诉它I am done ,让A其孙子函数

    #     latency_db.save({'request_id': request_id, 'function_name': self.function, 'phase': 'edge+node', 'time': end - start})
    #     return out


    ##todo:这个需要增加参数，一是函数名，二是函数在哪台机器即ip上运行
    #(self, workflow_name, function_name, request_id, input, output, keys, runtime, db_server):
    def run_lambda(self, request_id, runtime, input, output, to, keys,func_ip:str,func_name:str,workflow_name:str):
        #use my FreeStore
        store = FreeStore(self.workflow,self.function,request_id,input,output,keys,runtime,db_server,self.global_input)
        #todo:12-14,这里需要用到hoplite store，将其替换为我自己的hoplite Store
        self.ctx = {'workflow': self.workflow, 'function': self.function, 'store': store}

        # pre-exec
        exec(self.code, self.ctx)

        # run function
        start = time.time()
        out = eval('main()', self.ctx)
        end = time.time()
        # #todo-12-14,这里需要向A所在的ip发一个消息，告诉它I am done ,让A其孙子函数
        # #remote_url = 'http://{}/finish'.format(func_ip)
        # #print('remote_url:',remote_url)
        # #todo:我需要workflow_name
        # data = {
        #     'request_id':request_id,
        #     'function_name':func_name,
        #     'workflow_name':workflow_name,
        # }#todo-12-14肯定需要更新这个数据
        # #close
        duration = end - start 
        #reply = self.stub.Get(object_store_pb2.GetRequest(object_id = key.encode(encoding = 'utf-8')))
        #store.Close() #关掉channel 
        print('In run_lambda,the function_name:',func_name,' and workflow_name: ',workflow_name,' and func_ip:',func_ip, " and the duration:",duration)
        latency_db.save({'request_id': request_id, 'function_name': self.function, 'phase': 'edge+node', 'time':duration })
        return out


proxy = Flask(__name__)
proxy.status = 'new'
proxy.debug = False
runner = Runner()


@proxy.route('/status', methods=['GET'])
def status():
    res = {}
    res['status'] = proxy.status
    res['workdir'] = os.getcwd()
    if runner.function:
        res['function'] = runner.function
    return res


@proxy.route('/init', methods=['POST'])
def init():
    proxy.status = 'init'

    inp = request.get_json(force=True, silent=True)
    runner.init(inp['workflow'], inp['function'])

    proxy.status = 'ok'
    return ('OK', 200)


@proxy.route('/run', methods=['POST'])
def run():
    proxy.status = 'run'

    inp = request.get_json(force=True, silent=True)
    request_id = inp['request_id']
    runtime = inp['runtime']
    input = inp['input']
    output = inp['output']
    to = inp['to']
    keys =list() #empty
    func_ip = inp['ip']
    func_name = inp['function_name']
    workflow_name = inp['workflow_name']
    # record the execution time
    start = time.time()
    print('******the function_name:',func_name,' and workflow_name:',workflow_name)
    runner.run_lambda(request_id,runtime,input,output,to,keys,func_ip,func_name,workflow_name)
    #runner.run(request_id, runtime, input, output, to, keys)
    end = time.time()
    print("in run,the funcion:",func_name,"and run duration:",end - start)
    res = {
        "start_time": start,
        "end_time": end,
        "duration": end - start,
        #"inp": inp,
        "workflow_name":workflow_name,
        "function_name":func_name,
        "ip":func_ip,
        'request_id':request_id    
    }
    remote_url = 'http://{}/finish'.format(func_ip)
    print('remote_url:',remote_url)
        # #todo:我需要workflow_name
    data = {
        'request_id':request_id,
        'function_name':func_name,
        'workflow_name':workflow_name,
    }#todo-12-14肯定需要更新这个数据
        # #close 
    #print('In run_lambda,the function_name:',func_name,' and workflow_name: ',workflow_name,' and func_ip:',func_ip)
    #logging.info('container proxy run  the remote_url:%s and data:%s and func_ip:',remote_url,data,func_ip) #一个猜测:func_ip是192.168.1.50:8000这种格式
    proxy.status = 'ok'
    #p.join()
    return res


if __name__ == '__main__':
    server = WSGIServer(('0.0.0.0', 5000), proxy)
    print('server:',server)
    server.serve_forever()
