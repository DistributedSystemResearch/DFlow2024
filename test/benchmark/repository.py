from typing import Any, List
import couchdb
import redis
import json

couchdb_url = 'http://openwhisk:openwhisk@127.0.0.1:5984/'

class Repository:
    def __init__(self):
        self.redis = redis.StrictRedis(host='172.17.0.1', port=6380, db=0)
        self.couch = couchdb.Server(couchdb_url)

    def allocate_db(self, request_id):
        db = self.couch['results']
        db[request_id] = {}

    def mem_clearall(self):
        self.redis.flushall()

    def get_foreach_functions(self, db_name) -> List[str]:
        db = self.couch[db_name]
        for item in db:
            doc = db[item]
            if 'foreach_functions' in doc:
                return doc['foreach_functions']

    def get_merge_functions(self, db_name) -> List[str]:
        db = self.couch[db_name]
        for item in db:
            doc = db[item]
            if 'merge_functions' in doc:
                return doc['merge_functions']

    def get_start_functions(self, db_name) -> List[str]:
        db = self.couch[db_name]
        for item in db:
            doc = db[item]
            if 'start_functions' in doc:
                return doc['start_functions']

    def get_all_addrs(self, db_name) -> List[str]:
        db = self.couch[db_name]
        for item in db:
            doc = db[item]
            if 'addrs' in doc:
                return doc['addrs']

    def get_function_info(self, function_name: str, mode: str) -> Any:
        db = self.couch[mode]
        for item in db.find({'selector': {'function_name': function_name}}):
            return item

    def create_request_doc(self, request_id: str) -> None:
        self.couch['results'][request_id] = {}

    def get_keys(self, request_id: str) -> Any:
        keys = dict()
        doc = self.couch['results'][request_id]
        for k in doc:
            if k != '_id' and k != '_rev' and k != '_attachments':
                keys[k] = doc[k]
        return keys

    def get_len(self, request_id: str, function: str, parameter: str) -> int:
        db = self.couch['results']
        len = db[request_id + '_' + function + '_' + parameter]['len']
        return int(len)


    # fetch result from couchdb/redis
    def fetch_from_mem(self, redis_key, content_type):
        if content_type == 'application/json':
            redis_value = self.redis[redis_key].decode()
            return json.loads(redis_value)
        else:
            return self.redis[redis_key]

    def fetch_from_db(self, request_id, key):
        db = self.couch['results']
        f = db.get_attachment(request_id, filename=key, default='no attachment')
        if f != 'no attachment':
            return f.read()
        else:
            filename = key + '.json'
            f = db.get_attachment(request_id, filename=filename, default='no attachment')
            return json.load(f)

    def fetch(self, request_id, key):
        print('fetching...', key)
        redis_key_1 = request_id + '_' + key
        redis_key_2 = request_id + '_' + key + '.json'
        value = None
        if redis_key_1 in self.redis:
            value = self.fetch_from_mem(redis_key_1, 'bytes')
        elif redis_key_2 in self.redis:
            value = self.fetch_from_mem(redis_key_2, 'application/json')
        else:  # if not
            value = self.fetch_from_db(request_id, key)
        print('fetched value: ', value)
        return value
    


    def reset_all_mem(self, clear_function_data = False):
        if clear_function_data:
            self.couch.delete('results')
            self.couch.create('results')
        self.couch.delete('workflow_latency')
        self.couch.create('workflow_latency')


    def analyze_each_function(self, request_id):
        db = self.couch['workflow_latency']
        edge_time = {}
        node_time = {}
        transcode_cnt = 0
        for doc in db:
            if db[doc]['request_id'] != request_id:
                continue
            function_name = db[doc]['function_name']
            phase = db[doc]['phase']
            latency = db[doc]['time']
            if phase == 'edge+node':
                node_time.setdefault(function_name, 0)
                node_time[function_name] += latency
            else:
                edge_time.setdefault(function_name, 0)
                edge_time[function_name] += latency
                # if function_name == 'transcode':
                #     transcode_cnt = transcode_cnt+1
        for name in node_time:
            node_time[name] -= edge_time[name]
            # if name == 'transcode':
            #     node_time[name] /= transcode_cnt
            #     edge_time[name] /= transcode_cnt
        return edge_time, node_time

    def clear_latency_db(self):
        if 'latency' in self.couch:
            self.couch.delete('latency')
        self.couch.create('latency')
    
    def save_latency(self, l):
        db = self.couch['latency']
        db.save({'latency': l})
    
    def down_latency(self):
        db = self.couch['latency']
        l = []
        for _ in db:
            l.append(db[_]['latency'])
        return l
    
    def get_video_latency(self):
        db = self.couch['ffmpeg_latency']
        other_ffmpeg = 0
        other_io = 0
        transcode_ffmpeg = 0
        transcode_io = 0
        for doc in db:
            function_name = db[doc]['function']
            mode = db[doc]['mode']
            if function_name == 'transcode':
                if mode == 'io':
                    transcode_io += float(db[doc]['latency'])
                else:
                    transcode_ffmpeg += float(db[doc]['latency'])
            else:
                if mode == 'io':
                    other_io += float(db[doc]['latency'])
                else:
                    other_ffmpeg += float(db[doc]['latency'])
        return other_io / 12 + transcode_io / 48, other_ffmpeg / 12 + transcode_ffmpeg / 48