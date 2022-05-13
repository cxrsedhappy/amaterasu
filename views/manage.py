import discord
from discord import ui
from discord.ext import commands
from sqlalchemy.orm import Session

from data.user_role import Member

SERVER_ID = 777145173574418462
COLOUR = 0x242424


# /role manage
class manageDropdown(ui.Select):
    def __init__(self, con: Session, member_id: int, bot: commands.Bot):
        super().__init__(placeholder='We trying to rework this command', min_values=1, max_values=1, disabled=True)
        self.member = con.query(Member).where(Member.id == member_id).first()
        self.con = con
        self.roles_to_show = []
        self.bot = bot

        member_roles = self.member.roles
        for i in range(len(member_roles)):
            self.roles_to_show.append(member_roles[i])
            self.options.append(discord.SelectOption(label=member_roles[i].name,
                                                     description=member_roles[i].id,
                                                     value=f'{i}'))

    async def callback(self, interaction: discord.Interaction):
        for i in self.values:
            print(i)
        role = self.member.roles[int(self.values[0])]
        discord_role = self.bot.get_guild(SERVER_ID).get_role(role.id)

        if role.enabled is True:
            role.enabled = False
            await self.bot.get_guild(SERVER_ID).get_member(interaction.user.id).remove_roles(discord_role)
        else:
            role.enabled = True
            await self.bot.get_guild(SERVER_ID).get_member(interaction.user.id).add_roles(discord_role)

        self.con.commit()
        # I think this embed is too big for this?
        # I have update button already
        emb = discord.Embed(colour=COLOUR)
        emb.add_field(name='Done', value=f'{role.name} was {"enabled" if role.enabled is True else "disabled"}')
        await interaction.response.send_message(embed=emb, ephemeral=True)


class manageView(ui.View):
    """
    TODO
    Rework role manage logic
    """

    def __init__(self, author: discord.Member, con: Session, bot: commands.Bot):
        super().__init__()
        self.author = author
        self.con = con
        self.add_item(manageDropdown(self.con, self.author.id, bot))

    def update_info(self):
        mem = self.con.query(Member).where(Member.id == self.author.id).first()

        exp_time = ''
        value_for_emb = ''

        for role in mem.roles:
            if role.white_listed is False:
                exp_time = discord.utils.format_dt(role.expired_at)

            value_for_emb += f'{":white_check_mark:" if role.enabled else ":x:"}<@&{role.id}>' \
                             f'[{role.multiplier}x] - ' \
                             f'{f"expire at {exp_time}" if role.white_listed is False else f"No expiration date"} \n '

        emb = discord.Embed(colour=COLOUR)
        emb.add_field(name=':file_folder: Your roles', value=value_for_emb)
        return emb

    @discord.ui.button(label='Update', style=discord.ButtonStyle.blurple, custom_id='updateButton', disabled=True)
    async def update_button_callback(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.edit_message(embed=self.update_info())

    @discord.ui.button(label='Disable all', style=discord.ButtonStyle.blurple, custom_id='disableButton', disabled=True)
    async def disable_button_callback(self, interaction: discord.Interaction, button: discord.Button):
        pass

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author.id:
            return False
        return True
