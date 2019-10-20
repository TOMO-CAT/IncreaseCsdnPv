## 引言
爬虫是`python`数据分析难以绕开的一块，合理的爬虫可以促进信息的流通。但为了防止恶意爬虫给服务器带来的巨大压力，反爬虫策略也应运而生。我之前在一家比较大的内容信息平台实习过，在统计`pv`的时候经常需要“去爬去刷”，本文以`csdn`为例，简单写一个爬虫小程序实现提高访问量的功能来帮助大家了解爬虫与反爬虫的一些基本知识。

## 工程目录
```
├── ippool  //提供代理IP
│   ├── IP.db  //作为备份的sqlite数据库
│   ├── redis_ippool.py  //代理IP的redis数据库
│   ├── sqlite_ippool.py  //代理IP的sqlite数据库
├── crawler  //模拟浏览器访问 
│   ├── csdn.py  //获取csdn博文列表和访问csdn博文
│   ├── random_header  //获取随机请求头
├── README.md  //帮助文档  
├── proxy_getter  
│   ├── get_proxy.py  //从xici获取爬虫代理IP到数据库  
│   ├── random_headers.py  //获取随机请求头 
├── strategy  //反爬虫策略层  
│   ├── pv_strategy  //根据不同文章的浏览量决定访问频率
│   ├── time_strategy  //根据一天的不同时间决定访问频率
├── main  //主函数
│   ├── main.py  
```

## 实现的主要思路
#### 1.获取文章信息
如果要实现刷量的话，首先需要拿到每篇文章的`url`，所幸`csdn`文章列表都在该链接：
> https://blog.csdn.net/TOMOCAT/article/list/${index}

```python
    def get_article_info(self):
        page_num = 1
        all_article_infos = []

        while True:
            sleep_time = 6 * random.random()
            article_list_url = self.__home_page + "/article/list/{}".format(page_num)
            print("Info: now we are visiting %s..."%article_list_url)

            response = self.visit_csdn(article_list_url)
            if response == None:
                print("Fatal: get article info from %s fail" %article_list_url)
            article_infos = self.__parse_html_to_article_info(response.text)

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
        except Exception:
            print("Fatal: parse html failed, please check the html")
            return None
        return article_infos
```
#### 2.实现代理IP访问
对反爬策略稍微了解的同学应该都知道需要使用代理IP（我之前的文章有教如何从零构建自己的爬虫代理池），另外还需要伪造`headers`和`reference`。
```python
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
```

#### 3.反爬策略
一个是`pv_strategy`，即刷`pv`的量和该文章原本的访问量就正相关，伪造自然访问。具体的实现思路：
> 根据单篇文章访问量占总访问量求得该文章的访问概率，然后构造文章访问量的概率密度函数，生成随机数决定访问哪篇文章。

```python
"""
pv_strategy.py
function: provide url according to pv
"""
import random

class PvStrategy(object):
    # return the probability distribution of url according to pv
    @staticmethod
    def probability_distribution_url(article_info):
        urls = [one['href'] for one in article_info]
        read_nums = [int(one['read_num']) for one in article_info]

        total_read_nums = sum(read_nums)
        url_with_pv = [(url, read_num) for url, read_num in zip(urls, read_nums)]
        sorted_url_with_pv = sorted(url_with_pv)
        read_nums = [one[1] for one in sorted_url_with_pv]
        urls = [one[0] for one in sorted_url_with_pv]

        probabilitys = [read_num/total_read_nums for read_num in read_nums]
        sorted_url_with_prob = [(url, prob) for url, prob in zip(urls, probabilitys)]
        return sorted_url_with_prob

    # provide random url of article according to its page view
    @staticmethod
    def get_random_url_arrcording_to_pv(sorted_url_with_prob):
        urls = [one[0] for one in sorted_url_with_prob]
        probs = [one[1] for one in sorted_url_with_prob]

        accumulate_probs = [sum(probs[0:i+1]) for i in range(len(probs))]
        r = random.random()
        # generate random url according to accumulate_probs
        if r <= accumulate_probs[0]:
            return(urls[0])
        else:
            for index in range(1, len(accumulate_probs)):
                if (r > accumulate_probs[index-1]) and (r <= accumulate_probs[index]):
                    return urls[index]
```
另一个是`time_strategy`，模拟正常情况下一天的访问频率，即白天时间访问频率高，深更半夜访问频率低。可以根据自己的思路调整，我这里只做了一个粗略的版本。
```python
"""
time_strategy.py
function: provide view frequency according to time
"""
import datetime
class TimeStrategy(object):
    @staticmethod
    def get_sleeptime_by_hour():
        now_hour = datetime.datetime.now().strftime('%H')
        now_hour = int(now_hour)
        if now_hour >= 11 and now_hour < 24:
            return 4
        if now_hour >= 7 and now_hour <= 10:
            return 8
        else:
            return 10
```

