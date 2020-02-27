# -*- coding: utf-8 -*-
import pymongo
import re
from pyquery import PyQuery as pq
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep

from taobao.config import *

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]


# 定义一个taobao类
class weibo_infos:
    # 对象初始化
    def __init__(self):
        url = 'https://cn.bing.com/'
        self.url = url

        options = webdriver.ChromeOptions()
        options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})  # 不加载图片,加快访问速度
        options.add_experimental_option('excludeSwitches',
                                        ['enable-automation'])  # 此步骤很重要，设置为开发者模式，防止被各大网站识别出来使用了Selenium
        # options.add_argument('--headless')
        self.browser = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.browser, 10)  # 超时时长为10s

    # 登录淘宝
    def login(self, weibo_username, weibo_password):
        try:
            # 打开网页
            self.browser.get(self.url)

            # 等待 密码登录选项 出现
            password_login = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.qrcode-login > .login-links > .forget-pwd')))
            password_login.click()

            # 等待 微博登录选项 出现
            weibo_login = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.weibo-login')))
            weibo_login.click()

            # 等待 微博账号 出现
            weibo_user = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.username > .W_input')))
            weibo_user.send_keys(weibo_username)

            # 等待 微博密码 出现
            weibo_pwd = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.password > .W_input')))
            weibo_pwd.send_keys(weibo_password)

            # 等待 登录按钮 出现
            submit = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.btn_tip > a > span')))
            submit.click()

            # 直到获取到淘宝会员昵称才能确定是登录成功
            taobao_name = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                                          '.site-nav-bd > ul.site-nav-bd-l > li#J_SiteNavLogin > div.site-nav-menu-hd > div.site-nav-user > a.site-nav-login-info-nick ')))
            # 输出淘宝昵称
            print(taobao_name.text + '登陆成功')
        except TimeoutException:
            submit.click()
            # 直到获取到淘宝会员昵称才能确定是登录成功
            taobao_name = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                                          '.site-nav-bd > ul.site-nav-bd-l > li#J_SiteNavLogin > div.site-nav-menu-hd > div.site-nav-user > a.site-nav-login-info-nick ')))
            # 输出淘宝昵称
            print(taobao_name.text + '登陆成功')

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

    def next_page(self, page_num):
        print('当前页' + str(page_num))
        try:
            input = self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > input')))
            submit = self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit')))
            input.clear()
            input.send_keys(page_num)
            submit.click()
            self.wait.until(EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > ul > li.item.active > span'), str(page_num)))

        except TimeoutException:
            print('获取' + page_num + '页数据失败')
            self.next_page(page_num)

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
    a = weibo_infos()
    a.login("18144889905", "zxx1018")  # 登录
    a.search('美食')
