import time
import string
import random

#todo:一定要修改对应的FaasFlow的src/main.py
def main():
    
    input_res = store.getAllInput(store.input) #这里要设置 #todo:it may have bug(01-13)
    #它的input一部分来自global input，一部分来自它的前驱函数，input格式可以为dict,key是str,value是int 
    #对于global input,在grouping的时候已经存到了每台机器上的local store 
    #同样:我们也有弄好output
    #01-14,input是list
    #todo(01-13):这是针对科学计算应用，它的input也应该确立了
    for k in input_res.keys():
        print(k)
    output_res = {}
    #output是dict
    m = 'a'.encode()
    for (k,v) in store.output.items():
        result = m * v #v是一个int
        output_res[k] =result 
    time.sleep(store.runtime)
    store.PutAllOutput(output_res)#output_res是一个dict,k是str,v是dict，这里也要修改FaasFlow的

