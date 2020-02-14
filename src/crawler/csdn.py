import sys
sys.path.append('..')
import random
from crawler.random_header import RandomFakeHeaders
from ippool.redis_ippool import IPPool
import requests
import time
from bs4 import BeautifulSoup
import re

class CSDN(object):
    def __init__(self):
        self.__home_page = "https://blog.csdn.net/TOMOCAT"

    @staticmethod
    def visit_csdn(url, retry_time = 3):
        response = None
        for i in range(retry_time):
            try:
                headers = RandomFakeHeaders().random_headers_for_csdn()
                ip = IPPool().get_random_key()
                proxies = {"http": "http://" + ip}
                response = requests.get(url = url, headers= headers, proxies = proxies)

                if response.status_code == 200:
                    break
                else:
                    print("Warning: visit url %s failed, sleep 5 second to retry..." %url)
                    time.sleep(5)
                    continue
            except:
                print("Fatal: visit url %s fail, please check the network" %url)
                return None
        if response.status_code != 200:
            return None
        else:
            return response


    def get_article_info(self):
        page_num = 1
        all_article_infos = []

        while True:
            sleep_time = 6 * random.random()
            article_list_url = self.__home_page + "/article/list/{}".format(page_num)
            print("Info: now we are visiting %s..."%article_list_url)

            response = self.visit_csdn(article_list_url)
            # print("Debug: " + response.text)
            if response == None:
                print("Fatal: get article info from %s fail" %article_list_url)
            article_infos = self.__parse_html_to_article_info(response.text)
            # print("Debug: " + article_infos)

            if article_infos is None:
                print("Fatal: parse html to article info fail")
                return None
            if len(article_infos)>0:
                all_article_infos += article_infos
            else:
                break

            print("Info: now sleep for %d second..." %sleep_time)
            time.sleep(sleep_time)
            page_num += 1

        print("Info: have already visited all the article list page")
        return all_article_infos

    @staticmethod
    def __parse_html_to_article_info(html):
        article_infos = []
        soup = BeautifulSoup(html, "html.parser")
        try:
            contents = soup.find_all("div", {"class", "article-item-box csdn-tracking-statistics"})
        except Exception:
            print("Fatal: parse html failed, please check the html")
            return None
        for content in contents:
            try:
                article_info = {}
                article_info['id'] = content.attrs['data-articleid']
                article_info['href'] = content.a.attrs['href']
                article_info['title'] = re.sub(r"\s+|\n", "", content.a.get_text())
                article_info['date'] = content.find("span", {"class": "date"}).get_text()
                str_temp = content.find_all("span", {"class": "read-num"})
                article_info['read_num'] = int(re.findall(r'\d+', str_temp[0].get_text())[0])
                article_info['commit_num'] = int(re.findall(r"\d+", str_temp[1].get_text())[0])

                # avoid anti-crawler strategy
                if (article_info['id'] == '82762601') | (article_info['title'] == '原帝都的凛冬'):
                    continue
                else:
                    article_infos.append(article_info)
                print("Info: parse content successfully")
            except Exception:
                print("Fatal: parse content failed")
                continue
        return article_infos


    @staticmethod
    def get_total_pv(article_info):
        return 0

if __name__ == "__main__":
    # unit test
    test = CSDN()
    article_list_url = "https://blog.csdn.net/TOMOCAT/article/list/1"
    response = test.visit_csdn(article_list_url)
    if response.status_code == 200:
        print("Test: get response from url successfully")
    else:
        print("Test: get response fail")
    soup = BeautifulSoup(response.text, "html.parser")
    contents = soup.find_all("div", {"class", "article-item-box csdn-tracking-statistics"})
    if contents != None:
        print("Tets: get contents successfully")
    # print(contents)
    article_infos = []
    try:
        for content in contents:
            article_info = {}
            article_info['id'] = content.attrs['data-articleid']
            article_info['href'] = content.a.attrs['href']
            article_info['title'] = re.sub(r"\s+|\n", "", content.a.get_text())
            article_info['date'] = content.find("span", {"class": "date"}).get_text()
            str_temp = content.find_all("span", {"class": "read-num"})
            article_info['read_num'] = int(re.findall(r'\d+', str_temp[0].get_text())[0])
            article_info['commit_num'] = int(re.findall(r"\d+", str_temp[1].get_text())[0])

            # avoid anti-crawler strategy
            if (article_info['id'] == '82762601') | (article_info['title'] == '原帝都的凛冬'):
                continue
            else:
                article_infos.append(article_info)
            print("Info: parse content successfully")
    except Exception:
        print("Fatal: parse content failed")
    print(article_infos)

    # overall test
    test = CSDN()
    all_infos = test.get_article_info()
    print(all_infos)
