# -*- coding: utf-8 -*-
from time import sleep

import pymongo
import requests
from config import *
from pyquery import PyQuery as pq
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]


class tonghuashun_stock:
    # 对象初始化
    def __init__(self):
        self.url = 'http://basic.10jqka.com.cn/{}/finance.html'

        options = webdriver.ChromeOptions()
        options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})  # 不加载图片,加快访问速度
        options.add_experimental_option('excludeSwitches',
                                        ['enable-automation'])  # 此步骤很重要，设置为开发者模式，防止被各大网站识别出来使用了Selenium
        options.add_argument('--headless')
        self.browser = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.browser, 10)  # 超时时长为10s

    def main(self, stock):
        stock = str(stock)
        try:
            # 打开网页
            url = self.url.format(stock)
            self.browser.get(url)
            # 点击资产负债表
            debt = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#cwzbDemo > div.sidenav > ul > li:nth-child(2) > a')))
            debt.click()

        except TimeoutException:
            print(stock + '主页获取失败')

    def get_proxy(self):
        res = requests.get('http://localhost:5555/get')
        print('proxy', res.text)
        return res.text

    def get_debt(self):
        # 等待资产负债表的数据出现
        self.wait.until(EC.text_to_be_present_in_element(
            (By.CSS_SELECTOR,
             '#cwzbTable > .scroll_container > .table_data > .left_thead > .tbody > tbody > tr:nth-child(1) > th'),
            '资产(元)'))
        html = self.browser.page_source
        doc = pq(html)
        data_body = doc('.cwzb_table>.scroll_container>.table_data>.data_wraper>.data_tbody')
        dates = [v.text() for v in data_body.find('.top_thead>tbody').eq(1).find('.td_w').items()]
        keys = [v.text() for v in doc('.cwzb_table .table_data .left_thead>.tbody').find('tr:not(.unclick)>th').items()
                if v.text()]
        for index, date in enumerate(dates):
            self.get_by_report(index + 1, date, keys, data_body)

    def get_by_report(self, report, date, keys, father_body_ele):
        datas = father_body_ele.find('.tbody tr td:nth-child({})'.format(report)).items()
        datas = [v.text() for v in datas if v.text()]
        result = {}
        for index, item in enumerate(keys):
            result[item] = datas[index]

    def get_by_year(self):
        print('year')
    def swipe_down(self, second):
        for i in range(int(second / 0.1)):
            js = 'var q = document.documentElement.scrollTop=' + str(300 + 200 * i)
            self.browser.execute_script(js)
            sleep(0.1)
        js = "var q=document.documentElement.scrollTop=100000"
        self.browser.execute_script(js)
        sleep(0.2)

    def save_to_mysql(self, result):
        try:
            if db[MONGO_TABLE].insert_one(result):
                print('存储成功')
        except Exception:
            print('存储失效')


if __name__ == "__main__":
    page = tonghuashun_stock()
    page.main(601066)
    page.get_debt()
