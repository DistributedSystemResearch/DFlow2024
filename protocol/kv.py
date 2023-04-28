
import pickle
import codecs
import math
import json
dict = {}

#sizes = [int(math.pow(2,15)),int(math.pow(2,22)),int(math.pow(2,25))] #32KB 4MB 32MB
#sizes = [int(math.pow(2,15)),int(math.pow(2,22)),int(math.pow(2,25))] #32KB 4MB 32MB
#sizes = [int(math.pow(2,10)),int(math.pow(2,12)),int(math.pow(2,16))] #32KB 4MB 32MB
sizes = [int(math.pow(2,12)),int(math.pow(2,24)),int(math.pow(2,26))] #4kB,16MB,128MB 
dict1 ={}

keys =[] 
temp = "ABCDE"
keys.append(temp)
dict1[temp] = {temp:str(4) * (2**20)} #1MB
dict[temp] = {temp:str(4) * (2**20)} #1MB
for i in range(3):
    key = temp + str(i)
    keys.append(key)
    value = str(i) * sizes[i]
    dict[key] = {key:value}

i  = 0
for k, v in dict.items():
    print(type(v),type(json.dumps(v)))
    # if i == 0:
    #     print(v)
print(keys)

# print(dict['key0'])
# for k,v in dict.items():
#     #print(k,)
#     for k1,v1 in v.items():
#         #print(type(k),type(k1))
#         #print(k,k1)
#         encoded_value = codecs.encode(pickle.dumps(v), "base64")
#         print(type(encoded_value))
#         value_decode = pickle.loads(codecs.decode(encoded_value, "base64"))
#         print(type(encoded_value),type(value_decode))
#         print(v == value_decode)
#         print(value_decode)