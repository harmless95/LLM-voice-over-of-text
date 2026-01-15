import asyncio
import socket

from twitchio.ext import commands

from core.config import setting


class Bot(commands.Bot):

    def __init__(self):
        self.sock = None
        self.nick = "yourbotname"  # Ник бота
        self.token = setting.conf_tw.token.replace("oauth:", "")
        self.channel = f"#{setting.conf_tw.channel}"

    def connect(self):
        self.sock = socket.socket()
        self.sock.connect(("irc.chat.twitch.tv", 6667))
        self.send(f"PASS {self.token}")
        self.send(f"NICK {self.nick}")
        self.send(f"JOIN {self.channel}")
        print(f"✅ Подключился к {self.channel}")

    async def event_ready(self):
        print(f"Бот {self.nick} подключился")

    async def event_message(self, message):
        print(f"{message.author.name}: {message.content}")

        if message.author.name.lower() == self.nick.lower():
            return

        await self.handle_commands(message)

        if "привет" in message.content.lower():
            await message.channel.send(f"Привет @{message.author.name}!")

    @commands.command()
    async def hello(self, ctx: commands.Context):
        await ctx.send(f"Привет @{ctx.author.name}!")

    @commands.command(name="Таймер")
    async def timer(self, ctx: commands.Context, time: int):
        """!таймер 60 - таймер на 60 сек"""
        await ctx.send(f"⏰ Таймер на {time} запущен!")
        await asyncio.sleep(delay=time)
        await ctx.send(f"⏰ {ctx.author.name} таймер сработал!")

    @commands.command(name="Рулетка")
    async def slot(self, ctx: commands.Context):
        """!слот - рулетка"""
        import random

        emojis = ["🍒", "🍋", "🍊", "🔔", "💎", "7️⃣"]
        result = [random.choice(emojis) for _ in range(3)]
        await ctx.send(f"{result[0]}{result[1]}{result[2]}")


bot = Bot()
bot.run()
