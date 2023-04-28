# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import object_store_pb2 as object__store__pb2


class NotificationServerStub(object):
    """message HelloRequest {
    bytes req_data = 1;
    }

    message HelloReply {
    bytes resp_data = 1;
    }
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.WriteLocation = channel.unary_unary(
                '/objectstore.NotificationServer/WriteLocation',
                request_serializer=object__store__pb2.WriteLocationRequest.SerializeToString,
                response_deserializer=object__store__pb2.WriteLocationReply.FromString,
                )
        self.GetLocationSync = channel.unary_unary(
                '/objectstore.NotificationServer/GetLocationSync',
                request_serializer=object__store__pb2.GetLocationSyncRequest.SerializeToString,
                response_deserializer=object__store__pb2.GetLocationSyncReply.FromString,
                )


class NotificationServerServicer(object):
    """message HelloRequest {
    bytes req_data = 1;
    }

    message HelloReply {
    bytes resp_data = 1;
    }
    """

    def WriteLocation(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetLocationSync(self, request, context):
        """rpc Ping(HelloRequest) returns (HelloReply) ;
        rpc HandlePullObjectFailure(HandlePullObjectFailureRequest) returns (HandlePullObjectFailureReply);
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_NotificationServerServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'WriteLocation': grpc.unary_unary_rpc_method_handler(
                    servicer.WriteLocation,
                    request_deserializer=object__store__pb2.WriteLocationRequest.FromString,
                    response_serializer=object__store__pb2.WriteLocationReply.SerializeToString,
            ),
            'GetLocationSync': grpc.unary_unary_rpc_method_handler(
                    servicer.GetLocationSync,
                    request_deserializer=object__store__pb2.GetLocationSyncRequest.FromString,
                    response_serializer=object__store__pb2.GetLocationSyncReply.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'objectstore.NotificationServer', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class NotificationServer(object):
    """message HelloRequest {
    bytes req_data = 1;
    }

    message HelloReply {
    bytes resp_data = 1;
    }
    """

    @staticmethod
    def WriteLocation(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/objectstore.NotificationServer/WriteLocation',
            object__store__pb2.WriteLocationRequest.SerializeToString,
            object__store__pb2.WriteLocationReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetLocationSync(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/objectstore.NotificationServer/GetLocationSync',
            object__store__pb2.GetLocationSyncRequest.SerializeToString,
            object__store__pb2.GetLocationSyncReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)


class LocalStoreServerStub(object):
    """service LocalStoreServer {
    rpc Put(stream PutRequest) returns (PutReply) {}
    rpc Get(GetRequest) returns (stream GetReply) {}
    //rpc Put(PutRequest) returns (PutReply);
    //rpc Get(GetRequest) returns (GetReply);
    }

    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Put = channel.unary_unary(
                '/objectstore.LocalStoreServer/Put',
                request_serializer=object__store__pb2.PutRequest.SerializeToString,
                response_deserializer=object__store__pb2.PutReply.FromString,
                )
        self.Get = channel.unary_unary(
                '/objectstore.LocalStoreServer/Get',
                request_serializer=object__store__pb2.GetRequest.SerializeToString,
                response_deserializer=object__store__pb2.GetReply.FromString,
                )
        self.PutGlobalInput = channel.unary_unary(
                '/objectstore.LocalStoreServer/PutGlobalInput',
                request_serializer=object__store__pb2.PutGlobalInputRequest.SerializeToString,
                response_deserializer=object__store__pb2.PutGlobalInputReply.FromString,
                )


class LocalStoreServerServicer(object):
    """service LocalStoreServer {
    rpc Put(stream PutRequest) returns (PutReply) {}
    rpc Get(GetRequest) returns (stream GetReply) {}
    //rpc Put(PutRequest) returns (PutReply);
    //rpc Get(GetRequest) returns (GetReply);
    }

    """

    def Put(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Get(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def PutGlobalInput(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_LocalStoreServerServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Put': grpc.unary_unary_rpc_method_handler(
                    servicer.Put,
                    request_deserializer=object__store__pb2.PutRequest.FromString,
                    response_serializer=object__store__pb2.PutReply.SerializeToString,
            ),
            'Get': grpc.unary_unary_rpc_method_handler(
                    servicer.Get,
                    request_deserializer=object__store__pb2.GetRequest.FromString,
                    response_serializer=object__store__pb2.GetReply.SerializeToString,
            ),
            'PutGlobalInput': grpc.unary_unary_rpc_method_handler(
                    servicer.PutGlobalInput,
                    request_deserializer=object__store__pb2.PutGlobalInputRequest.FromString,
                    response_serializer=object__store__pb2.PutGlobalInputReply.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'objectstore.LocalStoreServer', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class LocalStoreServer(object):
    """service LocalStoreServer {
    rpc Put(stream PutRequest) returns (PutReply) {}
    rpc Get(GetRequest) returns (stream GetReply) {}
    //rpc Put(PutRequest) returns (PutReply);
    //rpc Get(GetRequest) returns (GetReply);
    }

    """

    @staticmethod
    def Put(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/objectstore.LocalStoreServer/Put',
            object__store__pb2.PutRequest.SerializeToString,
            object__store__pb2.PutReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Get(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/objectstore.LocalStoreServer/Get',
            object__store__pb2.GetRequest.SerializeToString,
            object__store__pb2.GetReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def PutGlobalInput(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/objectstore.LocalStoreServer/PutGlobalInput',
            object__store__pb2.PutGlobalInputRequest.SerializeToString,
            object__store__pb2.PutGlobalInputReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
