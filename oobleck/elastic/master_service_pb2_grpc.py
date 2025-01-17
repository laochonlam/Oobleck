# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""

import grpc
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2

import oobleck.elastic.master_service_pb2 as master__service__pb2


class OobleckMasterStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetDistInfo = channel.unary_unary(
            "/OobleckMaster/GetDistInfo",
            request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            response_deserializer=master__service__pb2.DistInfo.FromString,
        )
        self.GetCode = channel.unary_unary(
            "/OobleckMaster/GetCode",
            request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            response_deserializer=master__service__pb2.CodeInfo.FromString,
        )
        self.SetMasterRankPort = channel.unary_unary(
            "/OobleckMaster/SetMasterRankPort",
            request_serializer=master__service__pb2.PortInfo.SerializeToString,
            response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
        )
        self.GetMasterRankPort = channel.unary_unary(
            "/OobleckMaster/GetMasterRankPort",
            request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            response_deserializer=master__service__pb2.PortInfo.FromString,
        )
        self.WatchReconfigurationNotification = channel.unary_stream(
            "/OobleckMaster/WatchReconfigurationNotification",
            request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            response_deserializer=master__service__pb2.DistInfo.FromString,
        )
        self.KillAgent = channel.unary_unary(
            "/OobleckMaster/KillAgent",
            request_serializer=master__service__pb2.AgentInfo.SerializeToString,
            response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
        )


class OobleckMasterServicer(object):
    """Missing associated documentation comment in .proto file."""

    def GetDistInfo(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def GetCode(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def SetMasterRankPort(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def GetMasterRankPort(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def WatchReconfigurationNotification(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def KillAgent(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")


def add_OobleckMasterServicer_to_server(servicer, server):
    rpc_method_handlers = {
        "GetDistInfo": grpc.unary_unary_rpc_method_handler(
            servicer.GetDistInfo,
            request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            response_serializer=master__service__pb2.DistInfo.SerializeToString,
        ),
        "GetCode": grpc.unary_unary_rpc_method_handler(
            servicer.GetCode,
            request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            response_serializer=master__service__pb2.CodeInfo.SerializeToString,
        ),
        "SetMasterRankPort": grpc.unary_unary_rpc_method_handler(
            servicer.SetMasterRankPort,
            request_deserializer=master__service__pb2.PortInfo.FromString,
            response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
        ),
        "GetMasterRankPort": grpc.unary_unary_rpc_method_handler(
            servicer.GetMasterRankPort,
            request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            response_serializer=master__service__pb2.PortInfo.SerializeToString,
        ),
        "WatchReconfigurationNotification": grpc.unary_stream_rpc_method_handler(
            servicer.WatchReconfigurationNotification,
            request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            response_serializer=master__service__pb2.DistInfo.SerializeToString,
        ),
        "KillAgent": grpc.unary_unary_rpc_method_handler(
            servicer.KillAgent,
            request_deserializer=master__service__pb2.AgentInfo.FromString,
            response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        "OobleckMaster", rpc_method_handlers
    )
    server.add_generic_rpc_handlers((generic_handler,))


# This class is part of an EXPERIMENTAL API.
class OobleckMaster(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def GetDistInfo(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/OobleckMaster/GetDistInfo",
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            master__service__pb2.DistInfo.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def GetCode(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/OobleckMaster/GetCode",
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            master__service__pb2.CodeInfo.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def SetMasterRankPort(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/OobleckMaster/SetMasterRankPort",
            master__service__pb2.PortInfo.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def GetMasterRankPort(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/OobleckMaster/GetMasterRankPort",
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            master__service__pb2.PortInfo.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def WatchReconfigurationNotification(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_stream(
            request,
            target,
            "/OobleckMaster/WatchReconfigurationNotification",
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            master__service__pb2.DistInfo.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def KillAgent(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/OobleckMaster/KillAgent",
            master__service__pb2.AgentInfo.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )
