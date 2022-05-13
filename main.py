import os
import asyncio
import discord
from data.db_session import create_session, global_init
from data.user_role import Member, Role
from discord.ext import commands


APP_ID = 802514382181236747

WHERE_IS_MY_PANCAKES = 894192291831504959
HAPPY_TEST_BOT = 777145173574418462

# Boties
QQ = 802276078064238662
DEP = 969165372966199336
BOT = 802271250445369375

SERVER_ID = HAPPY_TEST_BOT
GUILD = discord.Object(SERVER_ID)


intents = discord.Intents.all()


class Client(commands.Bot):
    """
    TODO
    Add on_member_join event
    """
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
        await self.tree.sync(guild=GUILD)
        print('Connected and synced')


async def main():
    await client.start("ODAyNTE0MzgyMTgxMjM2NzQ3.YAwVwg.QbyBHccr2nc6XUUnBZwhoiD-a1s")


client = Client()
global_init('db/amaterasuDB')
asyncio.run(main())
