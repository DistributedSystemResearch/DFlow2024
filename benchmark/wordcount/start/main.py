import os

#Now,use my FreeStore 
def main():
    fn = list(os.listdir('/text'))
    res = dict()
    res['filename'] = fn 
    for fname in fn:
        with open('/text/'+fname, 'r') as f:
            res[fname] = f.read() #res是一个dict 
    #print("type(res):",type(res))
    store.Put("start",res) #here,the start are function's name,which is the key and res  is the value
