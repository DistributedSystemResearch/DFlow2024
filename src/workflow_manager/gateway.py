import json
import gevent
from gevent import monkey
monkey.patch_all()
import sys
from flask import Flask, request
from repository import Repository
import requests
import time
import config

app = Flask(__name__)
repo = Repository()

def trigger_function(workflow_name, request_id, function_name):
    info = repo.get_function_info(function_name, workflow_name + '_function_info') #这个返回啥
    #! info是整个wofkflow中某个函数的信息
    ip = ''
    if config.CONTROL_MODE == 'WorkerSP':
        ip = info['ip']
    elif config.CONTROL_MODE == 'MasterSP':
        ip = config.MASTER_HOST
    url = 'http://{}/request'.format(ip)
    data = {
        'request_id': request_id,
        'workflow_name': workflow_name,
        'function_name': function_name,
        'no_parent_execution': True
    }
    #? 12-12,trigger_function是向对应的主机ip发送请求，让它开始执行函数
    requests.post(url, json=data)

def run_workflow(workflow_name, request_id):
    repo.create_request_doc(request_id) #todo 这个得好好了解下

    # allocate works
    start_functions = repo.get_start_functions(workflow_name + '_workflow_metadata') 
    #12-07 更新:这个函数是表示workflow的第一个函数，start_function是可能有多个
    #! 12-12,在grouping的时候，start_functions是已经存在了couchdb中，这个表示一个DAG中入度为0的函数
    #! 12-12,注:start_function是可能有多个
    start = time.time()
    jobs = []
    for n in start_functions:
        #n是函数名
        jobs.append(gevent.spawn(trigger_function, workflow_name, request_id, n)) #n是function_name 
    gevent.joinall(jobs)
    end = time.time()

    # clear memory and other stuff
    if config.CLEAR_DB_AND_MEM:
        master_addr  = ''
        if config.CONTROL_MODE == 'WorkerSP':
            master_addr = repo.get_all_addrs(workflow_name + '_workflow_metadata')[0]
        elif config.CONTROL_MODE == 'MasterSP':
            master_addr = config.MASTER_HOST
        clear_url = 'http://{}/clear'.format(master_addr)
        requests.post(clear_url, json={'request_id': request_id, 'master': True, 'workflow_name': workflow_name})
    
    return end - start

@app.route('/run', methods = ['POST'])
def run():
    data = request.get_json(force=True, silent=True)
    workflow = data['workflow']
    request_id = data['request_id']
    logging.info('processing request ' + request_id + '...')
    repo.log_status(workflow, request_id, 'EXECUTE')
    latency = run_workflow(workflow, request_id)
    repo.log_status(workflow, request_id, 'FINISH')
    return json.dumps({'status': 'ok', 'latency': latency})

@app.route('/clear_container', methods = ['POST'])
def clear_container():
    data = request.get_json(force=True, silent=True)
    workflow = data['workflow']
    addrs = repo.get_all_addrs(workflow + '_workflow_metadata')
    jobs = []
    for addr in addrs:
        clear_url = f'http://{addr}/clear_container'
        jobs.append(gevent.spawn(requests.get, clear_url))
    gevent.joinall(jobs)
    return json.dumps({'status': 'ok'})

from gevent.pywsgi import WSGIServer
import logging
if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%H:%M:%S', level='INFO')
    server = WSGIServer((sys.argv[1], int(sys.argv[2])), app)
    server.serve_forever()