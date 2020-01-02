import socket

from utility import MyThread


class Node:
    def __init__(self, port=11719):
        self.ip = socket.gethostbyname(socket.gethostname())
        self.port = port
        
    def send(self, data, ip=None, **kwargs):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, True)
        message = {'ip': self.ip, 'message': data}
        for key, value in kwargs.items():
            message[key] = value
        if ip is None:
            for i in range(256):
                sock.sendto(bytes(str(message), encoding='utf-8'), (f'192.168.1.{i}', self.port))
        else:
            sock.sendto(bytes(str(message), encoding='utf-8'), (ip, self.port))

    def recieve(self, var):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, True)
        sock.bind(('0.0.0.0', self.port))

        message = sock.recv(128)
        var = eval(message.decode('utf-8'))
        return eval(message.decode('utf-8'))

    def await_recieve(self, data, match=None, flag=None, stop_count=1):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, True)
        sock.bind(('0.0.0.0', self.port))
        stop = 0

        while True:
            message = sock.recv(128)
            if match is None:
                if eval(message.decode('utf-8')) == data:
                    if flag is not None:
                        for elem in flag:
                            if elem[2] == '__VALUE__':
                                elem[2] = eval(message.decode('utf-8'))
                            if isinstance(elem[0][elem[1]], list):
                                elem[0][elem[1]].append(elem[2])
                            else:
                                elem[0][elem[1]] = elem[2]
                    stop += 1
                    if stop == stop_count:
                        return eval(message.decode('utf-8'))
            else:
                if data in eval(message.decode('utf-8'))[match]:
                    if flag is not None:
                        for elem in flag:
                            if elem[2] == '__VALUE__':
                                elem[2] = eval(message.decode('utf-8'))
                            if isinstance(elem[0][elem[1]], list):
                                elem[0][elem[1]].append(elem[2])
                            else:
                                elem[0][elem[1]] = elem[2]
                    stop += 1
                    if stop == stop_count:
                        return eval(message.decode('utf-8'))
