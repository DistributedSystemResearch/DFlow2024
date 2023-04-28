import os 

file = "ps.log"
tag = '"python3'
res =  [] 
i = 1
for line in open(file,'r'):
    curLine =line.strip().split(" ")
    if tag in curLine:
        res.append(curLine[0])

print(res)