import datetime
import os
import asyncio
import discord
from discord.utils import get

from data.db_session import create_session, global_init
from data.user_role import Member, Role
from discord.ext import commands, tasks

APP_ID = 802514382181236747

WHERE_IS_MY_PANCAKES = 894192291831504959
HAPPY_TEST_BOT = 777145173574418462
LONELY_SERVER = 802271249966563338

# Boties
QQ = 802276078064238662
DEP = 969165372966199336
BOT = 802271250445369375

SERVER_ID = LONELY_SERVER
GUILD = discord.Object(SERVER_ID)


intents = discord.Intents.all()


class Client(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents, application_id=APP_ID)

    async def on_ready(self):
        connection = create_session()

        for fn in os.listdir("./cogs"):
            if fn.endswith(".py"):
                await client.load_extension(f'cogs.{fn[:-3]}')

        # When bot is ready then
        for guild in self.guilds:
            if guild.id == SERVER_ID:  # Check for the guild
                for member in guild.members:
                    if not member.bot:  # If member is not bot
                        # Check if user is already exist
                        sql_member = connection.query(Member).where(Member.id == member.id).first()
                        print(sql_member)
                        if sql_member is None:
                            mem = Member()
                            mem.id = member.id
                            mem.nickname = member.name
                            mem.coins = 0
                            mem.reputation = 0
                            mem.profile_is_private = False

                            connection.add(mem)
                            sql_member = mem

                        for role in member.roles:
                            # Update roles for this user
                            sql_role = connection.query(Role).where(Role.id == role.id).first()
                            if sql_role is None and role.name != '@everyone':
                                r = Role()
                                r.id = role.id
                                r.name = role.name
                                r.colour = role.colour.value
                                r.owner = member.id
                                r.multiplier = 1.0
                                r.enabled = True
                                r.white_listed = True
                                r.expired_at = None
                                sql_member.roles.append(r)
                                connection.add(r)

        connection.commit()
        connection.close()
        await self.tree.sync()
        print('Connected and synced')

    async def on_member_join(self, member: discord.Member):
        connection = create_session()
        sql_member = connection.query(Member).where(Member.id == member.id).first()
        if sql_member is None:
            mem = Member()
            mem.id = member.id
            mem.nickname = member.name
            mem.coins = 0
            mem.reputation = 0
            mem.profile_is_private = False
            connection.add(mem)

        connection.commit()
        connection.close()

    async def setup_hook(self) -> None:
        self.my_background_task.start()

    @tasks.loop(seconds=60)  # task runs every 60 seconds
    async def my_background_task(self):
        connection = create_session()
        roles = connection.query(Role).where(Role.expired_at < datetime.timedelta(weeks=1) + datetime.datetime.now())
        for role in roles:
            connection.delete(role)
            temp = client.get_guild(SERVER_ID).get_role(role.id)
            await client.get_guild(SERVER_ID).get_member(role.owner).remove_roles(temp)
            await temp.delete()
        connection.commit()
        connection.close()

    @my_background_task.before_loop
    async def before_my_task(self):
        await self.wait_until_ready()  # wait until the bot logs in


async def main():
    await client.start("ODAyNTE0MzgyMTgxMjM2NzQ3.YAwVwg.QbyBHccr2nc6XUUnBZwhoiD-a1s")


client = Client()
global_init('db/amaterasuDB')
asyncio.run(main())
