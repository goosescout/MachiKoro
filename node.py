import socket

from utility import MyThread, Player, Card


class Node:
    def __init__(self, port=11719):
        self.hostname = socket.gethostname()
        #if "MacBook" in self.hostname:
            #self.ip = '172.20.10.11'
        #else:
        self.ip = socket.gethostbyname(self.hostname)

        self.port = port
        self.queque = []
        
    def send(self, data, ip=None, **kwargs):
        '''
        Send a message to a given ip.
        If ip is not provided (or None) sends a message to all ip adresses in range from 192.168.1.0 to 192.168.1.255
        Message is a dictionary, which holds a sender's ip, a text, and any other passed arguments.
        '''
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, True)
        message = {'ip': self.ip, 'text': data}
        for key, value in kwargs.items():
            message[key] = value
        if ip is None:
            to_ip = '.'.join(self.ip.split('.')[:-1])
            for i in range(256):
                sock.sendto(bytes(str(message), encoding='utf-8'), (f'{to_ip}.{i}', self.port))
            #sock.sendto(bytes(str(message), encoding='utf-8'), (('172.20.10.3' if "MacBook" in self.hostname else "172.20.10.12"), self.port))
        elif isinstance(ip, list) or isinstance(ip, map):
            for elem in ip:
                if elem != self.ip:
                    sock.sendto(bytes(str(message), encoding='utf-8'), (elem, self.port))
        else:
            sock.sendto(bytes(str(message), encoding='utf-8'), (ip, self.port))

    def recieve(self, var, key):
        '''
        Awaits for any one message and writes it in a variable provided.
        '''
        if self.queque:
            message = self.queque.pop()
            if isinstance(var[key], list):
                var[key].append(message)
            else:
                var[key] = message
            return message

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, True)
        sock.bind(('0.0.0.0', self.port))

        s = sock.recv(4096)
        message = eval(s.decode('utf-8'))
        for mes_key in message.keys():
            try:
                message[mes_key] = eval(message[key])
            except Exception:
                pass
        if isinstance(var[key], list):
            var[key].append(message)
        else:
            var[key] = message
        return message

    def await_recieve(self, *args):
        '''
        Awaits for a particular message.

        Takes blocks as an argument: node.await_reciceve([data, match, flag, stop_count], ...).
                                                         <------------block------------>
        Blocks must be lists (not tuples).
        At least one block must be passed as an argument.
        data - message that should match
        match - part of a recieved message that should match (for example ip, message, etc)
        flag - variables that should change once the message is recieved. Flag: [[variable_name, variable_key, value], ...]
            variable_name - name of a variable (it must be a dictionary)
            variable_key - key in the variable
            value - value to write in the variable (can be "__VALUE__" to write the recieved message or "__MATCH__" to write the matching value for message, or "__VALUE_DEL__" and "___MATCH_DEL__")
        stop_count - number of matches after which the programm stops to recieve them (0 - never stop)
        '''
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, True)
        sock.bind(('0.0.0.0', self.port))

        datas = [block[0] for block in args]
        matches = [block[1] for block in args]
        flags = [block[2] for block in args]
        stop_counts = [block[3] for block in args]
        stops = [0] * len(stop_counts)

        while True:
            s = sock.recv(65536)
            message = eval(s.decode('utf-8'))
            for key in message.keys():
                try:
                    message[key] = eval(message[key])
                except Exception:
                    pass
            if message['text'] == '__STOP_RECIEVE__':
                return
            for i, (data, match, flag, stop_count, stop) in enumerate(zip(datas, matches, flags, stop_counts, stops)):
                if data == message[match]:
                    if stop != stop_count:
                        for elem in flag:
                            if elem[2] not in ('__VALUE_DEL__', '__MATCH_DEL__'):
                                if elem[2] == '__VALUE__':
                                    elem[2] = message
                                elif elem[2] == '__MATCH__':
                                    elem[2] = message[match]
                                if isinstance(elem[0][elem[1]], list):
                                    elem[0][elem[1]].append(elem[2])
                                else:
                                    elem[0][elem[1]] = elem[2]
                            elif elem[2] == '__VALUE_DEL__':
                                if isinstance(elem[0][elem[1]], list):
                                    for inner_elem in elem[0][elem[1]]:
                                        try:
                                            if inner_elem[match] in message[match]:
                                                elem[0][elem[1]].remove(inner_elem)
                                                break
                                        except KeyError:
                                            pass
                            else:
                                if isinstance(elem[0][elem[1]], list):
                                    elem[0][elem[1]].remove(message[match])
                        stops[i] += 1
            if 'roll' in message['text']:
                self.queque.append(message)
            for i in range(len(stops)):
                if stops[i] != stop_counts[i]:
                    break
            else:
                return message
