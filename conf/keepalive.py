import threading
import time

import grpc
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2

from conf import sgrid_application

log_keepalive = sgrid_application.create_logger("log_keepalive")


class Empty:
    pass


class BaseGrpcConn:
    conns = []
    service = None
    channels: list[grpc.Channel] = []
    stubs = []

    def __init__(self, conns, service):
        self.conns = conns
        self.service = service
        self.channels = []
        self.stubs = []


# 代理管理类
class ProxyManager:
    proxy_dict: dict[str, BaseGrpcConn]

    def __init__(self, proxy_dict: dict[str, BaseGrpcConn]):
        self.proxy_dict = proxy_dict
        servers = self.proxy_dict.keys()
        for server in servers:
            grpc_config = proxy_dict[server]
            for conn in grpc_config.conns:
                channel = grpc.insecure_channel(conn)
                grpc_config.channels.append(channel)
                stub = grpc_config.service(channel)
                grpc_config.stubs.append(stub)

        # 启动 keep_alive 任务
        keep_alive_thread = threading.Thread(target=self.keep_alive)
        keep_alive_thread.daemon = True  # 设置为守护线程，主线程退出时该线程也会退出
        keep_alive_thread.start()

    # 每个 BaseGrpcConfig 的 conn 都是一个 grpc 连接，每个连接都要有一个grpc方法
    def keep_alive(self):
        servers = self.proxy_dict.keys()
        while True:
            for svrName in servers:
                grpc_conn = self.proxy_dict[svrName]
                index = 0
                for stub in grpc_conn.stubs:
                    try:
                        index += 1
                        conn = grpc_conn.conns[index-1]
                        log_keepalive.info("心跳检测开始 %s %s ", svrName, conn)
                        resp = None
                        try:
                            resp = stub.T_KeepAlive(google_dot_protobuf_dot_empty__pb2.Empty())
                        except grpc.RpcError as e:
                            log_keepalive.info("心跳检测出错 %s %s ", svrName, e)
                        log_keepalive.info("心跳检测结果 %s %s", svrName, resp)
                        flag = resp is not None
                        if flag:
                            log_keepalive.info("连接正常 %s %s ", svrName, flag)
                        else:
                            log_keepalive.info("尝试重新连接..")
                            while True:
                                # 重新连接
                                log_keepalive.info("重新连接中... {}".format(conn))
                                channel = grpc.insecure_channel(conn)
                                stub = grpc_conn.service(channel)
                                resp = stub.T_KeepAlive(google_dot_protobuf_dot_empty__pb2.Empty())
                                retry_flag = resp is not None
                                log_keepalive.info("重新连接结果: {} {}".format(svrName, resp))
                                if retry_flag:
                                    log_keepalive.info("重新连接成功: {} {}".format(svrName, retry_flag))
                                    grpc_conn.channels[index - 1] = channel
                                    grpc_conn.stubs[index - 1] = stub
                                    break
                                else:
                                    log_keepalive.info("重新连接失败: ")
                                    time.sleep(5)
                    except Exception as e:
                        log_keepalive.info("重新连接出错: {}".format(e))
                        time.sleep(5)
            time.sleep(10)

    def invoke(self, service_name: str, method_name: str, req):
        grpc_config = self.proxy_dict[service_name]
        if not grpc_config.service:
            raise Exception("service not found")
        log_keepalive.info("grpc_config.stubs: %s", grpc_config.stubs[0])
        method = getattr(grpc_config.stubs[0], method_name)
        if not method:
            raise Exception("method not found")
        rsp = method(req)
        return rsp

