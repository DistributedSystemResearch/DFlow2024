from os import remove
import couchdb
import redis
from typing import Dict, List
import config

couchdb_url = config.COUCHDB_URL

class Repository:
    def __init__(self, workflow_name, remove_old_db=True):
        self.redis = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB)
        self.couch = couchdb.Server(couchdb_url)
        if remove_old_db:
            db_list = [workflow_name + '_function_info', workflow_name + '_function_info_raw', workflow_name + '_workflow_metadata',workflow_name + '_function_ip']
            for db_name in db_list:
                if db_name in self.couch:
                    self.couch.delete(db_name)

    def save_function_info(self, function_info, db_name):
        if db_name not in self.couch:
            self.couch.create(db_name)
        db = self.couch[db_name]
        for name in function_info:
            #print('function name*******:',name)
            db[name] = function_info[name] #把function_info的每个key都保存在数据库中 name是函数名
    
    def save_function_ip(self,function_info_ip,db_name):
        if db_name not in self.couch:
            self.couch.create(db_name)
        db = self.couch[db_name]
        #function_info_ip是一个字典,key为workflow的名字
        #value是一个字典，其key为函数名，value为函数名所在的机器ip 
        for workflow_name in function_info_ip:
            print('workflow_name:',workflow_name,' and ips:',function_info_ip[workflow_name])
            db[workflow_name] = function_info_ip[workflow_name]
            
    def save_global_input(self,global_input,db_name,workflow_name):
        if db_name not in self.couch:
            self.couch.create(db_name)
        db = self.couch[db_name]
        db[workflow_name] = global_input    #global_input是一个dict 

    def save_foreach_functions(self, foreach_functions, db_name):
        if db_name not in self.couch:
            self.couch.create(db_name)
        db = self.couch[db_name]
        db.save({'foreach_functions': list(foreach_functions)})
    
    def save_merge_functions(self, merge_functions, db_name):
        if db_name not in self.couch:
            self.couch.create(db_name)
        db = self.couch[db_name]
        db.save({'merge_functions': list(merge_functions)})

    def save_critical_path_functions(self, critical_path_functions, db_name):
        if db_name not in self.couch:
            self.couch.create(db_name)
        db = self.couch[db_name]
        db.save({'critical_path_functions': list(critical_path_functions)})

    def save_all_addrs(self, addrs, db_name):
        if db_name not in self.couch:
            self.couch.create(db_name)
        db = self.couch[db_name]
        db.save({'addrs': list(addrs)})

    def save_start_functions(self, start_functions, db_name):
        if db_name not in self.couch:
            self.couch.create(db_name)
        db = self.couch[db_name]
        db.save({'start_functions': start_functions})

    def save_basic_input(self, basic_input, db_name):
        if db_name not in self.couch:
            self.couch.create(db_name)
        db = self.couch[db_name]
        db.save(basic_input)

    def fetch_finished_request_id(self, workflow_name: str) -> List[str]:
        db = self.couch['log']
        mango = {'selector': {'workflow': workflow_name, 'status': 'FINISH'}}
        return [row['request_id'] for row in db.find(mango)]

    def fetch_logs(self, workflow_name: str, request_id: str) -> List[Dict]:
        db = self.couch['log']
        mango = {'selector': {'request_id': request_id}}
        result = [dict(row) for row in db.find(mango)]
        result.remove({'request_id': request_id, 'workflow': workflow_name, 'status': 'EXECUTE'})
        result.remove({'request_id': request_id, 'workflow': workflow_name, 'status': 'FINISH'})
        return result
    
    def remove_logs(self, request_id: str):
        db = self.couch['log']
        mango = {'selector': {'request_id': request_id}}
        for row in db.find(mango):
            db.delete(row)
