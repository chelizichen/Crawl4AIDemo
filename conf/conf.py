import logging
import os
import re
from logging.handlers import TimedRotatingFileHandler

from typing_extensions import Union

from yaml import load, FullLoader, parse
from pathlib import Path

__conf__ = "SGRID_CONFIG"
__process_index__ = "PROCESS_INDEX"


class SgridConfig:
    config: Union[dict, None]

    def __init__(self, config_file="sgrid.yml"):
        self.config = None
        self.config_file = config_file

    def init_config(self):
        # yaml_text = """
        # server:
        #   name: DeepSeekServer
        #   host: 127.0.0.1
        #   port: 14232
        #   protocol: http
        #   language: python
        #   version: 3.10.12
        # config:
        #   api_key: sk-f0e1e656ba294b98a7ed892781df1ce9
        #   db: mysql+pymysql://root:lzy20211121@124.220.19.199:3306/t_ai
        # """
        # os.environ.setdefault("SGRID_CONFIG", yaml_text)
        sgrid_conf = os.environ.get(__conf__)
        if sgrid_conf:
            print(f"Sgrid-Python[{__conf__}] Prod", True)
            print("Sgrid-Python[conf]", sgrid_conf)
            try:
                config = load(sgrid_conf, Loader=FullLoader)
                self.config = config
                print("Sgrid-Python[self.config]", self.config)
            except Exception as e:
                print(f"Sgrid-Python[Error] Failed to parse {__conf__}: {e}")
            return
        cwd = os.getcwd()
        filepath = Path(cwd).joinpath(self.config_file)
        print("Sgrid-Python[read conf path]", filepath)
        with open(filepath, encoding="utf-8") as f:
            config = load(f, Loader=FullLoader)
            print("Sgrid-Python[conf] ==>", config)
            self.config = config

    # get ("server.port")
    def get(self, path, default=None):
        """
        :param path: 用点号分隔的键路径，例如 'a.b.c'
        :param default: 如果路径不存在，返回的默认值
        :return: 配置项的值，如果路径不存在则返回默认值
        """
        keys = path.split('.')
        current = self.config
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current

    def get_port(self):
        port = os.environ.get("SGRID_TARGET_PORT")
        if port:
            print("load env port")
            return int(port)
        if self.config is not None:
            print("load config port")
            return int(self.get("server.port", 8080))
        return 8080


class SgridApplication(SgridConfig):

    def __init__(self, config_file="sgrid.yml"):
        super().__init__(config_file)


    def get_server_name(self) -> str:
        return self.get("server.name")

    def create_logger(self, name: str) -> logging.Logger:
        svr = self.get_server_name()
        print(f"Sgrid-Python[create_logger] [svr={svr}] [name={name}]")
        """
        # 输出不同等级的日志
        # logger.debug('这是一条 DEBUG 级别的日志')
        # logger.info('这是一条 INFO 级别的日志')
        # logger.warning('这是一条 WARNING 级别的日志')
        # logger.error('这是一条 ERROR 级别的日志')
        # logger.critical('这是一条 CRITICAL 级别的日志')
        """
        if name.endswith(".log"):
            raise ValueError("logger not end with .log , just need name")
        is_sgrid = os.environ.get(__conf__)
        # 创建日志记录器
        logger = logging.getLogger(name)
        # 设置日志记录器的等级为 DEBUG
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(message)s')
        if is_sgrid is not None:
            # 创建文件处理器
            # file_path =
            log_dir = os.environ.get("SGRID_LOG_DIR")
            if log_dir is None:
                log_dir = os.getcwd()
            filename = f"{name}.log"  # 修改文件名格式
            filepath = Path(log_dir).joinpath(filename)

            file_handler = TimedRotatingFileHandler(
                filename=filepath,
                when='midnight',  # 每天午夜轮转
                interval=1,
                encoding='utf-8',
                backupCount=30,
                utc=True  # 使用UTC时间保证时间一致性
            )
            # 设置文件处理器的等级为 INFO
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(formatter)
            file_handler.suffix = "%Y%m%d"  # 修改后缀匹配格式
            file_handler.extMatch = re.compile(r"^\d{8}$")  # 匹配8位数字日期
            logger.addHandler(file_handler)
            return logger

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        return logger

    @classmethod
    def get_thread_lock(self) -> bool:
        index = os.environ.get(__process_index__)
        if index is None:
            return True
        if index == "0":
            return True
        return False
