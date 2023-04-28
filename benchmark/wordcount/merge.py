from test import FreeStore


def main():
    store = FreeStore()
    map_res = store.Get("count")
    filenames = map_res['filename'] #得到文件列表
    res = dict()
    for filename in filenames:
        filename_res =  map_res[filename] #这也是一个字典
        for w,f in filename_res.items():
            #w是代表词汇，f是代表词汇在这个文件出现的频率
            if w not in res:
                res[w] = f
            else:
                res[w] = res[w] +f    
    store.Put('result',res)

main()