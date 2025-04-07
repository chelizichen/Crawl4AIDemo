# 定义初始化配置的函数
from conf.conf import SgridApplication


def init_application():
    # 创建 SgridConfig 实例
    app = SgridApplication()
    # 初始化配置
    app.init_config()
    return app


sgrid_application = init_application()


