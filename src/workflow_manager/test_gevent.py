import gevent

y = [1,2,3,4]

def DPrint(x,i):
    global y 
    if(len(y)> 0):
        y = y[1:]
    print(x,i)

def test_gevent(x,i):
    global y 
    jobs = []
    job = gevent.spawn(DPrint,x,i)
    jobs.append(job)
    if(len(y) == 0 ):
        return ;
    for j in range(5):
        job =  gevent.spawn(test_gevent,x,j)
        jobs.append(job)
    gevent.joinall(jobs)

test_gevent(1,0)
