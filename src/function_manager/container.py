import requests
import docker
import time
import logging
import gevent
from docker.types import Mount
import json 
import sys
import multiprocessing 

sys.path.append("..")
from my_log import log

base_url = 'http://127.0.0.1:{}/{}'


class Container:
    # create a new container and return the wrapper
    @classmethod
    def create(cls, client, image_name, port, attr):
        log.info("container create,the image_name:%s",image_name)
        host_port = str(5000)  + '/tcp'
        container = client.containers.run(image_name,
                                          detach=True,
                                          ports={host_port: str(port)}, #docker端口:host端口
                                          labels=['workflow'])

        res = cls(container, port, attr)
        log.info('Container create,the container:%s',container)
        res.wait_start() #todo 这一步干啥
        return res

    # get the wrapper of an existed container
    # container_id is the container's docker id
    @classmethod
    def inherit(cls, client, container_id, port, attr):
        container = client.containers.get(container_id)
        return cls(container, port, attr)

    def __init__(self, container, port, attr):
        self.container = container
        self.port = port
        self.attr = attr
        self.lasttime = time.time()
        self.all_datas = {}


    # wait for the container cold start
    def wait_start(self):
        while True:
            try:
                log.info('wait_start')
                r = requests.get(base_url.format(self.port, 'status')) 
                log.info('wait_start,the r.status_code:%s and r:%s',r.status_code,r)
                #print('wait_start, the r:',r)
                if r.status_code == 200:
                    break
            except Exception:
                pass
            gevent.sleep(0.005)

    # send a request to container and wait for result
    def send_request(self, data):
        log.info('Container send_request,the url:%s',base_url.format(self.port, 'run'))
        #print('Container send_request,the url:%s',base_url.format(self.port, 'run'))
        log.info("Container send_request,the data:%s",data)
        #print("container send_request,the data:",data)
        #function_name = data['function_name']
        r = requests.post(base_url.format(self.port, 'run'), json= data)
        self.lasttime = time.time()
        res = r.json()
        #self.all_datas[function_name] = res
        print('here we use r.josn,type(res):',res ,' and res:',res)
        return  res
        

    # initialize the container
    def init(self, workflow_name, function_name):
        data = { 'workflow': workflow_name, 'function': function_name }
        x = base_url.format(self.port, 'init')
        log.info('container init:the base_url:%s',x)
        r = requests.post(base_url.format(self.port, 'init'), json=data)
        self.lasttime = time.time()
        return r.status_code == 200

    # kill and remove the container
    def destroy(self):
        self.container.remove(force=True)
