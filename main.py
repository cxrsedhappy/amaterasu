import os
import asyncio
import discord
from data.db_session import create_session, global_init
from data.user_role import Member
from discord.ext import commands


APP_ID = 802514382181236747
SERVER_ID = 777145173574418462

intents = discord.Intents.all()


class Client(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents, application_id=APP_ID)

    async def on_ready(self):

        connection = create_session()
        for fn in os.listdir("./cogs"):
            if fn.endswith(".py"):
                await client.load_extension(f'cogs.{fn[:-3]}')

        for guild in self.guilds:
            if guild.name == 'Happy Test Bot':
                for member in guild.members:
                    if not member.bot:
                        query = connection.query(Member).where(Member.id == member.id).first()
                        if query is None:
                            mem = Member()
                            mem.id = member.id
                            mem.nickname = member.name
                            mem.coins = 0
                            mem.reputation = 0
                            connection.add(mem)
                            connection.commit()

        connection.close()
        await self.tree.sync(guild=discord.Object(SERVER_ID))
        print('Connected and synced')


async def main():
    await client.start("ODAyNTE0MzgyMTgxMjM2NzQ3.YAwVwg.QbyBHccr2nc6XUUnBZwhoiD-a1s")


client = Client()
global_init('db/amaterasuDB')
asyncio.run(main())
