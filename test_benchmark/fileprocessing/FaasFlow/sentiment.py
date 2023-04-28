from wsgiref.util import request_uri
import config 
import redis
import couchdb
import uuid
import os
import time 
import matplotlib.pyplot as plt
from start import request_id
# # 这两行代码解决 plt 中文显示的问题
# plt.rcParams['font.sans-serif'] = ['SimHei']
# plt.rcParams['axes.unicode_minus'] = False


#from repository import Repository 
from Store import Store ,get_function_info 


get_start  = time.time() 
content = store.fetch(['file'])
#print('content',content)
#['file']
get_time = time.time() - get_start 
#print(content)
print(len(content))
print('get_time:',get_time)
    # sia = SentimentIntensityAnalyzer()
    # score = sia.polarity_scores(content) # can't handle large dataset
time.sleep(7)


store.put({'score': 0}, {})
