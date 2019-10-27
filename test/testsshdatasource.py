from aboutssh.SSHDataSource import SSHDataSource
if __name__ == '__main__':
    ds = SSHDataSource('192.168.1.155',username='root',password='8845')
    client = ds.conn_simple()
    stdin, stdout, stderr = client.exec_command('ls -l /')
    print('stdin: %s' % stdin)
    print('stdout: %s' % stdout)
    print('stderr: %s' % stderr)
    client.close()