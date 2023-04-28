
bash db_setup.bash 
cd ../src/workflow_manager
sudo bash master-lambda.sh > master-lambda.log 2>&1 &