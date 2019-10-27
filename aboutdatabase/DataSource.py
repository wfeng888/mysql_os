import mysql.connector
from DBUtils.PooledDB import PooledDB

from aboutdatabase.exceptions import ParamsNotMatch


class DataSource:
    _user_name = ''
    _pass_word = ''
    _host = ''
    _port = 0
    _data_base = ''

    def set_class_attr(self, *connParams):
        self._host = connParams[1]
        self._port = connParams[2]
        self._user_name = connParams[3]
        self._pass_word = connParams[4]
        self._data_base = connParams[5]

    def __init__(self, value):
        if isinstance(value, (tuple, list)):
            self.set_class_attr(self, *value)
        elif isinstance(value, dict):
            self.set_class_attr(self, *(value['host'], value['port'], value['user'], value['password'],value['database']))
        else:
            raise ParamsNotMatch('database connection parames not match ')

    def get_conn(self):
        pool = PooledDB(mysql.connector,maxcached=8,maxconnections=50,**{'user':self._user_name,'password':self._pass_word,'host':self._host,'port':self._port,'database':self._data_base})
        return pool.dedicated_connection()

