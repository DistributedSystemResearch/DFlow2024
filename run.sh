bash kill-docker.sh
docker start redis 
cd ./scripts/scripts/

bash xport.sh 

cd ../../FreeFaaSStore

#mkdir build
cd build 

cmake  -DCMAKE_BUILD_TYPE=Release ..
make -j16 

./local_store_server > local.log 2>&1  & 

code local.log 

docker start redis 

cd ../../scripts

bash flask_server.sh &


cd ../StoneFlow  


bash run.sh &
