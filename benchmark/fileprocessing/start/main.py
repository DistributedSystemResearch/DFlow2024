def main():
    fn = 'sample.md'
    with open('/text/'+fn, 'r') as f:
        content = f.read()
    data = {}
    data["start"] = content
    #contentBytes = content.encode(encoding = 'utf-8') #转为bytes 
    store.Put('start',data) #start是函数名