import asyncio

import grpc
import proto.math_pb2_grpc as math_pb2_grpc
import proto.craw_pb2_grpc as craw_pb2_grpc
from conf.logger import log_app, sgrid_application
from service import MathService, CrawService


async def serve(port):
    # port = sgrid_application.get_port()
    log_app.info(f"Starting server... to port {port}")
    # 创建一个 gRPC 服务器
    server = grpc.aio.server()
    # 注册 MathService 服务到服务器
    math_pb2_grpc.add_MathServiceServicer_to_server(MathService(), server)
    craw_pb2_grpc.add_CrawServiceServicer_to_server(CrawService(), server)
    # 绑定服务器地址和端口
    server.add_insecure_port(f'[::]:{port}')
    # 启动服务器
    await server.start()
    log_app.info(f"Server started, listening on port {port}")
    await server.wait_for_termination()


if __name__ == '__main__':
    asyncio.run(serve(sgrid_application.get_port()))
