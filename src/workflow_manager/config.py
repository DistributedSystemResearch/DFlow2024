
#FUNCTION_INFO_ADDRS = { 'fileprocessing': '../../benchmark/fileprocessing', 'wordcount': '../../benchmark/wordcount'}
FUNCTION_INFO_ADDRS = {'genome': '../../benchmark/generator/genome', 'epigenomics': '../../benchmark/generator/epigenomics',
                                                 'soykb': '../../benchmark/generator/soykb', 'cycles': '../../benchmark/generator/cycles',
                                                 'fileprocessing': '../../benchmark/fileprocessing', 'wordcount': '../../benchmark/wordcount'}
DATA_MODE = 'optimized'# raw, optimized
CONTROL_MODE = 'WorkerSP' # , MasterSP
MASTER_HOST = '172.16.189.19:8000' #作为master节点机器       #  '192.168.1.96:8000' #todo 这是master节点

COUCHDB_URL = 'http://openwhisk:openwhisk@172.16.187.19:5984/'


REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_DB = 0
CLEAR_DB_AND_MEM = True