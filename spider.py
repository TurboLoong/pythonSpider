import json
import os
import re
from _md5 import md5
from multiprocessing import Pool
from urllib.parse import urlencode

import pymongo
import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException

from config import *

client = pymongo.MongoClient(MONGO_URL, connect=False)
db = client[MONGO_DB]
headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/50.0.2661.102 Safari/537.36 ',
    'cookie': 'tt_webid=6776170704401679880; s_v_web_id=658cfcef8ed101d429c98be3c376dadd; ' +
              'WEATHER_CITY=%E5%8C%97%E4%BA%AC; tt_webid=6776170704401679880;' +
              ' __tasessionId=z2x6hteod1577700203400; csrftoken=e16f32cac21bdd5a5cf9f3c81238192b',
    'x-requested-with': 'XMLHttpRequest'
}


def get_page_index(offset, keyword):
    data = {
        'aid': 24,
        'app_name': 'web_search',
        'offset': offset,
        'format': 'json',
        'keyword': keyword,
        'autoload': 'true',
        'count': '20',
        'en_qc': 1,
        'cur_tab': 1,
        'from': 'search_tab',
        'pd': 'synthesis',
        'timestamp': 1577700644547,
    }

    url = 'https://www.toutiao.com/api/search/content/?' + urlencode(data)
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('请求索引页面出错')
        return None


def parse_page_index(html):
    data = json.loads(html)
    if data and 'data' in data.keys():
        for item in data.get('data'):
            yield item


def get_page_detail(url):
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('请求详情页出错' + url)
        return None


def parse_page_detail(html, url):
    soup = BeautifulSoup(html, 'lxml')
    title = soup.select('title')[0].get_text()
    images_pattern = re.compile(r'gallery: JSON.parse[(](.*?)[)],', re.S)
    result = re.search(images_pattern, html)
    if result:
        data = json.loads(result.group(1))
        data = json.loads(data)
        if data and 'sub_images' in data.keys():
            sub_images = data.get('sub_images')
            images = [item.get('url') for item in sub_images]
            for image in images: download_image(image)
            return {
                'title': title,
                'url': url,
                'images': images
            }


def download_image(url):
    print('正在下载', url)
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            save_image(response.content)
        return None
    except RequestException:
        print('下载图片出错' + url)
        return None


def save_image(content):
    file_path = '{0}/{1}.{2}'.format(os.getcwd(), md5(content).hexdigest(), 'jpg')
    if not os.path.exists(file_path):
        with open(file_path, 'wb') as f:
            f.write(content)
            f.close()


def save_to_mongo(result):
    if db[MONGO_TABLE].insert_one(result):
        print('存储到DB成功', result)
        return True
    return False


def main(offset):
    html = get_page_index(offset, KEYWORD)
    for item in parse_page_index(html):
        if not item.get('abstract') is None and item.get('abstract') == '':
            html = get_page_detail(item.get('article_url'))
            if html:
                result = parse_page_detail(html, item.get('article_url'))
                if result: save_to_mongo(result)


if __name__ == '__main__':
    groups = [x * 20 for x in range(GROUP_START, GROUP_END + 1)]
    pool = Pool()
    pool.map(main, groups)
