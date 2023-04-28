### 测试2
- 先python3 get.py 然后python3 put.py,测试阻塞机制

### 测试4
- 边A->B,A->C

- 代码 APut.py、BGet.py、CGet.py 

- 情况1:A和B在同一台机器上,C在另一台机器(见目录test4-1)
    - 测试阻塞机制与唤醒机制
    - B C先执行python3 xGet.py(这里的x可以是B也可以是C),然后A执行python3 APut.py
    - <font color=Green  >**设想:B和C都被阻塞，A put成功后，唤醒B和C</font>**
    - <font color=#FF000 > **如果实现对了，那么B C能拿到对应的数据</font>**

- 情况2:A和B在同一台机器，C在另一台机器(见目录test4-2)
    - A先python3 APut.py ，然后B和C执行python3 xGet.py
    - <font color=Pure >  **如果实现对了,B和C能拿到对应的数据 </font>**

- 情况3:A和B在同一台机器，C在另一台机器(见目录test4-3)
    - B python3 BGet.py,然后A python3 APut.py,C python3 CGet.py
    - <font color= Yellow>**设想:B被阻塞，A put成功后，唤醒B,C可能被阻塞，然后被A唤醒，也可能直接取到数据** </font>

- 情况4:A B C在一台机器上(见目录test4-4)
    - 先运行python3 xGet.py(x可能是B或者C),然后运行python3 APut.py
    - <font color= Green> **测试B和C被阻塞后,然后被唤醒，B和C可以拿到正确的数据** </font>
    - <font color= Red> **设想:B和C能被阻塞，然后被唤醒，然后拿到正确的数据** </font>