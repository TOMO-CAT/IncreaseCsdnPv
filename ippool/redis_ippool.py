import redis
import json

"""
IPPool function：
1) insert_ip: insert a proxy ip into redis
2) get_random_key: get a random key from redis
3) delete_by_key: delete a proxy ip by key
"""
class IPPool(object):
    def __init__(self):
        self.__HOST = '127.0.0.1'
        self.__PORT = 6379
        self.__IPPOOL_DB = 0
        self.__REDIS_CONN = redis.Redis(host=self.__HOST, port=self.__PORT, db=self.__IPPOOL_DB)

    def insert_ip(self, ip):
        # insert ip into redis
        # example of ip:['163.204.245.227', '9999', '广东', '高匿', 'HTTPS']
        # redis_conn = redis.Redis(host=self.__HOST, port=self.__PORT, ippool=self.__IPPOOL_DB)

        # construct key and value
        ip_with_port = str(ip[0]) + ":" + str(ip[1])
        # print("key:", ip_with_port)
        ip_info = json.dumps(ip)
        # print("value:", ip_info)
        self.__REDIS_CONN.set(ip_with_port, ip_info)

    def get_random_key(self):
        # select a random key from redis
        # redis_conn = redis.Redis(host=self.__HOST, port=self.__PORT, ippool=self.__IPPOOL_DB)
        # decode: transfer byte type to string type
        random_key = self.__REDIS_CONN.randomkey().decode()
        return random_key

    def delete_by_key(self, key):
        self.__REDIS_CONN.delete(key)
        return None # 无返回值

    def get_proxy_ip_cnt(self):
        return len(self.__REDIS_CONN.keys())

if __name__ == "__main__":
    ip_example = ['182.35.85.193', '9999', '山东泰安', '高匿', 'HTTP']
    test = IPPool()
    test.insert_ip(ip_example)
    print("Info: get a random key from IPPool")
    print(test.get_random_key())
    print(test.get_proxy_ip_cnt())
