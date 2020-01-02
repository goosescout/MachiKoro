import socket

from utility import MyThread


class Node:
    def __init__(self, port=11719):
        self.ip = socket.gethostbyname(socket.gethostname())
        self.port = port
        
    def send(self, data, ip=None):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, True)
        if ip is None:
            for i in range(256):
                sock.sendto(bytes(str(data), encode='utf-8'), (f'192.168.1.{i}', self.port))
        else:
            sock.sendto(bytes(str(data), encode='utf-8'), (ip, self.port))

    def recieve(self, var):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, True)
        sock.bind(('0.0.0.0', self.port))

        message = sock.recv(128)
        var = eval(message.decode('utf-8'))
        return eval(message.decode('utf-8'))

    def await_recieve(self, data, match=None, flag=None):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, True)
        sock.bind(('0.0.0.0', self.port))

        while True:
            message = sock.recv(128)
            if match is None:
                if eval(message.decode('utf-8')) == data:
                    if flag is not None:
                        flag[0][flag[1]] = True
                    return eval(message.decode('utf-8'))
            else:
                if eval(message.decode('utf-8'))[match] == data:
                    if flag is not None:
                        flag[0][flag[1]] = True
                    return eval(message.decode('utf-8'))
