import socket
from threading import Thread
import datetime
from random import randint


SUCCESS = 'OK'
IS_BOT = 'Yes'


class Server:

    def __init__(self, port, users_file, pins_file, history_file):
        self.socket = socket.socket()
        self.users_file = users_file
        self.pins_file = pins_file
        self.history_file = history_file
        self.conns = []
        self.socket.bind(('', port))
        self.socket.listen()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.socket.close()

    def start(self):
        while True:
            self.accept()

    def accept(self):
        conn = Connection(self, *self.socket.accept())
        self.conns.append(conn)
        Thread(target=conn.handle).start()

    def get_logins(self):
        logins = []
        with open(self.users_file) as file:
            for line in file:
                login = line.split()[0]
                logins.append(login)
        return logins

    def send_all(self, sender, message):
        if sender.is_bot:
            address = 'bot'
        else:
            address = f'{sender.ip}:{sender.port}'
        content = f'{sender.username} ({address}): {message}'
        self.add_to_history(content)
        for conn in self.conns:
            if conn.auth and conn != sender:
                conn.send(content)

    def add_to_history(self, text):
        with open(self.history_file, 'a') as file:
            file.write(f'[{datetime.datetime.now()}] {text}<br>\n')


class Connection:

    def __init__(self, server, conn, addr):
        self.server = server
        self.socket = conn
        self.ip = addr[0]
        self.port = addr[1]
        self.auth = False
        self.username = None
        self.pin = None
        self.is_bot = False

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.socket.close()

    def handle(self):
        if self.recv() == IS_BOT:
            self.is_bot = True
        self.send_success()
        self.login()
        if self.auth:
            self.listen_messages()

    def recv(self):
        return self.socket.recv(1024).decode()

    def send(self, content):
        self.socket.send(content.encode())

    def send_success(self):
        self.send(SUCCESS)

    def login(self):
        while True:
            username = self.recv()
            if username in self.server.get_logins():
                self.username = username
                self.set_pin()
                self.show_pin()
                self.send_success()
                while True:
                    pin = self.recv()
                    if pin == self.pin:
                        self.send_success()
                        self.auth = True
                        break
                    self.send('Invalid PIN code')
                break
            self.send('You are not registered yet')

    def set_pin(self):
        self.pin = str(randint(1111, 9999))

    def show_pin(self):
        with open(self.server.pins_file, 'a') as file:
            file.write(f'[{datetime.datetime.now()}] {self.username}: '
                       f'{self.pin}<br>\n')

    def listen_messages(self):
        while True:
            message = self.recv()
            if not message:
                break
            Thread(target=self.server.send_all, args=(self, message)).start()


def main():
    with Server(
        port=84,
        users_file='/var/www/b/users.txt',
        pins_file='/var/www/c/index.html',
        history_file='/var/www/b/index.html'
    ) as server:
        server.start()


if __name__ == '__main__':
    main()
