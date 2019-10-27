import os
from binascii import hexlify
import paramiko
import getpass
from utils import commonutils
import socket


class SSHDataSource(object):

    __host = ''
    __port = 22
    __user_name = ''
    __pass_word = ''
    __key_pass = ''

    def __init__(self,host,port=22,username=None,password=None,keypass=None):
        self.__host = host
        self.__port = port
        if commonutils.is_null(username):
            self.__user_name = getpass.getuser()
        else:
            self.__user_name = username
        self.__pass_word = password
        self.__key_pass = keypass


    def agent_auth(trnsprt, username):
        """
        Attempt to authenticate to the given transport using any of the private
        keys available from an SSH agent.
        """
        agent = paramiko.Agent()
        agent_keys = agent.get_keys()
        if len(agent_keys) == 0:
            return
        for key in agent_keys:
            print("Trying ssh-agent key %s" % hexlify(key.get_fingerprint()))
            try:
                trnsprt.auth_publickey(username, key)
                print("... success!")
                return
            except paramiko.SSHException:
                print("... nope.")

    def auth_by_pass(self,trnsprt,hostname,username=None,password=None,keypass=None):
        if username is None or len(username.strip()) < 1:
            username = getpass.getuser()
        path = os.path.join(os.environ["HOME"], ".ssh", "id_rsa")
        if len(path) != 0:
            try:
                key = paramiko.RSAKey.from_private_key_file(path)
            except paramiko.PasswordRequiredException:
                key = paramiko.RSAKey.from_private_key_file(path, keypass)
            trnsprt.auth_publickey(username, key)
            if  trnsprt.is_authenticated():
                return
            else:
                try:
                    key = paramiko.DSSKey.from_private_key_file(path)
                except paramiko.PasswordRequiredException:
                    key = paramiko.DSSKey.from_private_key_file(path, keypass)
                trnsprt.auth_publickey(username, key)
                if trnsprt.is_authenticated():
                    return
        if not username is None or len(password.strip()) > 0:
            trnsprt.auth_password(username, password)

    def conn_simple(self):
        # Paramiko client configuration
        UseGSSAPI = (
            paramiko.GSS_AUTH_AVAILABLE
        )  # enable "gssapi-with-mic" authentication, if supported by your python installation
        DoGSSAPIKeyExchange = (
            paramiko.GSS_AUTH_AVAILABLE
        )  # enable "gssapi-kex" key exchange, if supported by your python installation
        # UseGSSAPI = False
        # DoGSSAPIKeyExchange = False
        # now, connect and use paramiko Client to negotiate SSH2 across the connection
        try:
            client = paramiko.SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.WarningPolicy())
            print("*** Connecting...")
            if not UseGSSAPI and not DoGSSAPIKeyExchange:
                client.connect(self.__host, self.__port, self.__user_name, self.__pass_word)
            else:
                try:
                    client.connect(self.__host,self.__port,self.__user_name,gss_auth=UseGSSAPI,gss_kex=DoGSSAPIKeyExchange,)
                except Exception:
                    try:
                        client.connect(self.__host, self.__port, self.__user_name, self.__pass_word)
                    except Exception as e:
                        print("*** Connect failed: " + str(e))
                        try:
                            client.close()
                        except:
                            pass
                            return
            return client
        except Exception as e:
            print("*** Caught exception: %s: %s" % (e.__class__, e))
            try:
                client.close()
            except:
                pass

    def conn_socket(self):
        # now connect
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.__host, self.__port))
        except Exception as e:
            print("*** Connect failed: " + str(e))
            raise e
        try:
            tsport = paramiko.Transport(sock)
            try:
                tsport.start_client()
            except paramiko.SSHException as e:
                print("*** SSH negotiation failed.")
                raise e
            try:
                keys = paramiko.util.load_host_keys(
                    os.path.expanduser("~/.ssh/known_hosts")
                )
            except IOError:
                try:
                    keys = paramiko.util.load_host_keys(
                        os.path.expanduser("~/ssh/known_hosts")
                    )
                except IOError:
                    print("*** Unable to open host keys file")
                    keys = {}
            # check server's host key -- this is important.
            key = tsport.get_remote_server_key()
            if self.__host not in keys:
                print("*** WARNING: Unknown host key!")
            elif key.get_name() not in keys[self.__host]:
                print("*** WARNING: Unknown host key!")
            elif keys[self.__host][key.get_name()] != key:
                print("*** WARNING: Host key has changed!!!")
                return
            else:
                print("*** Host key OK.")

            self.agent_auth(tsport, self.__user_name)
            if not tsport.is_authenticated():
                self.auth_by_pass(self.__user_name, self.__host)
            if not tsport.is_authenticated():
                print("*** Authentication failed. :(")
                tsport.close()
                return

            return tsport.open_session()

        except Exception as e:
            print("*** Caught exception: " + str(e.__class__) + ": " + str(e))
            try:
                tsport.close()
            except:
                pass

