import markdown
import time 
def run():
    fn = './text/sample.md'
    with open(fn,'r') as f:
        content = f.read()
    start = time.time()
    html = markdown.markdown(content)
    duration = time.time() - start 
    print(type(html),duration)
    #print(html)
    print(len(html))
run()