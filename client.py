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
from bs4 import BeautifulSoup

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
async def craw_with_url(request_url: str, css_selector: str = None, rsp_type: str = None):
    log_client.info("craw request_url %s | css_selector %s | rsp_type %s ", request_url, css_selector, rsp_type)
    # 创建 gRPC 请求
    request = craw_pb2.CrawWithURLRequest(
        url=request_url,
        css_selector=css_selector,
        rsp_type=rsp_type,
    )
    response = proxy_manager.invoke("craw", "CrawWithURL", request)
    return {
        "result": response.data,
        "code": response.code,
        "msg": response.msg
    }


class FinancialData:
    link: str
    title: str
    id: str
    content: str
    interpret: str

    def __init__(self):
        pass

    def set_link(self, link: str):
        if link.startswith("https://www.cls.cn"):
            self.link = link
        else:
            self.link = "https://www.cls.cn" + link
        self.id = link.split("/")[-1]

    def set_title(self, title):
        self.title = title

    def set_content(self, content):
        self.content = content

    def set_interpret(self, interpret):
        self.interpret = interpret

    @staticmethod
    def validate_tag(tag):
        if tag.name != 'a':
            return False
        link = tag.attrs.get("href")
        if link.startswith("/detail/") is False:
            return False
        link_id = link.split("/")[-1]
        if link_id.isdigit() is False:
            return False
        return True


@app.get("/craw1")
async def craw_with_url1(request_url: str, css_selector: str = None, rsp_type: str = None):
    log_client.info("craw request_url %s | css_selector %s | rsp_type %s ", request_url, css_selector, rsp_type)
    # 创建 gRPC 请求
    request = craw_pb2.CrawWithURLRequest(
        url=request_url,
        css_selector=css_selector,
        rsp_type=rsp_type,
    )
    response = proxy_manager.invoke("craw", "CrawWithURL", request)
    soup = BeautifulSoup(response.data, 'html.parser')
    tags = soup.find_all(attrs={"rel": "noopener noreferrer"})
    FinancialDatas = []
    for i, tag in enumerate(tags, 1):

        if FinancialData.validate_tag(tag) is False:
            continue
        log_client.info(f"   链接: {tag.get('href', '无')}")
        log_client.info(f"\n{i}. 标签名称: {tag.name}")
        log_client.info(f"   属性: {tag.attrs}")
        log_client.info(f"   文本内容: {tag.text.strip() if tag.text else '无'}")

        f = FinancialData()
        f.set_link(tag.attrs.get("href"))
        f.set_title(tag.text.strip())
        FinancialDatas.append(f)
    FinancialDatas = FinancialDatas[:5]
    for f in FinancialDatas:
        log_client.info("爬取的链接 %s", f.link)
    for f in FinancialDatas:
        req_data = craw_pb2.CrawWithURLRequest(
            url=f.link,
            css_selector="div.content-left",
            rsp_type="markdown",
        )
        response = proxy_manager.invoke("craw", "CrawWithURL", req_data)
        log_client.info("爬取的链接 %s", f.link)
        log_client.debug("爬取的内容 %s", response.data)
        f.set_content(response.data)

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
