import os
file = './port.log'

ports = []
port1 ="23567"
port2 = "8000"
port3 = "20210"
port4 = "9999"
ports.append(port1)
ports.append(port2)
ports.append(port3)
ports.append(port4)
for line in open(file,'r'):
    curLine =line.strip().split(" ")
    #print(curLine)
    print(curLine)
    for word in curLine:
        for port in ports:
            if port in word:
                print(curLine[4])
                if curLine[1] != '':
                    os.system("sudo kill -9 " + curLine[1])
                else:
                    os.system("sudo kill -9 " + curLine[4])
                
                
