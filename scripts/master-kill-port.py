import os
file = './port.log'

ports = []
port1 ="23567"
port2 = "7000"
port3 = "8000"
port4 = "20210"
ports.append(port1)
ports.append(port2)
ports.append(port3)
ports.append(port4)
for line in open(file,'r'):
    curLine =line.strip().split(" ")
    #print(curLine)
    for word in curLine:
        for port in ports:
            if port in word:
                os.system("sudo kill -9 " + curLine[1])
