from crawler.csdn import CSDN
from strategy.pv_strategy import PvStrategy
from strategy.time_strategy import TimeStrategy
import datetime
import time
import random



if __name__ == "__main__":
    # 1) get article info: article url and read_num
    print("#" * 80)
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