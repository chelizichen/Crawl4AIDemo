import asyncio
import threading

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import proto.math_pb2 as math_pb2
import proto.craw_pb2 as craw_pb2
import proto.math_pb2_grpc as math_pb2_grpc
import proto.craw_pb2_grpc as craw_pb2_grpc
from conf import sgrid_application
from conf.keepalive import BaseGrpcConn, ProxyManager
from conf.logger_client import log_client

math_grpc_config = BaseGrpcConn(
    sgrid_application.get("math_grpc_config"),
    math_pb2_grpc.MathServiceStub,
)
craw_grpc_config = BaseGrpcConn(
    sgrid_application.get("craw_grpc_config"),
    craw_pb2_grpc.CrawServiceStub,
)
grpc_services = {
    "craw": craw_grpc_config,
    "math": math_grpc_config,
}

proxy_manager = ProxyManager(grpc_services)
app = FastAPI()
origins = sgrid_application.get("cors_origins")

log_client.info(f"添加跨域支持 origins {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/add/{num1}/{num2}")
async def add_numbers(num1: int, num2: int):
    log_client.info("add_numbers", num1, num2)
    request = math_pb2.AddRequest(num1=num1, num2=num2)
    response = proxy_manager.invoke("math", "Add", request)
    return {"result": response.result}


@app.get("/craw")
async def add_numbers(request_url: str):
    log_client.info("craw", request_url)
    # 创建 gRPC 请求
    request = craw_pb2.CrawWithURLRequest(
        url=request_url
    )
    response = proxy_manager.invoke("craw", "CrawWithURL", request)
    return {
        "result": response.data,
        "code": response.code,
        "msg": response.msg
    }


port = sgrid_application.get_port(default=14332)


def run_client():
    log_client.info("启动客户端，端口 %s ", port)
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    def run_serve():
        from server import serve
        asyncio.run(serve(port + 1))


    if sgrid_application.is_production is False:
        log_client.info("开始启动 子服务")
        # 创建并启动线程
        serve_thread = threading.Thread(target=run_serve)
        serve_thread.start()
        log_client.info("********* 启动完成 *********")
    run_client()
