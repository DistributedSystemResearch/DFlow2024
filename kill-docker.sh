# docker rm -f `docker ps -a | grep Created  | awk '{print $1}'`

# docker rm -f `docker ps -a | grep Dead  | awk '{print $1}'`

# docker rm -f `docker ps -a | grep Exited  | awk '{print $1}'`

# docker rm -f `docker ps -a | grep Up*  | awk '{print $1}'`

docker rm -f $(docker ps -aq --filter label=workflow)