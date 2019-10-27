from aboutdatabase.DataSource import DataSource



if __name__=='__main__':
    connparams = ('192.168.1.155',3309,'super','8845','purchasers')
    ds = DataSource(connparams)
    conn = ''
    try:
        conn = ds.get_conn()
        cursor = conn.cursor()
        cursor.execute('show tables')
        for i in cursor.fetchall():
            print(i)
    finally:
        conn.close()


