import os
import re
#Now,use my FreeStore 
def main():
    filenames = ["./text/pg-being_ernest.txt","../text/pg-dorian_gray.txt"]
    res = {} 
    i = 1
    for filename in filename:
        res1 = {}
        with open(filename,'r') as f:
            content = f.read()
            for w in re.split(r'\W+',content):
                if w not in res1:
                    res1[w] = 1
                else:
                    res1[w] +=1
        res[i] = res1[w]
        i++
    return res
res = main()
