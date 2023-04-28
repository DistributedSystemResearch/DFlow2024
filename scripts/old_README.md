### 节点机器设置
- 先跑 worker node
    - 先跑worker_setup.bash
    - 一个窗口然后跑run_local_store_server.sh
    - 接着跑run_flask_server.sh 
- master节点
    - 一个窗口跑run_notification.sh，这个比worker node需要更早跑起来
    - 先跑db_setup.bash 
    - 然后跑