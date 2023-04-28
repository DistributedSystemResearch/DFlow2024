import time
#注:upload的前驱节点是sentiment和conversion
def main():
    #inp = store.fetch(['html', 'score'])
    inp1 = store.Get('sentiment') #this is to get dict 
    inp2 = store.Get('conversion') #this is a str 
    # pretent to do some uploading
    time.sleep(1)