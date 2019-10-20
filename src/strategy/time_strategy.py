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
            return 1
        if now_hour >= 7 and now_hour <= 10:
            return 1
        else:
            return 1

if __name__ == "__main__":
    test = TimeStrategy()
    print(test.get_sleeptime_by_hour())
