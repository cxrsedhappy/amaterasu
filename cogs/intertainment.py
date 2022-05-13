import discord
import datetime

from random import randint

from sqlalchemy.orm import Session
from discord import app_commands, ui
from discord.ext import commands
from discord.utils import get

from views.manage import manageView
from views.profile import profileView
from views.duel import duelView
from views.create import createView

from data.user_role import Member, Duel, Role
from data.db_session import create_session


COLOUR = 0x242424
WHERE_IS_MY_PANCAKES = 894192291831504959
HAPPY_TEST_BOT = 777145173574418462

SERVER_ID = HAPPY_TEST_BOT
GUILD = discord.Object(SERVER_ID)


class InterCog(commands.Cog):
    """
    TODO
    Split roles command and other commands
    """
    roles = app_commands.Group(name='role', description='Roles commands', guild_ids=[SERVER_ID])

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        print(f"Loaded {self.__cog_name__}")

    @app_commands.command(name="profile", description="Show up your profile")
    @app_commands.guilds(GUILD)
    async def profile(self, interaction: discord.Interaction):
        connection = create_session()
        sql_member: Member = connection.query(Member).where(Member.id == interaction.user.id).first()

        join_time = interaction.user.joined_at.strftime("%a, %b %d, %Y @ %I:%M %p")
        emb = discord.Embed(colour=COLOUR)
        emb.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
        emb.add_field(name='Coins           ⠀', value=f'**{sql_member.coins}**', inline=True)
        emb.add_field(name='Reputation      ⠀', value=f'{sql_member.reputation}', inline=True)
        emb.add_field(name='Information     ⠀', value=f'Level: Soon\nJoined: {join_time}', inline=True)

        profile_view = profileView(interaction.user, sql_member, connection)
        await interaction.response.send_message(embed=emb,
                                                view=profile_view,
                                                ephemeral=True if sql_member.profile_is_private else False)

    @app_commands.command(name='bonus', description='Gives you 100 coins')
    @app_commands.checks.cooldown(1, 7200, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.guilds(GUILD)
    async def bonus(self, interaction: discord.Interaction):
        connection = create_session()
        mem = connection.query(Member).where(Member.id == interaction.user.id).first()

        mem.coins += 100

        connection.commit()
        connection.close()

        emb = discord.Embed(colour=COLOUR)
        emb.add_field(name='Done', value='Gained **100** coins', inline=True)
        await interaction.response.send_message(embed=emb)

    @app_commands.command(name='duel', description='Invite your enemy to a duel')
    @app_commands.guilds(GUILD)
    async def duel(self, interaction: discord.Interaction, enemy: discord.Member, coins: int):
        """
        TODO
        Add checker
        User can't duel someone who isn't in database
        """

        emb = discord.Embed()
        emb.set_author(name=interaction.user, icon_url=interaction.user.avatar)

        connection = create_session()
        f_duelist = connection.query(Member).where(Member.id == interaction.user.id).first()
        s_duelist = connection.query(Member).where(Member.id == enemy.id).first()

        # self dueling checker
        if interaction.user.id == enemy.id:
            emb.description = f'You can duel yourself'
            await interaction.response.send_message(embed=emb, ephemeral=True)
            return

        # money checker
        if f_duelist.coins < coins or s_duelist.coins < coins:
            emb.description = f"One of you don't have **{coins}** to duel"
            await interaction.response.send_message(embed=emb, ephemeral=True)
            return

        emb.description = f"{enemy.mention}, someone wants to duel you.\nShall you?"
        emb.add_field(name='Coins', value=f"**{coins}**")
        await interaction.response.send_message(embed=emb,
                                                view=duelView(interaction.user, enemy, coins,
                                                              f_duelist, s_duelist, connection))

    @roles.command(name='create', description='Create your own role')
    async def role_create(self, interaction: discord.Interaction, name: str, colour: str):
        """
        TODO
        Check colour for hex
        """
        connection = create_session()
        member = connection.query(Member).where(Member.id == interaction.user.id).first()

        emb = discord.Embed()
        hex_colour = discord.Colour(int(colour, 16))

        if member.coins < 20000:
            emb.add_field(name='Error', value="You don't have enough coins for this")
            await interaction.response.send_message(embed=emb)
            return

        emb.title = 'New role'
        emb.description = 'New role information'
        emb.add_field(name='Costs', value='**20000**')

        create_view = createView(interaction.user, member, connection, name, hex_colour, self.bot)
        await interaction.response.send_message(embed=emb, view=create_view)

    @roles.command(name='manage', description='Enable or disable roles')
    async def role_manage(self, interaction: discord.Interaction):
        connection = create_session()
        member = connection.query(Member).where(Member.id == interaction.user.id).first()

        value = ''
        expiration_time = ''

        for role in member.roles:
            if role.white_listed is False:
                expiration_time = discord.utils.format_dt(role.expired_at)

            value += f'{":white_check_mark:" if role.enabled else ":x:"}<@&{role.id}>' \
                     f'[{role.multiplier}x] - ' \
                     f'{f"expire at {expiration_time}" if role.white_listed is False else "No expiration date"} \n' \

        emb = discord.Embed(colour=COLOUR)
        emb.add_field(name=':file_folder: Your roles', value=value)
        await interaction.response.send_message(embed=emb, view=manageView(interaction.user, connection, self.bot))

    @roles.command(name='update', description='Soon...')
    async def role_update(self, interaction: discord.Interaction):
        emb = discord.Embed()
        emb.add_field(name='update', value='role updater')
        await interaction.response.send_message(embed=emb)

    @roles.command(name='gift', description='Soon...')
    @app_commands.checks.has_permissions(administrator=True)
    async def role_gift(self, interaction: discord.Interaction):
        emb = discord.Embed()
        emb.add_field(name='gift', value='role gifted')
        await interaction.response.send_message(embed=emb)

    @role_gift.error
    async def role_gift_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            emb = discord.Embed(colour=COLOUR)
            emb.add_field(name='Something wrong', value=f"It looks like you ain't admin")
            await interaction.response.send_message(embed=emb, ephemeral=True)

    @bonus.error
    async def bonus_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):

            time = int(error.retry_after)

            h = (time // 60) // 60
            s = time % 60
            m = (time // 60) % 60

            emb = discord.Embed(colour=COLOUR)
            emb.add_field(name='Come back next time', value=f"You're on cooldown. Try again in {h}:{m}:{s}", inline=True)
            await interaction.response.send_message(embed=emb, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(InterCog(bot))
