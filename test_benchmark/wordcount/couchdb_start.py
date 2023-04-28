import couchdb
import time

time.sleep(2)
db = couchdb.Server('http://openwhisk:openwhisk@192.168.1.96:5984')
if 'workflow_latency' in db:
    db.delete('workflow_latency')
if 'results' in db:
    db.delete('results')

if 'log' in db:
    db.delte('log')
db.create('workflow_latency')
db.create('results')
db.create('log')
