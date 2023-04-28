CURRENT_TIME=$(date '+%Y-%m-%d-%H-%M-%S')  

python3 run.py --datamode=raw > cflow-data_overhead____CURRENT_TIME${CURRENT_TIME}.log 2>&1 &

code cflow-data_overhead____CURRENT_TIME${CURRENT_TIME}.log 