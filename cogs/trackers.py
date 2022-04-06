import discord
from discord import app_commands
from discord.ext import commands

COLOUR = 0x242424
WHERE_IS_MY_PANCAKES = 894192291831504959
HAPPY_TEST_BOT = 777145173574418462

SERVER_ID = HAPPY_TEST_BOT
GUILD = discord.Object(SERVER_ID)


class TrackerCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        print(f"Loaded {self.__cog_name__}")

    @app_commands.command(name='apex', description='Shows your Apex stats')
    @app_commands.guilds(GUILD)
    async def apex(self, interaction: discord.Interaction):
        emb = discord.Embed(colour=COLOUR)
        emb.add_field(name='Apex', value='Apex tracker command')
        await interaction.response.send_message(embed=emb)

    @app_commands.command(name='valorant', description='Shows your Valorant stats')
    @app_commands.guilds(GUILD)
    async def google(self, interaction: discord.Interaction):
        emb = discord.Embed(colour=COLOUR)
        emb.add_field(name='Valorant', value='Valorant tracker command')
        await interaction.response.send_message(embed=emb)


async def setup(bot: commands.Bot):
    await bot.add_cog(TrackerCog(bot))
