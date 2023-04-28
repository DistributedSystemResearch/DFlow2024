CURRENT_TIME=$(date '+%Y-%m-%d-%H-%M-%S')  

python3 run.py --datamode=optimized > faasflow-data_overhead____CURRENT_TIME${CURRENT_TIME}.log 2>&1 &

code faasflow-data_overhead____CURRENT_TIME${CURRENT_TIME}.log 