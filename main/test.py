import datetime
import random
import time

while True:
    # get sleeptime
    total_visit_num = 0
    succ_num = 0
    start_time = datetime.datetime.now()
    start_hour = int(start_time.strftime('%H'))

    while True:


        # count the total_visit_num and succ_num
        total_visit_num += 1
        x = 10*random.random()
        time.sleep(0.5)
        if x >= 5:
            succ_num += 1
        pv_log = "\rhour: {}, the overall progress of succ_num/total_visit_num: {}/{}".format(start_hour, succ_num,
                                                                                              total_visit_num)
        print(pv_log, end="")

        # if running for a hour, then quit and get the new sleeptime
        end_time = datetime.datetime.now()
        run_time = (end_time - start_time).seconds

        if run_time > 10:
            print("\n", "#"*20)
            break