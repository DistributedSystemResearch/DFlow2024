import os 


file = "./4ps.log"

dir = "./genome/"

for line in open(file,'r'):
    curLine =line.strip().split(" ")
    #print(curLine[3])容器名
    id = curLine[0]
    #print(curLine)
    path = dir + curLine[3] +".log" 
    command = "docker logs " + id + " > " + path + " 2>&1"
    os.system(command  )