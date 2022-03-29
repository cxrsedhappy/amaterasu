import discord
import datetime

from random import randint
from discord import app_commands, ui
from discord.ext import commands
from discord.utils import get
from data.user_role import Member, Duel, Role
from data.db_session import create_session


COLOUR = 0x242424
SERVER_ID = 777145173574418462


class createView(ui.View):
    def __init__(self, author: discord.Member, sql_member, con, name, colour: discord.Colour, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        self.author = author
        self.member = sql_member
        self.con = con
        self.name = name
        self.colour = colour

    @discord.ui.button(label='✔', style=discord.ButtonStyle.green, custom_id='agreeButton')
    async def agree_button_callback(self, interaction: discord.Interaction, button: discord.Button):
        # Creates role on server and adds to member
        role = await self.bot.get_guild(SERVER_ID).create_role(name=self.name, colour=self.colour)
        await self.author.add_roles(role)

        r = Role()
        r.id = role.id
        r.name = role.name
        r.colour = role.colour.value
        r.owner = self.author.id
        r.multiplier = 1.0
        r.white_listed = False
        r.expired_at = datetime.datetime.today() + datetime.timedelta(weeks=1)

        self.member.roles.append(r)
        self.member.coins -= 20000
        self.con.add(r)
        self.con.commit()

        emb = discord.Embed(colour=COLOUR)
        emb.add_field(name='Done', value='Your role added to you')
        await interaction.response.edit_message(embed=emb, view=None)
        self.stop()

    @discord.ui.button(label='✖', style=discord.ButtonStyle.danger, custom_id='refuseButton')
    async def refuse_button_callback(self, interaction: discord.Interaction, button: discord.Button):
        emb = discord.Embed(colour=COLOUR)
        emb.add_field(name='Rejected', value='You rejected buying new role')
        await interaction.response.edit_message(embed=emb, view=None)
        self.stop()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if int(interaction.user.id) == int(self.author.id):
            return True
        return False


class profileView(ui.View):
    def __init__(self, author: discord.Member, sql_member, connection):
        """
        TODO
        Public or Private profile
        """
        super().__init__()
        self.author = author
        self.member = sql_member
        self.con = connection

    @discord.ui.button(label='General', style=discord.ButtonStyle.gray, custom_id='generalButton')
    async def general_button_callback(self, interaction: discord.Interaction, button: discord.Button):
        join_time = interaction.user.joined_at.strftime("%a, %b %d, %Y @ %I:%M %p")

        emb = discord.Embed(colour=COLOUR)
        emb.set_author(name=self.author.name, icon_url=self.author.avatar)
        emb.add_field(name='Coins           ⠀', value=f'**{self.member.coins}**', inline=True)
        emb.add_field(name='Reputation      ⠀', value=f'{self.member.reputation}', inline=True)
        emb.add_field(name='Information     ⠀', value=f'Level: Soon\nJoined: {join_time}', inline=True)
        await interaction.response.edit_message(embed=emb, view=self)

    @discord.ui.button(label='Roles', style=discord.ButtonStyle.gray, custom_id='roleButton')
    async def roles_button_callback(self, interaction: discord.Interaction, button: discord.Button):
        """
        TODO
        Rewrite logic (maybe?)
        """

        white_listed_description = ''
        black_listed_description = ''
        for role in self.member.roles:
            if role.white_listed is True:
                white_listed_description += f'<@&{role.id}>\n'
            else:
                black_listed_description += f'<@&{role.id}>\n'

        emb = discord.Embed(colour=COLOUR, description='To update your role time use **/roleupdate**\n\n'
                                                       'White listed roles mean they have **no expiration**.\n '
                                                       'Those roles can be gifted from server admins\n\n'
                                                       'Current roles means this roles have **expiration** date.\n\n')
        emb.add_field(name='White Listed Roles',
                      value=white_listed_description if white_listed_description != '' else 'None')
        emb.add_field(name='Current Roles',
                      value=black_listed_description if black_listed_description != '' else 'None')

        await interaction.response.edit_message(embed=emb, view=self)

    @discord.ui.button(label='Duel History', style=discord.ButtonStyle.gray, custom_id='duelButton')
    async def battles_button_callback(self, interaction: discord.Interaction, button: discord.Button):
        history = ''
        duels = self.member.duels
        # print(self.member.duels)
        low, high = get(self.author.guild.emojis, name="low"), get(self.author.guild.emojis, name="high")

        for i in range(min(len(duels), 10) - 1, -1, -1):
            won = True if int(self.author.id) == int(duels[i].winner) else False
            history += f"{high if won else low} **{'Won' if won else 'Lose'}** — **{duels[i].pay}** " \
                       f"{datetime.datetime.strftime(duels[i].timestamp, '%d.%m.%y')}\n"

        # checks if emd.add_field(value) won't be empty
        if history == '':
            history += "You didn't duel someone"

        emb = discord.Embed(colour=COLOUR)
        emb.add_field(name='Last 10 duels', value=history)

        await interaction.response.edit_message(embed=emb, view=self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """
        TODO
        Bug with interaction_check
        If Bob used command and didn't click the button
        And ALice used this command too
        Alice can click on Bob's buttons (Bob can't click his buttons)
        """
        if int(interaction.user.id) == int(self.author.id):
            return True
        return False


class duelView(ui.View):
    def __init__(self, author: discord.User, enemy: discord.Member, coins: int, f_duelist, s_duelist, con):
        super().__init__()
        self.author = author
        self.enemy = enemy
        self.coins = coins
        self.f_duelist = f_duelist
        self.s_duelist = s_duelist
        self.con = con

    @discord.ui.button(label='✔', style=discord.ButtonStyle.green, custom_id='agreeButton')
    async def agree_button_callback(self, interaction: discord.Interaction, button: discord.Button):
        await self.interaction_check(interaction)
        emb = discord.Embed(colour=COLOUR)
        emb.set_author(name=self.author.name, icon_url=self.author.avatar)

        if self.f_duelist.coins < self.coins or self.s_duelist.coins < self.coins:
            emb.description = f"One of you don't have **{self.coins}** to duel"
            await interaction.response.send_message(embed=emb)

        duel = Duel()
        duel.duelist_one = self.author.id
        duel.duelist_two = self.enemy.id
        duel.pay = self.coins
        duel.timestamp = datetime.datetime.today().replace(microsecond=0)

        if randint(1, 100) > 50:
            duel.winner = self.author.id
            self.f_duelist.coins += self.coins
            self.s_duelist.coins -= self.coins
        else:
            duel.winner = self.enemy.id
            self.f_duelist.coins -= self.coins
            self.s_duelist.coins += self.coins

        self.f_duelist.duels.append(duel)
        self.s_duelist.duels.append(duel)
        self.con.commit()


        emb.description = f'<@{duel.winner}> won and earn **{self.coins} coins!**'

        await interaction.response.edit_message(f"<@{duel.winner}>", embed=emb, view=None)
        self.stop()

    @discord.ui.button(label='✖', style=discord.ButtonStyle.danger, custom_id='refuseButton')
    async def refuse_button_callback(self, interaction: discord.Interaction, button: discord.Button):
        emb = discord.Embed(description=f"<@{self.author.id}> your enemy refused duel!", colour=COLOUR)
        await interaction.response.edit_message(embed=emb, view=None)
        self.stop()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if int(interaction.user.id) == int(self.enemy.id):
            return True
        return False


class InterCog(commands.Cog):
    roles = app_commands.Group(name='role', description='Roles commands', guild_ids=[777145173574418462])

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        print(f"Loaded {self.__cog_name__}")

    @app_commands.command(name="profile", description="Show up your profile")
    @app_commands.guilds(discord.Object(777145173574418462))
    async def profile(self, interaction: discord.Interaction):
        connection = create_session()
        sql_member = connection.query(Member).where(Member.id == interaction.user.id).first()

        join_time = interaction.user.joined_at.strftime("%a, %b %d, %Y @ %I:%M %p")
        emb = discord.Embed(colour=COLOUR)
        emb.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
        emb.add_field(name='Coins           ⠀', value=f'**{sql_member.coins}**', inline=True)
        emb.add_field(name='Reputation      ⠀', value=f'{sql_member.reputation}', inline=True)
        emb.add_field(name='Information     ⠀', value=f'Level: Soon\nJoined: {join_time}', inline=True)

        profile = profileView(interaction.user, sql_member, connection)
        await interaction.response.send_message(embed=emb, view=profile)

    @app_commands.command(name='bonus', description='Gives you 100 coins')
    @app_commands.checks.cooldown(1, 7200, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.guilds(discord.Object(777145173574418462))
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
    @app_commands.guilds(discord.Object(777145173574418462))
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
                                                   view=duelView(interaction.user, enemy, coins, f_duelist, s_duelist,
                                                              connection))

    @roles.command(name='create', description='Create your own role')
    async def role_create(self, interaction: discord.Interaction, name: str, colour: str):
        hex_colour = discord.Colour(int(colour, 16))
        connection = create_session()
        member = connection.query(Member).where(Member.id == interaction.user.id).first()

        if member.coins < 20000:
            emb = discord.Embed()
            emb.add_field(name='Error', value="You don't have enough coins for this")
            await interaction.response.send_message(embed=emb)
            return

        emb = discord.Embed(title='New role', description='New role information')
        emb.add_field(name='Costs', value='**20000**')
        create_view = createView(interaction.user, member, connection, name, hex_colour, self.bot)
        await interaction.response.send_message(embed=emb, view=create_view)

    @roles.command(name='manage', description='Soon...')
    async def role_manage(self, interaction: discord.Interaction):
        emb = discord.Embed()
        emb.add_field(name='manage', value='role manager')
        await interaction.response.send_message(embed=emb)

    @roles.command(name='update', description='Soon...')
    async def role_update(self, interaction: discord.Interaction):
        emb = discord.Embed()
        emb.add_field(name='udpate', value='role updater')
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
