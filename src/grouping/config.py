NETWORK_BANDWIDTH = 25 * 1024 * 1024 / 4 # 25MB/s / 4
NET_MEM_BANDWIDTH_RATIO = 15 # mem_time = net_time / 15
CONTAINER_MEM = 256 * 1024 * 1024 # 256MB
NODE_MEM = 256 * 1024 * 1024 * 1024 # 256G
RESERVED_MEM_PERCENTAGE = 0.2
GROUP_LIMIT = 100
WORKFLOW_YAML_ADDR = {'fileprocessing': '../../benchmark/fileprocessing/flat_workflow.yaml',
               #   'illgal_recognizer': '../../benchmark/illgal_recognizer/flat_workflow.yaml',
               #   'video': '../../benchmark/video/flat_workflow.yaml',
                  'wordcount': '../../benchmark/wordcount/flat_workflow.yaml',
                  'cycles': '../../benchmark/generator/cycles/flat_workflow.yaml',
                  'epigenomics': '../../benchmark/generator/epigenomics/flat_workflow.yaml',
                  'genome': '../../benchmark/generator/genome/flat_workflow.yaml',
                  'soykb': '../../benchmark/generator/soykb/flat_workflow.yaml'}
COUCHDB_URL = 'http://openwhisk:openwhisk@127.0.0.1:5984/'
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_DB = 0
#todo:这里增加worker_node的ip 
#master_node的ip暂定为:192.168.1.96,即lambda机器是master
#则lambda2机器和lambda1机器是worker_node,到时候在云上测试的时候需要更改
#WORK_NODES =["192.168.1.50", "192.168.1.203"] #50是lambda2机器，203是lambda1机器

WORK_NODES = ["http://172.16.187.13:23567/handle","http://172.16.187.14:23567/handle"]
#,"http://172.16.187.16:23567/handle","http://172.16.187.15:23567/handle","http://172.16.187.17:23567/handle","http://172.16.187.18:23567/handle","http://172.16.187.12:23567/handle"]

#WORK_NODES = ["http://172.16.187.13:23567/handle","http://172.16.187.14:23567/handle","http://172.16.187.16:23567/handle","http://172.16.187.15:23567/handle","http://172.16.187.17:23567/handle","http://172.16.187.18:23567/handle","http://172.16.187.12:23567/handle"]
#WORK_NODES =["http://192.168.1.50:23567/handle", "http://192.168.1.203:23567/handle"] 
#修改:lambda1和lambda2作为worker机器

#203是master机器
