# from crawl4ai import AsyncWebCrawler, __version__
# print("crawl4ai ==>", __version__)

import requests
import time

from conf.logger import log_craw_service


class Crawl4AiService:
    def __init__(self, base_url: str = "http://127.0.0.1:11235"):
        self.base_url = base_url

    def submit_and_wait(self, request_data: dict, timeout: int = 300, rsp_type: str = "markdown") -> dict:
        # Submit crawl job
        log_craw_service.info("request_data: %s | timeout %s | rsp_type %s", request_data, timeout, rsp_type)
        response = requests.post(f"{self.base_url}/crawl", json=request_data,
                                 headers={"Authorization": "Bearer " + "Leecumulus21"})
        log_craw_service.debug("response %s", response)
        task_id = response.json()["task_id"]
        log_craw_service.info("task_id %s", task_id)
        # Poll for result
        start_time = time.time()
        while True:
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Task {task_id} timeout")
            result = requests.get(f"{self.base_url}/task/{task_id}",
                                  headers={"Authorization": "Bearer " + "Leecumulus21"})
            status = result.json()
            if status["status"] == "completed":
                log_craw_service.debug("status %s", status['result']['markdown'])
                log_craw_service.info("result keys %s", status['result'].keys())
                return status['result'][rsp_type]

            time.sleep(2)


craw_instance = Crawl4AiService()

if __name__ == "__main__":
    # test
    craw_instance.submit_and_wait(request_data={
        "urls": "https://blog.csdn.net/ayushu/article/details/128245134",
    })
