from __future__ import print_function
import logging
import object_store_pb2
import object_store_pb2_grpc
import grpc
import json


class FreeStore():
    def __init__(self):
        self.channel  = grpc.insecure_channel('localhost:9999',options=[
            ('grpc.max_send_message_length', -1),
            ('grpc.max_receive_message_length',-1),],) #4GB
        self.stub = object_store_pb2_grpc.LocalStoreServerStub(self.channel)
    def PuStream(S)