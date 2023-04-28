### 优化global input 
- 每台worker node服务器起一个flask server,接受来自master node机器的global_input,master node通过requests.post发过来
- 每台worker node服务器收到请求后，调用python  grpc client的PutGloabl接口，将数据发给local store server 
- 文件:server.py/FreeStoreClient.py 