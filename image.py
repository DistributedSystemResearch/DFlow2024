import os 


filename = "image.log"
os.system("docker images > " + filename )


for line in open(filename,'r'):
    curLine =line.strip().split(" ")
    print(curLine)

    #print(len(curLine[55]))
    if curLine[0] == '<none>':
        print(curLine[59])
        os.system("docker image rm " + curLine[59])