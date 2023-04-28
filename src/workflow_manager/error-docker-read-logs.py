import os 
import sys


file = "./ps.log"
tag = '"python3'
res =  [] 

def FindWorkflow(workflow_pool,image_name):
    for workflow in workflow_pool:
        if workflow in image_name:
            return workflow
    return None 
i = 1
dirs = []
dir_docker = {}
workflow_pool = ['cycles', 'epigenomics', 'genome', 'soykb',  'fileprocessing', 'wc']
for workflow_name in workflow_pool:
    dir_docker[workflow_name] = []
for line in open(file,'r'):
    curLine =line.strip().split(" ")
    if tag in curLine: #找到对应的所有workflow 运行的docker id
        for workflow_name in workflow_pool:
            for word in curLine :
                if workflow_name in word:
                    dir_docker[workflow_name].append(curLine[0])

print(dir_docker)  


dir =  "./" 
for workflow_dir in workflow_pool:
    s = dir + workflow_dir
    if os.path.exists(s):
        os.system('rm -rf ' + s  )

for workflow_dir in workflow_pool:
    if os.path.exists(workflow_dir) == False:
        s = dir + workflow_dir
        os.mkdir(s)

for k , v in dir_docker.items():
    #k is 目录
    for id in v:
        filename ="./" + k + "/"  + id + ".log"
        print(filename)
        os.system("sudo docker logs %s > %s 2>&1 " % (id ,filename) ) 
