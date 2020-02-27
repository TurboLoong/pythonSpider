from urllib.parse import urlencode

import requests
from pyquery import PyQuery as pq

base_url = 'https://weixin.sogou.com/weixin?'

headers = {
    'Cookie': 'SUV=00FC437170C192D25B91400FDAB74471; SUID=D292C1703320910A000000005B94B04A; ssuid=4568505316; GOTO=Af99047; SMYUV=1563680569390023; UM_distinctid=16c527712721b2-0439167de0bdca-c343162-1fa400-16c52771273bb; ABTEST=1|1578120667|v1; IPLOC=CN5101; weixinIndexVisited=1; SNUID=BFDE94C7B7BD2CFD57EE0606B8AEA427; JSESSIONID=aaahzfL75i3fRaeVdhB9w; sct=3; ppinf=5|1578121561|1579331161|dHJ1c3Q6MToxfGNsaWVudGlkOjQ6MjAxN3x1bmlxbmFtZTo1NjpUdXJib0xvb25nLSVFNSU4OSU4RCVFNyVBQiVBRiVFNSVCNyVBNSVFNyVBOCU4QiVFNSVCOCU4OHxjcnQ6MTA6MTU3ODEyMTU2MXxyZWZuaWNrOjU2OlR1cmJvTG9vbmctJUU1JTg5JThEJUU3JUFCJUFGJUU1JUI3JUE1JUU3JUE4JThCJUU1JUI4JTg4fHVzZXJpZDo0NDpvOXQybHVPLURZNUZpVS1wMmJacVIwNlhhQnVjQHdlaXhpbi5zb2h1LmNvbXw; pprdig=wLUNEJNGh2Stzl9swNNQdmZx4t3UE8glHfxbApplACmt80hXFTGzzMuvBm7sPUdM8RZYWaFt-81C2TwPN4W7GOSNa1c2PY5F__uOpGA9ZAmilQI4SM4c87su4iAFEXwzcBAI2GOdWv-tGNnkw9bn9cpzjQ_50T8GPnH7acRDsOM; sgid=22-45042051-AV4QOVn9KqW7A1btBMAv92Q',
    'Host': 'weixin.sogou.com',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'
}
keyword = '风景'

proxy_pool_url = 'http://127.0.0.1:5000/get'
proxy = None
max_count = 5
count = 0


def parse_html(html):
    doc = pq(html)
    items = doc('.news-box .news-list li .txt-box h3 a').items()
    return ['https://weixin.sogou.com' + item.attr('href') for item in items]


def get_detail(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            response.encoding = 'utf-8'
            return response.text
        return None
    except ConnectionError:
        return None


def get_proxy():
    try:
        response = requests.get(proxy_pool_url)
        if response.status_code == 200:
            return response.text
        return None
    except ConnectionError:
        return None


def get_html(url, count=1):
    print('Crawling url', url)
    print('trying count', count)
    if count == max_count:
        print('over max count')
        return None
    global proxy
    try:
        if proxy:
            curr_proxy = {
                'http': 'http://' + proxy
            }
            print('current proxy', proxy)
            response = requests.get(url, allow_redirects=False, headers=headers, proxies=curr_proxy)
        else:
            response = requests.get(url, allow_redirects=False, headers=headers)
        if response.status_code == 200:
            return response.text
        if response.status_code == 302:
            # 如果是302，更换代理
            print(302)
            proxy = get_proxy()
            if proxy:
                print('Using proxy: ', proxy)
                return get_html(url)
            else:
                print('Get Proxy Failed')
                return None
    except ConnectionError as e:
        print(e.args)
        proxy = get_proxy()
        count += 1
        return get_html(url, count)


def get_index(key_word, page):
    data = {
        'query': key_word,
        'type': 2,
        'page': page
    }
    queries = urlencode(data)
    url = base_url + queries
    html = get_html(url)
    return html


def main():
    for page in range(1, 2):
        html = get_index(keyword, page)
        if html:
            article_urls = parse_html(html)
            for article_url in article_urls:
                content = get_detail(article_url)
                print(content)


if __name__ == '__main__':
    main()
