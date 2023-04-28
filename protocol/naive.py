from  FreeStoreClient import Store

import time 
store =Store()


"""
size = 100 * 1024 * 1024 #100M
key = "hello"
value = 'a' * size 

start = time.time()

store.PutStr(key,value)
not_stream_duration = time.time()  - start 

start = time.time()
"""
x = [4,8,16,32,64,96,100]

for i in x:
    size = i * 1024 * 1024 
    key1 = "hello" + str(i)
    value1 = 'a' * size 
    valueSize = str(i) +"M" #how MB
    start  =time.time()
    store.PutStr(key1,value1)
    not_stream_duration = time.time()  - start 
    print('Put',valueSize,'do not use stream ,duration:',not_stream_duration)
    start = time.time()
    store.GetStr(key1)
    duration = time.time() - start 
    print('Get',valueSize,'do not use stream duration:',duration)
    """
    start = time.time()
    key2 = 'olleh' + str(i)
    value2 = '*b' * size 
    store.Stream(key2,value2)
    stream_duration = time.time() - start 
    print('Put',valueSize,'use stream,duration:',stream_duration)
    print('**********\n')
    """

# dic = {}

# dic[key] = v
# store.Put(key,dic)

# data, _ = store.Get(key)
# print(len(data[key]))