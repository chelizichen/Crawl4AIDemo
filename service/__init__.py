import grpc
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
import proto.math_pb2 as math_pb2
import proto.math_pb2_grpc as math_pb2_grpc
import proto.craw_pb2 as craw_pb2
import proto.craw_pb2_grpc as craw_pb2_grpc
from conf import log_craw, log_math
from service.craw import craw_instance


# 实现 MathService 服务
class MathService(math_pb2_grpc.MathServiceServicer):
    def __init__(self):
        log_math.info(f"MathService init called")

    def T_KeepAlive(self, request, context):
        log_math.info("MathService >> T_KeepAlive called")
        context.set_code(grpc.StatusCode.OK)
        return google_dot_protobuf_dot_empty__pb2.Empty()

    def Add(self, request, context):
        # 计算两个整数的和
        result = request.num1 + request.num2
        return math_pb2.AddResponse(result=result)


# 实现 MathService 服务
class CrawService(craw_pb2_grpc.CrawServiceServicer):
    def __init__(self):
        log_craw.info(f"CrawService init called")

    def T_KeepAlive(self, request, context):
        log_craw.info("CrawService >> T_KeepAlive called")
        return google_dot_protobuf_dot_empty__pb2.Empty()

    def CrawWithURL(self, request, context):
        try:
            log_craw.info(f"craw with url >> {request.url}")
            rsp = craw_instance.submit_and_wait(request_data={
                "urls": request.url,
            })
            log_craw.info(f"craw with url rsp >>  {rsp}")
            context.set_code(grpc.StatusCode.OK)
            return craw_pb2.CrawWithURLResponse(data=rsp, code=0, msg="ok")
        except Exception as e:
            # Record exception information
            log_craw.error(f"Error occurred while crawling with URL {request.url}: {e}")
            # Set the gRPC status code to indicate an internal error
            context.set_code(grpc.StatusCode.INTERNAL)
            # Set an error message to be returned to the client
            context.set_details(str(e))
            # Return an empty response or a response indicating the error
            return craw_pb2.CrawWithURLResponse(data=None, code=1, msg=str(e))
