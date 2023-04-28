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
    for workflow_name in workflow_pool:
        for word in curLine:
            if workflow_name in word or tag in word:
                if not(curLine[0] in dir_docker):
                    dir_docker[curLine[0]] = workflow_name
                    os.system("sudo docker stop " + curLine[0])
                    os.system("sudo docker rm " + curLine[0])
    # for workflow_name in workflow_pool:
    #     if tag in curLine or workflow_name in 
    # if tag in curLine: #找到对应的所有workflow 运行的docker id
    #     for workflow_name in workflow_pool:
    #         for word in curLine:
    #             if workflow_name in word:
    #                 dir_docker[workflow_name].append(curLine[0])
    #                 os.system('')


# dir =  "." 
# for workflow_dir in workflow_pool:
#     s = dir + workflow_dir
#     if os.path.exists(s):
#         s = dir  + workflow_dir
#         os.system('rm -rf ' + s  )

# for workflow_dir in workflow_pool:
#     if os.path.exists(workflow_dir) == False:
#         os.mkdir(workflow_dir)

# for k , v in dir_docker.items():
#     #k is 目录
#     for id in v:
        #command1 ="sudo docker stop " + id 
        #command2 = "sudo docker rm " + id 
        # os.system(command1)
        # os.system(command2)
