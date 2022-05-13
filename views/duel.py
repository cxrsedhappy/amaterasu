import datetime
from random import randint

import discord
from discord import ui

from data.user_role import Duel


SERVER_ID = 777145173574418462
COLOUR = 0x242424


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

        await interaction.response.edit_message(embed=emb, view=None)
        self.stop()

    @discord.ui.button(label='✖', style=discord.ButtonStyle.danger, custom_id='refuseButton')
    async def refuse_button_callback(self, interaction: discord.Interaction, button: discord.Button):
        emb = discord.Embed(description=f"<@{self.author.id}> your enemy refused duel!", colour=COLOUR)
        await interaction.response.edit_message(embed=emb, view=None)
        self.stop()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.enemy.id:
            return True
        return False