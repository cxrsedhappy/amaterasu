import datetime
import discord
from discord import ui
from discord.ext import commands

from data.user_role import Role


LONELY_SERVER = 802271249966563338
WHERE_IS_MY_PANCAKES = 894192291831504959
HAPPY_TEST_BOT = 777145173574418462

SERVER_ID = LONELY_SERVER
COLOUR = 0x242424


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
        r.enabled = True
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
        if interaction.user.id == self.author.id:
            return True
        return False
