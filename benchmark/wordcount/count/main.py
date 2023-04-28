import re
def main():
    content  = store.Get("start")
    #this is a tupe 
    #print('type(filename_content):',type(content))
    filenames=content['filename'] #这个filenames有所有的文件
    #res is a dict,the k are the filename ,v are the filename's content 
    res = dict()
    res['filename'] = filenames
    for filename in filenames:
        temp = dict()
        words = content[filename]
        for w in re.split(r'\W+', words):
            if w not in temp:
                temp[w] = 1
            else:
                temp[w] +=1
        res[filename] = temp #这个文件对于的map过程
    store.Put("count",res)