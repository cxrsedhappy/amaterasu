import datetime

import discord
from discord import ui
from discord.utils import get


HAPPY_TEST_BOT = 777145173574418462
SERVER_ID = 777145173574418462
COLOUR = 0x242424


class profileView(ui.View):
    def __init__(self, author: discord.Member, sql_member):
        super().__init__()
        self.author = author
        self.member = sql_member
        self.embeds = []

        # General embed ------------------------------------------------------------------------------
        emb = discord.Embed(colour=COLOUR)
        emb.set_author(name=self.author.name, icon_url=self.author.avatar)
        emb.add_field(name='Coins           ⠀', value=f'**{self.member.coins}**', inline=True)
        emb.add_field(name='Reputation      ⠀', value=f'{self.member.reputation}', inline=True)
        self.embeds.append(emb)

        # Roles embed --------------------------------------------------------------------------------
        white_listed_description = ''
        black_listed_description = ''
        for role in self.member.roles:
            if role.white_listed is True:
                white_listed_description += f'<@&{role.id}>\n'
            else:
                black_listed_description += f'<@&{role.id}>\n'

        emb = discord.Embed(colour=COLOUR,
                            title='Roles',
                            description='To update your role time use **/roleupdate**\n\n'
                                        'White listed roles mean they have **no expiration**.\n '
                                        'Those roles can be gifted from server admins\n\n'
                                        'Current roles means this roles have **expiration** date.\n\n')
        emb.add_field(name='White Listed Roles',
                      value=white_listed_description if white_listed_description != '' else 'None')
        emb.add_field(name='Current Roles',
                      value=black_listed_description if black_listed_description != '' else 'None')
        self.embeds.append(emb)

        # Battle embed -------------------------------------------------------------------------------
        value_to_emb = ''
        duels = self.member.duels
        duels.reverse()

        low, high = get(self.author.guild.emojis, name="low"), get(self.author.guild.emojis, name="high")

        for i in range(min(len(duels), 10)):
            won = True if int(self.author.id) == int(duels[i].winner) else False
            value_to_emb += f"{high if won else low} **{'Won' if won else 'Lose'}** — **{duels[i].pay}** " \
                            f"{datetime.datetime.strftime(duels[i].timestamp, '%d.%m.%y')}\n"

        # checks if emd.add_field(value) isn't empty
        if value_to_emb == '':
            value_to_emb += "You didn't duel someone"

        emb = discord.Embed(colour=COLOUR, title='Battles')
        emb.add_field(name='Last 10 duels', value=value_to_emb)
        self.embeds.append(emb)

        # Setting embed -----------------------------------------------------------------------------
        emb = discord.Embed(colour=COLOUR, title='Settings')
        emb.add_field(name='Profile', value=f"{'**Private**' if self.member.profile_is_private else 'Public'}")
        emb.set_footer(text='You will be able to toggle your profile settings soon...')
        self.embeds.append(emb)

    @discord.ui.button(label='General', style=discord.ButtonStyle.blurple, custom_id='generalButton')
    async def general_button_callback(self, interaction: discord.Interaction, button: discord.Button):
        emb = self.embeds[0]
        join_time = interaction.user.joined_at.strftime("%a, %b %d, %Y @ %I:%M %p")
        emb.add_field(name='Information     ⠀', value=f'Level: Soon\nJoined: {join_time}', inline=True)
        await interaction.response.edit_message(embed=emb, view=self)

    @discord.ui.button(label='Roles', style=discord.ButtonStyle.blurple, custom_id='roleButton')
    async def roles_button_callback(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.edit_message(embed=self.embeds[1], view=self)

    @discord.ui.button(label='History', style=discord.ButtonStyle.blurple, custom_id='duelButton')
    async def battles_button_callback(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.edit_message(embed=self.embeds[2], view=self)

    @discord.ui.button(label='Settings', style=discord.ButtonStyle.blurple, custom_id='settingsButton')
    async def settings_button_callback(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.edit_message(embed=self.embeds[3])

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """
        TODO
        Bug with interaction_check
        If Bob used command and didn't click the button
        And ALice used this command too
        Alice can click on Bob's buttons (Bob can't click his buttons)
        """
        if interaction.user.id == self.author.id:
            return True
        return False
