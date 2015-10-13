# coding=utf-8
import socket
import json


class DubboException(Exception):
    def __init__(self, errno, msg, java_exception=None):
        self.errno = errno
        self.msg = msg

    def __str__(self):
        return 'Errno: %s, %s' % (self.errno, self.msg)

class JavaException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return 'Java Exception: \n %s' % self.msg

class Interface(object):
    def __init__(self, socket, path, interfaces, encoding='utf-8'):
        self.__socket = socket
        self.__path = path
        self.__cache_ls = []
        self.__encoding = encoding
        self.__interfaces = interfaces


    def __dir__(self):
        self.__socket.send(b'ls %s\r\n' % self.__path.encode(self.__encoding))
        ret = self.__socket.recv(102400)
        ls = ret.decode(self.__encoding).split('\r\n')[:-1]
        return ls

    def __getattr__(self, item):
        if item.startswith('__'):
            return super().__getattr__(item)
        return Interface(self.__socket, '%s.%s' % (self.__path, item), self.__interfaces, self.__encoding)

    def __call__(self, *args, **kwargs):
        command = 'invoke %s(%s)' % (self.__path, json.dumps(args)[1:-1])
        self.__socket.send(command.encode('utf-8') + b'\r\n')
        ret = self.__socket.recv(102400)
        try:
            ret_data, elapsed_time, prompt = ret.decode(self.__encoding).split('\r\n')
        except:
            raise JavaException(msg=ret.decode(self.__encoding).split('\r\n')[0])

        jdata = json.loads(ret_data)

        if not jdata['success']:
            raise DubboException(errno=jdata['code'], msg=jdata['message'])
        return jdata['model']


class DubboClient(object):

    def __init__(self, ip, port, encoding='utf-8'):
        self.__ip = ip
        self.__port = port
        self.__socket = socket.socket()
        # connect to dubbo server
        self.__socket.connect((ip, port))
        self.__cache_ls = []
        self.__encoding = encoding
        self.__dir__()

    def __getattr__(self, item):
        if item.startswith('__'):
            return self.__dict__[item]
        return Interface(self.__socket, item, self.__cache_ls, self.__encoding)

    def __dir__(self):
        self.__socket.send(b'ls\r\n')
        ret = self.__socket.recv(102400)
        self.__cache_ls = ret.decode(self.__encoding).split('\r\n')[:-1]
        return self.__cache_ls
