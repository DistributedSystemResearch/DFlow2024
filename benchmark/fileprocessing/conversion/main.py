import markdown

def main():
    contentBytes = store.Get('start') #start是conversion函数的父函数，需要从start那里拿数据
    content = contentBytes["start"]
    html = markdown.markdown(content) #html是str类型
    data = {}
    data["conversion"] = html 
    store.Put('conversion',data) #conversion是该函数名