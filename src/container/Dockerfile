# recommend not to use the alpine one, it lacks lots of dependencies
# the slim one ocuppies about 2x space compared to alpine one
# FROM python:3.7-alpine
FROM python:3.7-slim

COPY pip.conf /etc/pip.conf

# fulfill the structure requirement of proxy
RUN mkdir /proxy
RUN pip3 install --upgrade pip
#RUN export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python 
RUN pip3 install --no-cache-dir gevent flask couchdb  grpcio==1.48.2 grpcio-tools==1.48.2 requests  redis 
# copy libs
COPY proxy.py /proxy/proxy.py
COPY main.py /proxy/main.py
RUN cat /proxy/main.py 
RUN echo "Hello World"
COPY xproto.sh /proxy/xproto.sh
#RUN pip3 install protobuf==3.19.6
RUN cat /proxy/xproto.sh

COPY object_store.proto /proxy/object_store.proto
RUN cat  /proxy/object_store.proto
# RUN cd /proxy
# RUN bash xproto.sh
COPY object_store_pb2_grpc.py /proxy/object_store_pb2_grpc.py
COPY object_store_pb2.py /proxy/object_store_pb2.py
RUN cat /proxy/object_store_pb2.py
RUN cat /proxy/object_store_pb2_grpc.py
COPY FreeStoreClient.py /proxy/FreeStoreClient.py
COPY config.py /proxy/config.py

WORKDIR /proxy

# proxy server runs under port 5000
EXPOSE 5000

# for alpine base only
# RUN apk update && \
#     apk add --no-cache --virtual .build-deps gcc musl-dev libffi-dev make && \
#     pip install --no-cache-dir gevent flask && \
#     apk del .build-deps
# RUN sed -i 's/deb.debian.org/mirrors.cloud.aliyuncs.com/g' /etc/apt/sources.list
RUN apt-get clean
RUN apt-get update 



CMD [ "python3", "/proxy/proxy.py" ]
