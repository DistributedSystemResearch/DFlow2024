import redis 
import time 

store = redis.StrictRedis(host='172.17.0.1', port=6379, db=0)

x = [4,8,16,32,64,96,100,200,400,800]

for i in x:
    size = i * 1024 * 1024 
    key1 = "hello" + str(i)
    value1 = 'a' * size 
    valueSize = str(i) +"M" #how MB
    start  =time.time()
    store.put(key1,value1)
    not_stream_duration = time.time()  - start 
    print('Put',valueSize,'redis put key1 ,duration:',not_stream_duration)
    start = time.time()
    key2 = 'olleh' + str(i)
    value2 = '*b' * size 
    #store.Stream(key2,value2)
    store.put(key2,value2)
    stream_duration = time.time() - start 
    print('Put',valueSize,'redis put key2,duration:',stream_duration)
    print('**********\n')
    