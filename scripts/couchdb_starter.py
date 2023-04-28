import couchdb
import time

time.sleep(2)

#URL = 'http://openwhisk:openwhisk@172.16.187.6:5984/'
#db = couchdb.Server(URL)
db = couchdb.Server('http://openwhisk:openwhisk@127.0.0.1:5984')
if 'workflow_latency' in db:
   db.delete('workflow_latency')
if 'log' in db:
    db.delete('log')
if 'results' in db:
    db.delete('results')
db.create('workflow_latency')
db.create('results')
db.create('log')
