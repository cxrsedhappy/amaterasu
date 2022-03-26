import discord

from random import randint
import datetime
from datetime import datetime

from discord.utils import get
from data.db_session import create_session
from data.user_role import Member, Duel
from discord import app_commands, ui
from discord.ext import commands

COLOUR = 0x242424


class createView(ui.View):
    def __init__(self, author: discord.Member, sql_member, con, name, colour: discord.Colour):
        super().__init__()
        self.author = author
        self.member = sql_member
        self.con = con
        self.name = name
        self.colour = colour

    @discord.ui.button(label='✔', style=discord.ButtonStyle.green, custom_id='agreeButton')
    async def agree_button_callback(self, button: discord.Button, interaction: discord.Interaction):
        """
        TODO
        Adding Role to user in Discord
        """
        self.member.coins -= 20000
        self.con.commit()
        self.con.close()
        emb = discord.Embed()
        emb.add_field(name='Done', value='Your role added to you')
        await interaction.response.edit_message(embed=emb, view=None)
        self.stop()

    @discord.ui.button(label='✖', style=discord.ButtonStyle.danger, custom_id='refuseButton')
    async def refuse_button_callback(self, button: discord.Button, interaction: discord.Interaction):
        emb = discord.Embed()
        emb.add_field(name='Rejected', value='You rejected buying new role')
        await interaction.response.edit_message(embed=emb, view=None)
        self.stop()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if int(interaction.user.id) == int(self.author.id):
            return True
        return False


class profileView(ui.View):
    def __init__(self, author: discord.Member, sql_member):
        super().__init__()
        self.author = author
        self.member = sql_member

    @discord.ui.button(label='General', style=discord.ButtonStyle.gray, custom_id='generalButton')
    async def general_button_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        join_time = interaction.user.joined_at.strftime("%a, %b %d, %Y @ %I:%M %p")

        emb = discord.Embed(colour=COLOUR)
        emb.set_author(name=self.author.name, icon_url=self.author.avatar)
        emb.add_field(name='Coins           ⠀', value=f'**{self.member.coins}**', inline=True)
        emb.add_field(name='Reputation      ⠀', value=f'{self.member.reputation}', inline=True)
        emb.add_field(name='Information     ⠀', value=f'Level: Soon\nJoined: {join_time}', inline=True)
        await interaction.response.edit_message(embed=emb, view=self)

    @discord.ui.button(label='Roles', style=discord.ButtonStyle.gray, custom_id='roleButton')
    async def roles_button_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
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
    async def battles_button_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        emb = discord.Embed()

        history = ""
        duels = self.member.duels
        low, high = get(self.author.guild.emojis, name="low"), get(self.author.guild.emojis, name="high")
        for i in range(min(len(duels), 10) - 1, -1, -1):
            won = True if int(self.author.id) == int(duels[i].winner) else False
            history += f"{high if won else low} **{'Won' if won else 'Lose'}** — **{duels[i].pay}** " \
                       f"{datetime.strftime(duels[i].timestamp, '%d.%m.%y')}\n"

        # checks if emd.add_field(value) won't be empty
        if history == '':
            history += "you didn't duel someone"

        emb.add_field(name='Last 10 duels', value=history)
        await interaction.response.edit_message(embed=emb, view=self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """
        TODO
        Bug with interaction_check
        If Bob used command and didn't click the button other
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
    async def agree_button_callback(self, button: discord.Button, interaction: discord.Interaction):
        await self.interaction_check(interaction)
        emb = discord.Embed()
        emb.set_author(name=self.author.name, icon_url=self.author.avatar)

        if self.f_duelist.coins < self.coins or self.s_duelist.coins < self.coins:
            emb.description = f"One of you don't have **{self.coins}** to duel"
            await interaction.response.send_message(embed=emb)

        duel = Duel()
        duel.duelist_one = self.author.id
        duel.duelist_two = self.enemy.id
        duel.pay = self.coins
        duel.timestamp = datetime.today().replace(microsecond=0)

        if randint(1, 100) > 50:
            duel.winner = self.author.id
            self.f_duelist.coins += self.coins
            self.s_duelist.coins -= self.coins
            self.f_duelist.duels.append(duel)
            self.s_duelist.duels.append(duel)
        else:
            duel.winner = self.enemy.id
            self.f_duelist.coins -= self.coins
            self.s_duelist.coins += self.coins
            self.f_duelist.duels.append(duel)
            self.s_duelist.duels.append(duel)

        emb.description = f'<@{duel.winner}> won and earn **{self.coins} coins!**'
        self.con.commit()
        await interaction.response.edit_message(embed=emb, view=None)
        self.stop()

    @discord.ui.button(label='✖', style=discord.ButtonStyle.danger, custom_id='refuseButton')
    async def refuse_button_callback(self, button: discord.Button, interaction: discord.Interaction):
        emb = discord.Embed(description=f"<@{self.author.id}> your enemy refused duel!")
        await interaction.response.edit_message(embed=emb, view=None)
        self.stop()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        print(interaction.user)
        print(self.author)
        if int(interaction.user.id) == int(self.enemy.id):
            return True
        return False


class InterCog(commands.Cog):
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

        profile = profileView(interaction.user, sql_member)
        await interaction.response.send_message(embed=emb, view=profile)

    @app_commands.command(name='bonus', description='Gives you 100 coins')
    @app_commands.guilds(discord.Object(777145173574418462))
    async def bonus(self, interaction: discord.Interaction):
        """
        TODO
        Add command cooldown
        """
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

    @app_commands.command(name='create_role', description='Create your own role')
    @app_commands.guilds(discord.Object(777145173574418462))
    async def role_create(self, interaction: discord.Interaction, name: str, colour: str):
        hex_colour = discord.Colour(int(colour, 16))
        connection = create_session()
        member = connection.query(Member).where(Member.id == interaction.user.id).first()

        if member.coins <= 20000:
            emb = discord.Embed()
            emb.add_field(name='Error', value="You don't have enough coins for this")
            await interaction.response.send_message(embed=emb)
            return

        emb = discord.Embed(title='New role', description='New role information')
        emb.add_field(name='Costs', value='**20000**')

        await interaction.response.send_message(embed=emb, view=createView(interaction.user, member, connection, name, hex_colour))


async def setup(bot: commands.Bot):
    await bot.add_cog(InterCog(bot))
