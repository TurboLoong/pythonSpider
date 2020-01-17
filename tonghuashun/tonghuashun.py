# -*- coding: utf-8 -*-
import re
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


# 定义一个taobao类
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

    # 登录淘宝
    def main(self, stock):
        stock = str(stock)
        try:
            # 打开网页
            url = self.url.format(stock)
            self.browser.get(url)
            debt = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#cwzbDemo > div.sidenav > ul > li.current > a')))
            debt.click()
            simple = self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, '#cwzbTable > div.scroll_container > ul > li:nth-child(3) > a')))
            simple.click()
            html = self.browser.page_source
            doc = pq(html)
            items = doc('#cwzbTable .data_wraper > .tbody > tr ').items()
        except TimeoutException:
            print(stock + '主页获取失败')

    def search(self, key_words):
        try:
            Input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#q"))
            )
            submit = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_TSearchForm > div.search-button > button'))
            )
            Input.send_keys(key_words)
            submit.click()
            total_page = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                                                '#mainsrp-pager > div > div > div > div.total'))).text

            total = int(re.compile('(\d+)').search(total_page).group(1))
            for i in range(2, total + 1):
                self.get_products()
                self.swipe_down(0.2)
                self.next_page(i)
        except TimeoutException:
            self.search()

    def get_proxy(self):
        res = requests.get('http://localhost:5555/get')
        print('proxy', res.text)
        return res.text

    def get_products(self):
        print('存储产品')
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-itemlist .items .item')))
        html = self.browser.page_source
        doc = pq(html)
        items = doc('#mainsrp-itemlist .items .item').items()
        for item in items:
            product = {
                'image': item.find('.pic .img').attr('src'),
                'price': item.find('.price').text(),
                'deal': item.find('.deal-cnt').text()[:-3],
                'title': item.find('.title').text(),
                'location': item.find('.location').text(),
                'shop': item.find('.shop').text()
            }
            self.save_to_mongo(product)

    def swipe_down(self, second):
        for i in range(int(second / 0.1)):
            js = 'var q = document.documentElement.scrollTop=' + str(300 + 200 * i)
            self.browser.execute_script(js)
            sleep(0.1)
        js = "var q=document.documentElement.scrollTop=100000"
        self.browser.execute_script(js)
        sleep(0.2)

    def save_to_mongo(self, result):
        try:
            if db[MONGO_TABLE].insert_one(result):
                print('存储成功')
        except Exception:
            print('存储失效')


if __name__ == "__main__":
    page = tonghuashun_stock()
    page.main(601066)
    # page.search('美食')
