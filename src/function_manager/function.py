import logging
import time
import math
from gevent import event
from gevent.lock import BoundedSemaphore
from container import Container
from function_info import FunctionInfo
import requests,multiprocessing
import sys
sys.path.append("..")
from my_log import log

    #response.close()
# data structure for request info
class RequestInfo:
    def __init__(self, request_id, data):
        self.request_id = request_id
        self.data = data
        self.result = event.AsyncResult() #这个是什么
        self.arrival = time.time()

# manage a function's container pool
class Function:
    def __init__(self, client, function_info, port_controller):
        self.client = client
        self.info = function_info
        self.port_controller = port_controller
        
        self.num_processing = 0
        self.rq = []
        log.info('Function, the ifo:%s and function_name:%s ',self.info,self.info.function_name)
        print('Function, the self.info:',self.info, 'and function_name: ',self.info.function_name)
        #FIXME 
        self.function_name = self.info.function_name #TODO just for debug 
        # container pool
        self.num_exec = 0 # the number of containers in execution, not in container pool
        self.container_pool = []
        self.b = BoundedSemaphore()
        # self.record_ports = dir()
    
    # put the request into request queue
    #input是输入,output是输出
    def send_request(self, request_id, runtime, input, output, to, keys):
        data = {'request_id': request_id, 'runtime': runtime, 'input': input, 'output': output, 'to': to, 'keys': keys}
        req = RequestInfo(request_id, data)
        self.rq.append(req) #将req加入请求队列
        res = req.result.get() ##todo res不是很理解
        return res

    # put the request into request queue
    #input是输入,output是输出
    def send_request_lambda(self, request_id, function_name,runtime, input, output, to, keys,func_ip:str,workflow_name:str):
        data = {
            'request_id': request_id, 
            'runtime': runtime,
             'input': input, 
             'output': output, 
             'to': to, 
             'keys': keys,
             'ip':func_ip,
             'function_name':function_name,
             'workflow_name':workflow_name,
        }
        req = RequestInfo(request_id, data)
        self.rq.append(req) #将req加入请求队列
        log.info('1Function , send_request_lambda:,the function_name:%s and ip:%s and workflow_name:%s and len(req):%s',function_name,func_ip,workflow_name,len(self.rq))
        log.info('2function send_request_lambda,the len(self.rq):%s and self.num_processing:%s and self.function_name:%s',len(self.rq),self.num_processing,self.function_name)
        #print('function send_request_lambda,the function_name:',function_name, ' and ip:',func_ip, ' and workflow_name:',workflow_name,' and len(rq):',len(self.rq))
        res = req.result.get() ##todo res不是很理解
        func_ip = res['ip']
        workflow_name = res['workflow_name']
        function_name = res['function_name']
        request_id = res['request_id']
        data = {
            'request_id':request_id,
            'function_name':function_name,
            'workflow_name':workflow_name
        }
        #remote_url =  'http://{}/finish'.format(func_ip) #这里需要加上端口,因为在向他的机器上必须要用端口
        #response = requests.post(remote_url, json=data) #todo 可能需要异步？
        
        #p = multiprocessing.Process(target = MyProcessing,args = (remote_url,data,))
        #p.start()
        return res
    # receive a request from upper layer
    def dispatch_request(self):
        # no request to dispatch
        #print('dispatch request')
        #log.info('dispactch_request,the len(self.rq):%s and self.num_processing:%s',len(self.rq),self.num_processing)
        if len(self.rq) - self.num_processing == 0:
            return
        self.num_processing += 1
        
        # 1. try to get a workable container from pool
        container = self.self_container()
        
        # create a new container
        while container is None:
        # if container is None:
            container = self.create_container()
           
        # the number of exec container hits limit
        #print('dispatch_request,the self.function_name:',self.function_name ,' and container:',container)
        log.info('dispatch_request,the self.function_name:%s and container:%s',self.function_name,container)
        log.info('dispactch_request,the len(self.rq):%s and self.num_processing:%s and self.function_name:%s',len(self.rq),self.num_processing,self.function_name)

        if container is None:
            self.num_processing -= 1
            return

        req = self.rq.pop(0)
        self.num_processing -= 1
        # 2. send request to the container
        #TODO:为什么不执行到这里？
        log.info('send request to: %s of: %s, rq len: %d', self.info.function_name, req.request_id, len(self.rq))
        #print('function dispatch request,self.info.function_name:',self.info.function_name,' and req.request_id:',req.request_id,' and len(self.rq):',len(self.rq))
        res = container.send_request(req.data)#给docker发请求,这应该是一个json

        req.result.set(res)
        
        # 3. put the container back into pool
        self.put_container(container)
        #这里可以向其它发消息

    # get a container from container pool
    # if there's no container in pool, return None
    def self_container(self):
        res = None

        self.b.acquire()
        if len(self.container_pool) != 0:
            log.info('get container from pool of function: %s, pool size: %d', self.info.function_name, len(self.container_pool))
            res = self.container_pool.pop(-1)
            self.num_exec += 1
        self.b.release()
        
        return res

    # create a new container
    def create_container(self):
        # do not create new exec container
        # when the number of execs hits the limit
        self.b.acquire() # critical: missing lock may cause infinite container creation under high concurrency scenario
        if self.num_exec + len(self.container_pool) > self.info.max_containers:
            log.info('hit container limit, function: %s', self.info.function_name)
            return None
        self.num_exec += 1
        self.b.release()

        log.info('create container of function: %s', self.info.function_name)
        try:
            host_port = self.port_controller.get()
            # while host_port in self.record_ports:
            #     host_port = self.port_controller.get()
            # self.record_ports[host_port]  =1 #避免端口重复
            container = Container.create(self.client, self.info.img_name, host_port, 'exec')
        except Exception as e:
            print(e)
            self.num_exec -= 1
            return None
        self.init_container(container)
        log.info('function init_container:%s and self.function_name:%s',container,self.function_name)
        return container

    # put the container into one of the three pool, according to its attribute
    def put_container(self, container):
        self.b.acquire()
        self.container_pool.append(container)
        self.num_exec -= 1
        self.b.release()

    # after the destruction of container
    # its port should be give back to port manager
    def remove_container(self, container):
        logging.info('remove container: %s, pool size: %d', self.info.function_name, len(self.container_pool))
        container.destroy()
        self.port_controller.put(container.port)

    # do the function specific initialization work
    def init_container(self, container):
        container.init(self.info.workflow_name, self.info.function_name)

    # do the repack and cleaning work regularly
    def repack_and_clean(self):
        # find the old containers
        old_container = []
        self.b.acquire()
        self.container_pool = clean_pool(self.container_pool, exec_lifetime, old_container)
        self.b.release()

        # time consuming work is put here
        for c in old_container:
            self.remove_container(c)
        # self.record_ports.clear()

def favg(a):
    return math.fsum(a) / len(a)

# life time of three different kinds of containers
exec_lifetime = 600

# the pool list is in order:
# - at the tail is the hottest containers (most recently used)
# - at the head is the coldest containers (least recently used)
def clean_pool(pool, lifetime, old_container):
    cur_time = time.time()
    idx = -1
    for i, c in enumerate(pool):
        if cur_time - c.lasttime < lifetime:
            idx = i
            break
    # all containers in pool are old, or the pool is empty
    if idx < 0:
        idx = len(pool)
    old_container.extend(pool[:idx])
    return pool[idx:]
