"""
random_header.py
function: provide random headers for crawler
"""
from fake_useragent import UserAgent
import random

class RandomFakeHeaders(object):
    def __init__(self):
        self.__CSDN_REFERER = [
            "https://www.google.com.hk/", "https://cn.bing.com/",
            "https://www.baidu.com/", "https://blog.csdn.net/TOMOCAT",
        ]
        self.__XICI_REFERER = [
            "https://www.baidu.com/s?wd=%E8%A5%BF%E5%88%BA&rsv_spt=1&rsv_iqid=0xc1588bae0009dc70&issp=1&f=8&rsv_bp=1&rsv_idx=2&ie=utf-8&rqlang=cn&tn=baiduhome_pg&rsv_enter=0&rsv_dl=tb&oq=Do%2520you%2520need%2520to%2520install%2520a%2520parser%2520library&rsv_t=bc8dYJxmE1XHedb7zcu2axFtAmjEt%2BAoBI7IFR8oZjQZv%2FH9FdyNVymCHAxnFPwLat2d&inputT=3735&rsv_pq=f061bc24001f3088&rsv_sug3=195&rsv_sug1=69&rsv_sug7=100&rsv_sug2=0&rsv_sug4=4998",
            "https://blog.csdn.net/fitz1318/article/details/79463472",
        ]
        self.__VALID_REFERER = [
            "https://zhuanlan.zhihu.com/p/45093545",
            "https://www.baidu.com/s?wd=%E7%88%AC%E8%99%AB&rsv_spt=1&rsv_iqid=0xc1588bae0009dc70&issp=1&f=8&rsv_bp=1&rsv_idx=2&ie=utf-8&rqlang=cn&tn=baiduhome_pg&rsv_enter=0&rsv_dl=tb&oq=b&rsv_t=7ef0FnAfNLK3ecVn2Nsz6p696SDSWBQ%2Ffs90HHqIOi4XwAPjB%2BXpz5rykgx1wqJrmKks&inputT=1372&rsv_pq=df111c830004dea5&rsv_sug3=216&rsv_sug2=0&prefixsug=%25E7%2588%25AC%25E8%2599%25AB&rsp=1&rsv_sug4=2326",
        ]

    def random_headers_for_xici(self):
        headers = {
            "User-Agent": UserAgent().random,
            "Referer": random.choice(self.__XICI_REFERER),
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Host": "www.xicidaili.com",
            "Upgrade-Insecure-Requests": "1"
        }
        return headers

    def random_headers_for_csdn(self):
        headers = {
            "User-Agent":
                UserAgent().random,  ##随机选择UA
            "Referer":
                random.choice(self.__CSDN_REFERER),
            "Accept-Language":
                "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept":
                "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding":
                "gzip, deflate, br",
            "Cache-Control":
                "max-age=0",
            "Connection":
                "keep-alive",
            "Host":
                "blog.csdn.net",
            "Upgrade-Insecure-Requests":
                "1"
        }
        return headers

    def random_headers_for_validation(self):
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "close",
            "Host": "httpbin.org",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": UserAgent().random,
            "Referer": random.choice(self.__VALID_REFERER)
        }
        return headers

if __name__ == "__main__":
    print("Info: generate 20 random headers for xici:")
    for i in range(20):
        print(RandomFakeHeaders().random_headers_for_xici())
    print("Info: generate 20 random headers for csdn:")
    for i in range(20):
        print(RandomFakeHeaders().random_headers_for_csdn())
    print("Info: generate a random headers for validation:")
    print(RandomFakeHeaders().random_headers_for_validation())