import os
import time
from flask import Flask, request
from gevent.pywsgi import WSGIServer
from FreeStoreClient import FreeStore




proxy = Flask(__name__)
proxy.status = 'new'
proxy.debug = False


def HandleGlobalInput(global_input):
    #global_input是json格式
    store = FreeStore()
    store.PutGlobalInput(global_input)
    store.Close()


@proxy.route('/handle', methods=['POST'])
def handle():
    proxy.status ='handle'
    global_input = request.get_json(force=True, silent=True)
    print(len(global_input))
    print('*******global_input********',global_input)
    res = {
        'reply':'ok'
    }
    HandleGlobalInput(global_input)
    proxy.status = 'ok'
    return res 

if __name__ == '__main__':
    server = WSGIServer(('0.0.0.0', 23567), proxy)
    print('listen on 23567')
    server.serve_forever()

