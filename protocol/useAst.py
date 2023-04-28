import ast
# byte_str = b"{'one': 1, 'two': 2}"
# dict_str = byte_str.decode("UTF-8")
# mydata = ast.literal_eval(dict_str)
# print(repr(mydata))
import time

mydict = {"hello":'world','freq':3,'Id':{'world':76, 'SJTU':"FDU"}}
print('1 mydict type:',type(mydict),mydict)
#print('2myStr type:',type(myStr),myStr)
start  = time.time()
myStr = str(mydict)

bytes_myStr =myStr.encode(encoding = "utf-8")
duration_dict_to_str_to_bytes = time.time() - start
print('3 byte_myStr  type:',type(bytes_myStr), bytes_myStr)
start = time.time()
dict_str = bytes_myStr.decode('utf-8')
mydata = ast.literal_eval(dict_str)
duration_bytes_to_str_to_dict = time.time() - start
print('4 mydata type:',type(mydata),mydata)

print('5 dict_to_str_to_bytes ',duration_bytes_to_str_to_dict, ' and bytes_to_str_to_dict:',duration_bytes_to_str_to_dict)
"""
1 mydict type: <class 'dict'> {'hello': 'world', 'freq': 3, 'Id': {'world': 76, 'SJTU': 'FDU'}}
2myStr type: <class 'str'> {'hello': 'world', 'freq': 3, 'Id': {'world': 76, 'SJTU': 'FDU'}}
3 byte_myStr  type: <class 'bytes'> b"{'hello': 'world', 'freq': 3, 'Id': {'world': 76, 'SJTU': 'FDU'}}"
4 mydata type: <class 'dict'> {'hello': 'world', 'freq': 3, 'Id': {'world': 76, 'SJTU': 'FDU'}}

"""
"""
1 mydict type: <class 'dict'> {'hello': 'world', 'freq': 3, 'Id': {'world': 76, 'SJTU': 'FDU'}}
3 byte_myStr  type: <class 'bytes'> b"{'hello': 'world', 'freq': 3, 'Id': {'world': 76, 'SJTU': 'FDU'}}"
4 mydata type: <class 'dict'> {'hello': 'world', 'freq': 3, 'Id': {'world': 76, 'SJTU': 'FDU'}}
5 dict_to_str_to_bytes  4.839897155761719e-05  and bytes_to_str_to_dict: 4.839897155761719e-05

"""