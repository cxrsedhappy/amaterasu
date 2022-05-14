import discord
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands
from wrappers.pypex import API

COLOUR = 0x242424
WHERE_IS_MY_PANCAKES = 894192291831504959
HAPPY_TEST_BOT = 777145173574418462
LONELY_SERVER = 802271249966563338

SERVER_ID = HAPPY_TEST_BOT
GUILD = discord.Object(SERVER_ID)


class TrackerCog(commands.Cog):
    track = app_commands.Group(name='tracker', description='Tracker commands')

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.apex_api = API(api_key='QFMbvc2VXPKUs3MdH7EW')

    async def cog_load(self):
        print(f"Loaded {self.__cog_name__}")

    @track.command(name='apex', description='Shows your Apex stats')
    @app_commands.choices(platforms=[
        Choice(name='PC', value='PC'),
        Choice(name='PSN', value='PSN'),
        Choice(name='XBOX', value='XBOX'),
    ])
    async def apex(self, interaction: discord.Interaction, name: str, platforms: Choice[str]):
        await interaction.response.defer()

        player = self.apex_api.get_player(name=name, platform=platforms.value)
        if player is None:
            emb = discord.Embed(colour=COLOUR)
            emb.add_field(name='Error', value=f"Couldn't find player on {platforms.value}")
            await interaction.followup.send(embed=emb)
            return

        main = player.global_player
        realtime = player.realtime_player

        description_to_embed = f"{main.name}: {realtime.currentState}\n" \
                               f"Platform: {main.platform}\n" \
                               f"Level: {main.level}\n"

        fields = list()
        fields.append(f"MMR:\n"
                      f"**{main.mm_rankScore}**\n"
                      f"DIVISION:\n"
                      f"{main.mm_rankAsText}")

        fields.append(f"MMR:\n"
                      f"**{main.ar_rankScore}**\n"
                      f"DIVISION:\n"
                      f"{main.ar_rankAsText}")

        emb = discord.Embed(colour=COLOUR, description=description_to_embed)
        emb.add_field(name='Ranked Matchmaking', value=fields[0], inline=True)
        emb.add_field(name='Ranked Arena', value=fields[1], inline=True)
        emb.set_thumbnail(url=main.mm_rankImg)
        await interaction.followup.send(embed=emb)

    # @track.command(name='valorant', description='Shows your Valorant stats')
    # async def valorant(self, interaction: discord.Interaction):
    #     emb = discord.Embed(colour=COLOUR)
    #     emb.add_field(name='Valorant', value='Valorant tracker command')
    #     await interaction.response.send_message(embed=emb)


async def setup(bot: commands.Bot):
    await bot.add_cog(TrackerCog(bot))
