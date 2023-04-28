import os 
path = "/home/xxsh/StoneFree/src/workflow_manager/" + 'cycles'
if os.path.exists(path):
    os.system('rm -rf %s ' % path)