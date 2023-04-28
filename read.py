import os 

def remove_image(filename):
    for line in open(filename):
        data = line.split(' ')
        new_data = []
        for x in data:
            
            if x != '':
                #(x)
                new_data.append(x)
        data = new_data 
        # if "redis" not in data:
            #print(data[55])
        print(data[2])
        id = data[2]
        cmd = "docker image rm " + str(id)
        os.system(cmd)

os.system("docker image ls | grep recog > none.log ")

filename = "none.log"

remove_image(filename)

os.system("docker image ls | grep none > none.log ")

filename = "none.log"

remove_image(filename)
