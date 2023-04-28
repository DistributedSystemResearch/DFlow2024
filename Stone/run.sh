mkdir build

cd build

cmake ..

make  -j16 

./main > flow.log 2>&1 &

code flow.log 

