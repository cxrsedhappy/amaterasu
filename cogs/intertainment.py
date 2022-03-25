import discord

from random import randint
from datetime import datetime

from discord.utils import get

from data.db_session import create_session
from data.user_role import Member, Duel
from discord import app_commands, ui
from discord.ext import commands

COLOUR = 0x242424


class profileView(ui.View):
    def __init__(self, author: discord.Member, sql_member):
        super().__init__()
        self.author = author
        self.member = sql_member

    @discord.ui.button(label='General', style=discord.ButtonStyle.gray, custom_id='generalButton')
    async def general_button_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        emb = discord.Embed(colour=COLOUR)
        join_time = interaction.user.joined_at.strftime("%a, %b %d, %Y @ %I:%M %p")
        emb.add_field(name='Coins           ⠀', value=f'**{self.member.coins}**', inline=True)
        emb.add_field(name='Reputation      ⠀', value=f'{self.member.reputation}', inline=True)
        emb.add_field(name='Information     ⠀', value=f'Level: No info\nJoined: {join_time}', inline=True)
        emb.set_author(name=self.author.name, icon_url=self.author.avatar)
        await interaction.response.edit_message(embed=emb, view=self)

    @discord.ui.button(label='Roles', style=discord.ButtonStyle.gray, custom_id='roleButton')
    async def roles_button_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        emb = discord.Embed(colour=COLOUR, description='All roles have limited time. \n'
                                                       'To update your role time use **/roleupdate**')
        emb.add_field(name='Current Roles', value='<@&943619597708443732>\n<@&943621521199468574>', inline=True)
        emb.set_author(name=self.author.name, icon_url=self.author.avatar)
        await interaction.response.edit_message(embed=emb, view=self)

    @discord.ui.button(label='Duel History', style=discord.ButtonStyle.gray, custom_id='duelButton')
    async def battles_button_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        emb = discord.Embed()

        history = ""
        duels = self.member.duels
        low, high = get(self.author.guild.emojis, name="low"), get(self.author.guild.emojis, name="high")
        for i in range(min(len(duels), 10) - 1, -1, -1):
            won = True if int(self.author.id) == int(duels[i].winner) else False
            history += f"{high if won else low} **{'Won' if won else 'Lose'}** — **{duels[i].pay}** {datetime.strftime(duels[i].timestamp, '%d.%m.%y')}\n "

        # checks if emd.add_field(value) won't be empty
        if history == '':
            history += "you didn't duel someone"

        emb.add_field(name='Last 10 duels', value=history)
        await interaction.response.edit_message(embed=emb, view=self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
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

        join_time = interaction.user.joined_at.strftime("%b %d, %Y @ %I:%M %p")
        emb = discord.Embed(colour=COLOUR)
        emb.add_field(name='Coins           ⠀', value=f'**{sql_member.coins}**', inline=True)
        emb.add_field(name='Reputation      ⠀', value=f'{sql_member.reputation}', inline=True)
        emb.add_field(name='Information     ⠀', value=f'Level: No info\nJoin time: {join_time}', inline=True)
        emb.set_author(name=interaction.user, icon_url=interaction.user.avatar)

        profile = profileView(interaction.user, sql_member)

        await interaction.response.send_message(embed=emb, view=profile)

    @app_commands.command(name='bonus', description='Gives you 100 coins')
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


async def setup(bot: commands.Bot):
    await bot.add_cog(InterCog(bot))
