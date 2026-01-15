# bot_main.py - 100% Python 3.13+ совместимый!
import socket
import re
import time
import threading
from core.config import setting


class TwitchBot:
    def __init__(self):
        self.nick = "yourbotname"  # ← ЗАМЕНИ на ник БОТА!
        self.token = setting.conf_tw.token.replace("oauth:", "")
        self.channel = f"#{setting.conf_tw.channel}"
        self.sock = None

    def connect(self):
        self.sock = socket.socket()
        self.sock.connect(("irc.chat.twitch.tv", 6667))
        self.send(f"PASS oauth:{self.token}")
        self.send(f"NICK {self.nick}")
        self.send(f"JOIN {self.channel}")
        print(f"✅ Подключился к {self.channel}")

    def send(self, msg):
        self.sock.send(f"{msg}\r\n".encode("utf-8"))

    def chat(self, msg):
        self.send(f"PRIVMSG {self.channel} {msg}")

    def parse_message(self, resp):
        if resp.startswith("PING"):
            self.sock.send("PONG\r\n".encode("utf-8"))
            return

        if "PRIVMSG" in resp:
            username = re.search(r"\w+", resp.split("!")[0][1:]).group()
            message = resp.split(":", 2)[2].rstrip()

            print(f"💬 {username}: {message}")

            if username.lower() == self.nick.lower():
                return

            # Автоответ
            if "привет" in message.lower():
                self.chat(f"Привет @{username}!")

            # Команды
            if message == "!hello":
                self.chat(f"Привет @{username}!")

            elif message.startswith("!таймер"):
                try:
                    seconds = int(message.split()[1])
                    threading.Timer(
                        seconds,
                        lambda u=username: self.chat(f"⏰ @{u} таймер сработал!"),
                    ).start()
                    self.chat(f"⏰ Таймер на {seconds}с @{username}!")
                except:
                    self.chat(f"❌ @{username} !таймер 30")

            elif message == "!слот":
                import random

                emojis = ["🍒", "🍋", "🍊", "🔔", "💎", "7️⃣"]
                result = [random.choice(emojis) for _ in range(3)]
                self.chat(f"{result[0]}{result[1]}{result[2]}")

    def listen(self):
        while True:
            try:
                resp = self.sock.recv(2048).decode("utf-8", errors="ignore")
                if resp:
                    for line in resp.split("\n"):
                        self.parse_message(line.strip())
            except:
                print("🔄 Переподключение...")
                time.sleep(5)
                self.connect()

    def run(self):
        self.connect()
        self.listen()


if __name__ == "__main__":
    bot = TwitchBot()
    bot.run()
