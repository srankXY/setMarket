# -*- utf-8 -*-
# 示例程序：万金油selenium版本

import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

class SET(object):

    def __init__(self):

        options = Options()

        # 判断系统类型
        if os.name == "posix":
            options.add_argument('--headless')

        # 稳定性、日志参数等
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('log-level=3')
        options.add_argument('--disable-gpu')

        # selenium控制加载模式
        options.page_load_strategy = 'normal'

        # 反爬相关
        options.add_experimental_option(
            "excludeSwitches", ["enable-automation"]
            # 'excludeSwitches', ['enable-logging']
        )
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('lang=zh-CN,zh,zh-TW,en-US,en')
        options.add_argument(
            '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36')
        options.add_argument("--disable-blink-features=AutomationControlled")

        # 加载选项
        self.browser = webdriver.Chrome(options=options)

        # 固定窗口
        self.browser.set_window_size(width=945, height=1020)
        # 显式等待
        self.browser.implicitly_wait(10)

        # js2次伪装
        self.browser.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': 'delete navigator.__proto__.webdriver',
        })

    # 详情页函数
    def SYMBOL(self, symbol_name: str):

        # 重组详情页url并进入
        symbol_url = "https://www.set.or.th/en/market/product/stock/quote/%s/price" % symbol_name

        self.browser.get(symbol_url)

        # 获取最新价
        last = self.browser.find_element(By.XPATH, '//div[contains(@class, "price-info-stock-detail-box")][1]'
                                                   '/div[1]/span').text

        return last

    # 核心函数
    def MARKET(self, base_url: str):

        # 打开行情页
        self.browser.get(base_url)

        # 获取symbol列表对象
        symbols_ele = self.browser.find_elements(By.XPATH, '//a[contains(@class,"text-symbol")]/div[1]')

        # 组装symbol 迭代器
        def toMap(e):
            return e.text
        symbols = list(map(toMap, symbols_ele))
        # print("当前查询币种列表为: %s" % symbols)

        # 获取详情信息
        market_data = {}
        for i in symbols:
            market_data[i] = self.SYMBOL(i)

        return json.dumps(market_data)

if __name__ == '__main__':

    # AGRI - Agribusiness 分类下股票
    url = "https://www.set.or.th/en/market/index/set/agro/agri"
    app = SET()
    app.MARKET(base_url=url)
