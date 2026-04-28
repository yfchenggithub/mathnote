import os
from playwright.sync_api import sync_playwright

# 1. 在导入和启动之前，手动指定浏览器内核的存放路径
# 这样 Playwright 就会去这个位置找 chromium，而不是去 C:\Users\乱码... 下找
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = r"D:\PlaywrightBrowsers"

with sync_playwright() as p:
    # 启动浏览器（默认无头模式，这里设为有界面查看）
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    # 访问网页
    page.goto("https://www.baidu.com")

    # 输入内容并回车
    page.fill("#kw", "Playwright 教程")
    page.keyboard.press("Enter")

    # 等待一会儿查看结果并截图
    page.wait_for_timeout(3000)
    page.screenshot(path="result.png")

    browser.close()
