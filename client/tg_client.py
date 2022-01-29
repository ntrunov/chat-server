import socket
from threading import Thread

from telegram import Bot
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters

from tg_token import TOKEN


SUCCESS = 'OK'
IS_BOT = 'Yes'


class TelegramBot:

    def __init__(self, host, port, token):
        self.host = host
        self.port = port
        self.token = token
        self.updater = Updater(token)
        self.clients = []

    def start(self):
        self.updater.dispatcher.add_handler(
            MessageHandler(Filters.text & (~Filters.command),
                           self.handle_message)
        )
        self.updater.start_polling()

    def handle_message(self, update, context):
        message = update.message.text
        chat_id = update.effective_chat.id
        client = self.get_client(chat_id)
        if not client:
            client = self.add_client(chat_id)
        response = client.process_message(message)
        if response and response != SUCCESS:
            update.message.reply_text(text=response)

    def get_client(self, chat_id):
        for client in self.clients:
            if client.chat_id == chat_id:
                return client

    def add_client(self, chat_id):
        client = TelegramClient(self, chat_id, self.host, self.port)
        self.clients.append(client)
        client.start()
        return client


class TelegramClient:

    def __init__(self, bot, chat_id, host, port):
        self.bot = bot
        self.chat_id = chat_id
        self.host = host
        self.port = port
        self.socket = socket.socket()
        self.auth = False
        self.username = None

    def start(self):
        self.socket.connect((self.host, self.port))
        self.request(IS_BOT)

    def recv(self):
        return self.socket.recv(1024).decode()

    def send(self, content):
        self.socket.send(content.encode())

    def request(self, content):
        self.send(content)
        return self.recv()

    def process_message(self, message):
        if self.auth:
            self.send(message)
        elif self.username:
            response = self.request(message)
            if response == SUCCESS:
                self.auth = True
                self.send_to_chat('You are successfully logged in')
                Thread(target=self.listen_server_messages).start()
            return response
        else:
            response = self.request(message)
            if response == SUCCESS:
                self.username = message
                self.send_to_chat('Enter your PIN code')
            return response

    def listen_server_messages(self):
        while True:
            message = self.recv()
            if not message:
                break
            if self.auth:
                self.send_to_chat(message)

    def send_to_chat(self, message):
        Bot(self.bot.token).send_message(self.chat_id, message)

    def close(self):
        self.socket.close()


def main():
    tg_bot = TelegramBot(host='localhost', port=84, token=TOKEN)
    tg_bot.start()


if __name__ == '__main__':
    main()
