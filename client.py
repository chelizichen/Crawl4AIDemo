import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import proto.math_pb2 as math_pb2
import proto.craw_pb2 as craw_pb2
import proto.math_pb2_grpc as math_pb2_grpc
import proto.craw_pb2_grpc as craw_pb2_grpc
from conf import sgrid_application
from conf.keepalive import BaseGrpcConn, ProxyManager

math_grpc_config = BaseGrpcConn(["localhost:9011"],
                                math_pb2_grpc.MathServiceStub,
                                )
craw_grpc_config = BaseGrpcConn(["localhost:9011"],
                                craw_pb2_grpc.CrawServiceStub,
                                )
grpc_services = {
    "craw": craw_grpc_config,
    "math": math_grpc_config,
}

proxy_manager = ProxyManager(grpc_services)
app = FastAPI()
origins = sgrid_application.get("cors_origins")

print(f"添加跨域支持 origins {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/add/{num1}/{num2}")
async def add_numbers(num1: int, num2: int):
    print("add_numbers", num1, num2)
    request = math_pb2.AddRequest(num1=num1, num2=num2)
    response = proxy_manager.invoke("math", "Add", request)
    return {"result": response.result}


@app.get("/craw")
async def add_numbers(request_url: str):
    print("craw", request_url)
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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=14332)
