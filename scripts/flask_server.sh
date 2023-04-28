#flask server处理global input的问题
#global input主要是针对科学计算的benchmark,这些有global input
#对于global input的处理是将global input广播到每台worker机器
#worker机器会运行一个flask server,然后收到global input后，调用python grpc client
#将这个global input发给local_store_server,对于这些global_input,local_store_server直接存在local_store里
#不需要与notification交互
#因为每台worker机器都有一份global input
cd ../src/local_server
bash build.sh
bash proto.sh 
python3 proxy.py