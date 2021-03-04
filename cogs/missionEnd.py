import discord 
import json 

from discord.ext import commands 
from discord.utils import get 
from lib import FileHandler, UpdateMission # pylint: disable=no-name-in-module

fh = FileHandler()


class MissionEnd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 

    def load_data(self):
        self.mission = fh.load_file('mission')

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        self.load_data()
        reaction = payload.emoji.name 
        if reaction != '\U0001F51A':
            return 

        titles = []
        for title, value in self.mission.items():
            for msg in value.values():
                if msg == payload.message_id:
                    titles.append(title)
        mission_date_time = ''.join(titles)

        if mission_date_time != "":
            guild = self.bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            udvikler_role = discord.utils.get(guild.roles, name='Udvikler')
            ai_role = discord.utils.get(guild.roles, name='AI')

            if reaction == '\U0001F51A':
                if udvikler_role in member.roles or ai_role in member.roles:
                    self.u_mission = UpdateMission(self.bot)
                    mission_type = self.mission[mission_date_time]['type']
                    if mission_type == "Torsdags Mission":
                        await self.u_mission.UpdateMissionEmbed(guild, mission_date_time, mission_type, True)
                    if mission_type in ["Hygge Mission", "Special Events"]:
                        await self.u_mission.UpdateHyggeSpecialEmbed(guild, mission_date_time, mission_type, True)

                    leifbot_channel = discord.utils.get(guild.text_channels, name="leifbot")
                    leifbot_embed = discord.Embed(title="Mission Afsluttet", description=f"<@{payload.user_id}> har afsluttet en **{mission_type}**",color=0x303136)
                    await leifbot_channel.send(embed=leifbot_embed)                    

def setup(bot):
    bot.add_cog(MissionEnd(bot))
