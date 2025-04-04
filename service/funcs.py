from crawl4ai import AsyncWebCrawler, __version__

print("crawl4ai ==>", __version__)


async def craw_with_url(target_url: str):
    """
    craw_with_url 方法的实现
    :param target_url: 包含 URL 的请求
    :return: 包含爬取结果的响应，Markdown 格式
    """
    async with AsyncWebCrawler(verbose=True) as crawler:
        result = await crawler.arun(
            url=target_url)
    return result.markdown
