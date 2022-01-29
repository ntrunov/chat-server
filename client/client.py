import socket
from threading import Thread


SUCCESS = 'OK'
IS_BOT = 'No'


class Client:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket()
        self.auth = False
        self.username = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.socket.close()

    def start(self):
        self.socket.connect((self.host, self.port))
        self.request(IS_BOT)
        self.login()
        if self.auth:
            Thread(target=self.listen_messages).start()
            self.input_messages()

    def recv(self):
        return self.socket.recv(1024).decode()

    def send(self, content):
        self.socket.send(content.encode())

    def request(self, content):
        self.send(content)
        return self.recv()

    def login(self):
        self.username = input('Enter your login: ')
        response = self.request(self.username)
        if response == SUCCESS:
            pin = input('Enter your PIN code: ')
            response = self.request(pin)
            if response == SUCCESS:
                self.auth = True
            else:
                print(response)
        else:
            print(response)

    def input_messages(self):
        while True:
            message = input(f'{self.username}: ')
            if message:
                self.send(message)

    def listen_messages(self):
        while True:
            message = self.recv()
            if not message:
                break
            print(f'\r{message}\n{self.username}: ', end='')


def main():
    with Client(host='localhost', port=84) as client:
        client.start()


if __name__ == '__main__':
    main()
