import discord

from random import randint
from data.db_session import create_session
from data.user_role import Member, Duel
from discord import app_commands, ui
from discord.ext import commands

COLOUR = 0x242424


class profileView(ui.View):
    def __init__(self, ctx: discord.Interaction, query):
        super().__init__()
        self.ctx = ctx
        self.query = query

    @discord.ui.button(label='General', style=discord.ButtonStyle.gray, custom_id='generalButton')
    async def general_button_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        emb = discord.Embed(colour=COLOUR)
        join_time = interaction.user.joined_at.strftime("%a, %b %d, %Y @ %I:%M %p")
        emb.add_field(name='Coins           ⠀', value=f'**{self.query.coins}**', inline=True)
        emb.add_field(name='Reputation      ⠀', value=f'{self.query.reputation}', inline=True)
        emb.add_field(name='Information     ⠀', value=f'Level: 34\n{join_time}', inline=True)
        emb.set_author(name=self.ctx.user, icon_url=self.ctx.user.avatar)
        await interaction.response.edit_message(embed=emb)

    @discord.ui.button(label='Roles', style=discord.ButtonStyle.gray, custom_id='roleButton')
    async def roles_button_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        emb = discord.Embed(colour=COLOUR, description='All roles have limited time. \n'
                                                       'To update your role time use **/roleupdate**')
        emb.add_field(name='Current Roles', value='<@&943619597708443732>\n<@&943621521199468574>', inline=True)
        emb.set_author(name=self.ctx.user, icon_url=self.ctx.user.avatar)
        await interaction.response.edit_message(embed=emb)

    @discord.ui.button(label='Duel History', style=discord.ButtonStyle.gray, custom_id='duelButton', disabled=True)
    async def battles_button_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message('heh')

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.ctx.user:
            return False
        return True


class duelView(ui.View):
    def __init__(self, ctx: discord.Interaction, enemy: discord.Member, coins: int):
        super().__init__()
        self.ctx = ctx
        self.enemy = enemy
        self.coins = coins

    @discord.ui.button(label='✔', style=discord.ButtonStyle.green, custom_id='agreeButton')
    async def agreeButton_callback(self, button: discord.Button, interaction: discord.Interaction):
        """
        TODO:
        Relocate coin checker to /duel command  Done: -
        Add check from self dueling             Done: -
        Add mention to embeds                   Done: -
        """

        """
        This callback send 2 requests to Database
        """
        connection = create_session()
        f_duelist = connection.query(Member).where(Member.id == self.ctx.user.id).first()
        s_duelist = connection.query(Member).where(Member.id == self.enemy.id).first()

        emb = discord.Embed()
        emb.set_author(name=interaction.user, icon_url=interaction.user.avatar)
        if f_duelist.coins < self.coins or s_duelist.coins < self.coins:
            emb.description = f"One of you don't have **{self.coins}** to duel"
            await interaction.response.send_message(embed=emb)
            return

        duel = Duel()
        duel.duelist_one = interaction.user.id
        duel.duelist_two = self.enemy.id
        duel.pay = self.coins

        if randint(1, 100) > 50:
            duel.winner = interaction.user.id
            f_duelist.coins += self.coins
            f_duelist.duels.append(duel)
            s_duelist.coins -= self.coins
            s_duelist.duels.append(duel)
        else:
            duel.winner = self.enemy.id
            f_duelist.coins -= self.coins
            f_duelist.duels.append(duel)
            s_duelist.coins += self.coins
            s_duelist.duels.append(duel)

        emb.description = f'<@{duel.winner}> won and earn **{self.coins} coins!**'
        connection.commit()
        connection.close()
        await interaction.response.edit_message(embed=emb, view=None)

    @discord.ui.button(label='✖', style=discord.ButtonStyle.danger, custom_id='refuseButton')
    async def refuseButton_callback(self, button: discord.Button, interaction: discord.Interaction):
        emb = discord.Embed(description=f"{self.ctx.user.mention} your enemy refused duel!")
        await interaction.response.edit_message(embed=emb, view=None)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.enemy.id:
            return False
        return True


class InterCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        print(f"Loaded {self.__cog_name__}")

    @app_commands.command(name="profile", description="Show up your profile")
    @app_commands.guilds(discord.Object(777145173574418462))
    async def profile(self, interaction: discord.Interaction):
        connection = create_session()
        member = connection.query(Member).where(Member.id == interaction.user.id).first()
        connection.close()

        join_time = interaction.user.joined_at.strftime("%b %d, %Y @ %I:%M %p")
        emb = discord.Embed(colour=COLOUR)
        emb.add_field(name='Coins           ⠀', value=f'**{member.coins}**', inline=True)
        emb.add_field(name='Reputation      ⠀', value=f'{member.reputation}', inline=True)
        emb.add_field(name='Information     ⠀', value=f'Level: No info\nJoin time: {join_time}', inline=True)
        emb.set_author(name=interaction.user, icon_url=interaction.user.avatar)
        await interaction.response.send_message(embed=emb, view=profileView(interaction, member))

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
        emb.set_author(name=interaction.user, icon_url=interaction.user.avatar)
        await interaction.response.send_message(embed=emb)

    @app_commands.command(name='duel', description='Invite your enemy to a duel')
    @app_commands.guilds(discord.Object(777145173574418462))
    async def duel(self, interaction: discord.Interaction, enemy: discord.Member, coins: int):
        emb = discord.Embed(description=f'{enemy.mention} was invited to duel! Do you accept?')
        emb.set_author(name=interaction.user, icon_url=interaction.user.avatar)
        await interaction.response.send_message(embed=emb, view=duelView(interaction, enemy, coins))


async def setup(bot: commands.Bot):
    await bot.add_cog(InterCog(bot))
