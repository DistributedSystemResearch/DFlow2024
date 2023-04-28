import json
import time
file = {"hello":'world','freq':3,'Id':{'world':76, 'SJTU':"FDU"}}

print('1 type of file:',type(file))
start = time.time()
fileJson = json.dumps(file)
print('0 len(fileJson)',len(fileJson))
print('2 type of fileJson:',type(fileJson))
duration_json  = time.time() - start
start = time.time()
fileJsonBytes = fileJson.encode('utf-8')
print('0 len(filejsonBytes)',len(fileJsonBytes))
duration_json_to_bytes = time.time() - start
#print('in jsonToBytes.py  the duration of  str to json',duration_json,' and the duration of json to bytes',duration_json_to_bytes)
print('3 type of fileJsonBytes:',type(fileJsonBytes))

start  = time.time()
JsonToStr  = json.loads(fileJsonBytes)
duration_bytes_to_dict = time.time() - start
print('4 type of JsonToStr:',type(JsonToStr))
print(JsonToStr["hello"])
print(JsonToStr['Id']['world'])
print('5 in jsonToBytes.py  the duration of  str to json',duration_json,' and the duration of json to bytes',duration_json_to_bytes, ' and the duration of bytes to dict',duration_bytes_to_dict)

"""
1 type of file: <class 'dict'>
2 type of fileJson: <class 'str'>
3 type of fileJsonBytes: <class 'bytes'>
4 type of JsonToStr: <class 'dict'>
world
76
5 in jsonToBytes.py  the duration of  str to json 3.0279159545898438e-05  and the duration of json to bytes 1.1920928955078125e-06  and the duration of bytes to dict 0.00011467933654785156

"""
