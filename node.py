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

    def recieve(self):
    # Awaits for any one message.
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, True)
        sock.bind(('0.0.0.0', self.port))

        s = sock.recv(128)
        message = eval(s.decode('utf-8'))
        #var = eval(message.decode('utf-8'))
        return message

    #def await_recieve(self, data, match=None, flag=None, stop_count=1):
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
            s = sock.recv(128)
            message = eval(s.decode('utf-8'))
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
                                        if inner_elem['ip'] == message['ip']:
                                            print(elem[0][elem[1]])
                                            elem[0][elem[1]].remove(inner_elem)
                                            print(elem[0][elem[1]])
                                            break
                            else:
                                if isinstance(elem[0][elem[1]], list):
                                    elem[0][elem[1]].remove(message[match])
                        stops[i] += 1
            for i in range(len(stops)):
                if stops[i] != stop_counts[i]:
                    break
            else:
                return

            '''
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
            '''