#### 4.main work
```python
if __name__ == "__main__":
    # 1) get article info: article url and read_num
    print("#"*80)
    print("get the article info from csdn...")
    print("#" * 80)
    csdn = CSDN()
    article_info = csdn.get_article_info()

    # 2) use pv strategy to get url's probability
    print("#" * 80)
    print("generate the urls with probability...")
    print("#" * 80)
    url_with_prob = PvStrategy().probability_distribution_url(article_info)

    # 3) main work
    print("#" * 80)
    print("start to increase page view...")
    print("#" * 80)
    while True:
    # get sleeptime
        sleeptime = TimeStrategy().get_sleeptime_by_hour()
        total_visit_num = 0
        succ_num = 0
        start_time = datetime.datetime.now()
        start_hour = int(start_time.strftime('%H'))
        while True:
            # count the total_visit_num and succ_num
            total_visit_num += 1
            target_url = PvStrategy().get_random_url_arrcording_to_pv(url_with_prob)
            response = csdn.visit_csdn(target_url)
            if not response is None:
                succ_num += 1
            pv_log = "\rhour: {}, the overall progress of succ_num/total_visit_num: {}/{}".format(start_hour, succ_num, total_visit_num)
            print(pv_log, end = "")

            # if running for a hour, then quit and get the new sleeptime
            end_time = datetime.datetime.now()
            run_time = (end_time - start_time).seconds

            # sleep for a while to avoid anti-crawler
            time.sleep(random.random() * sleeptime)
            if run_time > 60 * 60:  # 3600 seconds equal to a hour
                print("\n", end = "")
                break
```


## 日志样例
> 首先遍历文章列表获取所有文章信息，然后根据每篇文章的访问量计算累积概率密度函数。开始刷量时会给出当前时间（不同时间对应的刷量频率是不同的，主要是应对反爬策略），然后实时更新该小时内的成功数和总数（当发现成功率下降即是需要更新代理IP了）。如果访问失败，会给出"Fatal"并另起一行统计访问信息。
```
################################################################################
get the article info from csdn...
################################################################################
Info: now we are visiting https://blog.csdn.net/TOMOCAT/article/list/1...
Info: now sleep for 2 second...
Info: now we are visiting https://blog.csdn.net/TOMOCAT/article/list/2...
Info: now sleep for 1 second...
Info: now we are visiting https://blog.csdn.net/TOMOCAT/article/list/3...
Info: now sleep for 2 second...
Info: now we are visiting https://blog.csdn.net/TOMOCAT/article/list/4...
Info: now sleep for 5 second...
Info: now we are visiting https://blog.csdn.net/TOMOCAT/article/list/5...
Info: now sleep for 0 second...
Info: now we are visiting https://blog.csdn.net/TOMOCAT/article/list/6...
Info: now sleep for 5 second...
Info: now we are visiting https://blog.csdn.net/TOMOCAT/article/list/7...
Info: now sleep for 1 second...
Info: now we are visiting https://blog.csdn.net/TOMOCAT/article/list/8...
Info: now sleep for 4 second...
Info: now we are visiting https://blog.csdn.net/TOMOCAT/article/list/9...
Info: now sleep for 1 second...
Info: now we are visiting https://blog.csdn.net/TOMOCAT/article/list/10...
Info: now sleep for 3 second...
Info: now we are visiting https://blog.csdn.net/TOMOCAT/article/list/11...
Info: now sleep for 3 second...
Info: now we are visiting https://blog.csdn.net/TOMOCAT/article/list/12...
Info: have already visited all the article list page
################################################################################
generate the urls with probability...
################################################################################
################################################################################
start to increase page view...
################################################################################
hour: 22, the overall progress of succ_num/total_visit_num: 2662/2662
hour: 23, the overall progress of succ_num/total_visit_num: 709/709Fatal: visit url https://blog.csdn.net/TOMOCAT/article/details/84969578 fail, please check the network
hour: 23, the overall progress of succ_num/total_visit_num: 2233/2234Fatal: visit url https://blog.csdn.net/TOMOCAT/article/details/82684466 fail, please check the network
hour: 23, the overall progress of succ_num/total_visit_num: 2574/2576
hour: 0, the overall progress of succ_num/total_visit_num: 1481/1481
hour: 1, the overall progress of succ_num/total_visit_num: 1479/1479
hour: 2, the overall progress of succ_num/total_visit_num: 1274/1274Fatal: visit url https://blog.csdn.net/TOMOCAT/article/details/78723277 fail, please check the network
hour: 2, the overall progress of succ_num/total_visit_num: 1274/1275Fatal: visit url https://blog.csdn.net/TOMOCAT/article/details/79091842 fail, please check the network
hour: 2, the overall progress of succ_num/total_visit_num: 1274/1276
```

## 写在最后
合适的爬虫对信息流通是有益的，但是暴力爬虫不可取。瞎爬不仅会给别人的服务器带来巨大的压力而且还会给双方造成较大的麻烦，写这篇文章只是给大家科普一下刷量的概念和一些简单的爬虫与反爬虫知识，共勉~