import os
file = './port.log'

ports = []
port1 ="23567"
port2 = "8000"
port3 = "9999"

ports.append(port1)
ports.append(port2)
ports.append(port3)
for line in open(file,'r'):
    curLine =line.strip().split(" ")
    #print(curLine)
    for word in curLine:
        for port in ports:
            if port in word:
                os.system("sudo kill -9 " + curLine[1])