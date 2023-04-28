#run local_store_server 每台worker node都运行一个local store server，它作为grpc server,服务来自
#docker python grpc  client的请求
#同时收到grpc client请求后，处理，同时local store server作为grpc client,会与
#notification通信

cd FreeStore 

rm -rf build

mkdir build

cd build 

sudo cmake ..

sudo make  -j8

sudo ./local_store_server > local_store.log 2>&1  &