from asyncio import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-automation'])
brower = webdriver.Chrome(options=options)
brower.execute_script('Object.defineProperties(navigator,{webdriver:{get:()=>false}})')
wait = WebDriverWait(brower, 10)


def swipe_down(self, second):
    for i in range(int(second / 0.1)):
        js = "var q=document.documentElement.scrollTop=" + str(300 + 200 * i)
        self.browser.execute_script(js)
        sleep(0.1)
    js = "var q=document.documentElement.scrollTop=100000"
    self.browser.execute_script(js)
    sleep(0.2)


def search():
    brower.get('https://www.taobao.com/')
    # try:
    Input = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#q"))
    )
    submit = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_TSearchForm > div.search-button > button')))
    Input.send_keys('美食')
    submit.click()


# finally:
#     brower.quit()


def main():
    search()


if __name__ == '__main__':
    main()
