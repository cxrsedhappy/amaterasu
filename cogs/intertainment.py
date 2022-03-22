import discord

from typing import Literal
from discord import app_commands, ui
from discord.ext import commands


COLOUR = 0x242424


class MyView(ui.View):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

    @discord.ui.button(label='go kys', style=discord.ButtonStyle.green, custom_id='kys')
    async def kys_callback(self, button, interaction: discord.Interaction):
        await interaction.response.send_message('cool', ephemeral=True)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        print(interaction.user.id)
        print(self.ctx.user)
        if interaction.user != self.ctx.user:
            await interaction.response.send_modal('wrong user', ephemeral=True)
            return False
        return True


class profileView(ui.View):
    def __init__(self, ctx: discord.Interaction):
        super().__init__()
        self.ctx = ctx

    @discord.ui.button(label='General', style=discord.ButtonStyle.gray, custom_id='generalButton')
    async def general_button_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        emb = discord.Embed(colour=COLOUR)
        emb.add_field(name='Coins           ⠀', value='**500**', inline=True)
        emb.add_field(name='Reputation      ⠀', value='25', inline=True)
        emb.add_field(name='Information     ⠀', value='Level: 34\nJoined: 29.10.24', inline=True)
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


class newAlertModalFloorAlert(ui.Modal, title='Enter collection slug'):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)
    userInput = ui.TextInput(label='Collection Slug')

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.edit_message(embed=None, content=f'`{self.userInput}`** - is this correct?**')


class InterCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        print(f"Loaded {self.__cog_name__}")

    @app_commands.command(name="profile", description="Show up your profile")
    @app_commands.guilds(discord.Object(777145173574418462))
    async def profile(self, interaction: discord.Interaction):
        emb = discord.Embed(colour=COLOUR)
        emb.add_field(name='Coins           ⠀', value='**500**', inline=True)
        emb.add_field(name='Reputation      ⠀', value='25', inline=True)
        emb.add_field(name='Information     ⠀', value='Level: 34\nJoined: 29.10.24', inline=True)
        emb.set_author(name=interaction.user, icon_url=interaction.user.avatar)
        await interaction.response.send_message(embed=emb, view=profileView(interaction))


async def setup(bot: commands.Bot):
    await bot.add_cog(InterCog(bot))
