apt install libssl-dev 
cd 

git clone git@github.com:lambda7xx/cpr.git

cd cpr 

mkdir  build

cd build

cmake ..
make && sudo make install 


cd  #回到根目录

git clone git@github.com:sogou/workflow.git

cd workflow

make && sudo make install 

cd  #回到根目录

git clone git@github.com:wfrest/wfrest.git

cd wfrest

mkdir build

cd build

cmake .. 

make  && sudo make install 


