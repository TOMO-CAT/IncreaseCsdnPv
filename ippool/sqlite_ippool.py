"""
sqlite_ippool.py
IPPool function: back up for redis
1) create: create a table
2) insert
3) select
4) delete
"""


import sqlite3

class IPPool(object):
    def __init__(self,table_name):
        self.__table_name = 'validation_ip_table'
        self.__database_name = "IP.ippool"

    def create(self):
        conn = sqlite3.connect(self.__database_name, isolation_level = None)
        conn.execute(
            "create table if not exists %s(IP CHAR(20) UNIQUE, PORT INTEGER, ADDRESS CHAR(50), TYPE CHAR(50), PROTOCOL CHAR(50))"
            % self.__table_name)
        print("Info: create table %s successfully" % self.__table_name)

    def insert(self, ip):
        conn = sqlite3.connect(self.__database_name, isolation_level = None)
        # set isolation_level to None then we don't need to commit every time
        for one in ip:
            conn.execute(
                "insert or ignore into %s(IP, PORT, ADDRESS, TYPE, PROTOCOL) values (?,?,?,?,?)"
                % (self.__table_name), (one[0], one[1], one[2], one[3], one[4]))
        conn.commit()
        conn.close()

    def select(self, random_flag = False):
        conn = sqlite3.connect(self.__database_name, isolation_level = None)
        # use cursor to get return result
        cur=conn.cursor()

        if random_flag:
            cur.execute("select * from %s order by random() limit 1"% self.__table_name)
            result = cur.fetchone()
        else:
            cur.execute("select * from %s" % self.__table_name)
            result = cur.fetchall()
        cur.close()
        conn.close()
        return result

    def get_random_ip(self):
        raw_ip_info = self.select(random_flag=True)
        IP = str(raw_ip_info[0]) + ":" + str(raw_ip_info[1])
        return {"http": "http://" + IP}

    def delete(self, IP = ('1',1,'1','1','1'), delete_all=False):
        conn = sqlite3.connect(self.__database_name,isolation_level = None)
        if not delete_all:
            n = conn.execute("delete from %s where IP=?" % self.__table_name,
                        (IP[0],))
            print("Info: delete ", n.rowcount, " record")
        else:
            n = conn.execute("delete from %s" % self.__table_name)
            print("Info: delete all data，the cnt is ", n.rowcount)
        conn.close()

if __name__ == "__main__":
    conn = sqlite3.connect('IP.ippool', isolation_level = None)

    cur = conn.cursor()
    cur.execute("select * from %s order by random() limit 1" % 'validation_ip_table')
    result = cur.fetchone()
    print(result)

    test = IPPool('validation_ip_table')
    print("Test: connect to IP.ippool successfully")
    proxy_ip = test.get_random_ip()
    print("Test: get a random proxy from sqlite: {}".format(proxy_ip))
