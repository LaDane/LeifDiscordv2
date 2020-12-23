import discord
import json 
import asyncio

from discord.ext import commands 
from discord.utils import get 

from lib import FileHandler, GuildEmojis, GuildUserGroup, UpdateMission # pylint: disable=no-name-in-module

fh = FileHandler()


class MissionSignup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 

    def load_data(self):
        self.id = fh.load_file('id')
        self.mission = fh.load_file('mission')

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        self.load_data()
        bot_id = self.id['RDF']['discord_bot_id']
        if payload.user_id == bot_id:
            return  # bot reacted

        reaction = payload.emoji.name 
        white_check_emoji = '\u2705'
        x_emoji = '\u274C'
        if reaction not in [white_check_emoji, x_emoji]:
            return  # not correct reaction emoji

        titles = []
        for title, value in self.mission.items():
            for msg in value.values():
                if msg == payload.message_id:
                    titles.append(title)
        mission_date_time = ''.join(titles)

        if mission_date_time != "":
            guild = self.bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            member_id = payload.user_id 
            member_nick = member.nick 
            if member_nick == None:
                member_nick = member.name 
            self.g_emoji = GuildEmojis(guild)
            self.g_usergroup = GuildUserGroup(self.bot)
            self.u_mission = UpdateMission(self.bot)
            member_group = await self.g_usergroup.checkgroup(guild, member)
            member_role = await self.g_usergroup.checkrole(guild, member)
            mission_type = self.mission[mission_date_time]['type']

            if mission_type in ["Torsdags Mission", "Hygge Mission", "Special Events"]:
                if reaction == white_check_emoji and str(member_id) not in self.mission[mission_date_time]['absent']:
                    self.mission[mission_date_time]['attending'][member_id] = {}
                    self.mission[mission_date_time]['attending'][member_id]['user_name'] = member_nick 
                    self.mission[mission_date_time]['attending'][member_id]['group'] = member_group

                    if member_group == "Gruppeløs":
                        self.mission[mission_date_time]['attending'][member_id]['emoji_member_id'] = f":grey_question: <@{member_id}>"

                    elif member_group != "Gruppeløs" and member_role == "Gruppeløs" and mission_type == "Torsdags Mission":
                        self.mission[mission_date_time]['attending'][member_id]['emoji_member_id'] = f"{self.g_emoji.guild_groups[member_group]} <@{member_id}>"

                    elif member_role != "Gruppeløs" and mission_type == "Torsdags Mission":
                        self.mission[mission_date_time]['attending'][member_id]['role'] = member_role
                        self.mission[mission_date_time]['attending'][member_id]['emoji_member_id'] = f"{self.g_emoji.guild_roles[member_role]} <@{member_id}>"

                    elif member_group != "Gruppeløs" and mission_type in ["Hygge Mission", "Special Events"]:
                        self.mission[mission_date_time]['attending'][member_id]['emoji_member_id'] = f"{self.g_emoji.guild_groups[member_group]} <@{member_id}>"
                    
                if reaction == x_emoji and str(member_id) not in self.mission[mission_date_time]['attending']:
                    self.mission[mission_date_time]['absent'][member_id] = {}
                    self.mission[mission_date_time]['absent'][member_id]['user_name'] = member_nick 
                    self.mission[mission_date_time]['absent'][member_id]['group'] = member_group                     
                    if member_group == "Gruppeløs":
                        self.mission[mission_date_time]['absent'][member_id]['emoji_member_id'] = f":grey_question: <@{member_id}>"
                    elif member_group != "Gruppeløs":
                        self.mission[mission_date_time]['absent'][member_id]['emoji_member_id'] = f"{self.g_emoji.guild_groups[member_group]} <@{member_id}>"

                if mission_type == "Torsdags Mission":
                    if str(member_id) in self.mission[mission_date_time]['deltagerliste']:
                        del self.mission[mission_date_time]['deltagerliste'][str(member_id)]
                fh.save_file(self.mission, 'mission')

                if mission_type == "Torsdags Mission":
                    await self.u_mission.UpdateMissionEmbed(guild, mission_date_time, "Torsdags Mission", False)       # Update "Torsdags Mission" with data from json
                    await self.u_mission.UpdateMissionEmbed(guild, mission_date_time, "Deltagerliste", False)          # Update "Deltagerliste" with data from json  

                if mission_type in ["Hygge Mission", "Special Events"]:
                    if mission_type == "Special Events" and reaction == white_check_emoji:
                        special_needs_role = discord.utils.get(guild.roles, name='Special-Needs')
                        await member.add_roles(special_needs_role)                                              # gives member "Special Needs" role
                    await self.u_mission.UpdateHyggeSpecialEmbed(guild, mission_date_time, mission_type, False) # Update "Hygge Mission" / "Special Events" with data from json


    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        self.load_data()
        bot_id = self.id['RDF']['discord_bot_id']
        if payload.user_id == bot_id:
            return  # bot reacted

        reaction = payload.emoji.name 
        white_check_emoji = '\u2705'
        x_emoji = '\u274C'
        if reaction not in [white_check_emoji, x_emoji]:
            return  # not correct reaction emoji

        titles = []
        for title, value in self.mission.items():
            for msg in value.values():
                if msg == payload.message_id:
                    titles.append(title)
        mission_date_time = ''.join(titles)

        if mission_date_time != "":
            guild = self.bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            member_id = payload.user_id 
            member_nick = member.nick 
            if member_nick == None:
                member_nick = member.name 
            self.g_emoji = GuildEmojis(guild)
            self.g_usergroup = GuildUserGroup(self.bot)
            self.u_mission = UpdateMission(self.bot)
            member_group = await self.g_usergroup.checkgroup(guild, member)
            # member_role = await self.g_usergroup.checkrole(guild, member)
            mission_type = self.mission[mission_date_time]['type']

            if mission_type in ["Torsdags Mission", "Hygge Mission", "Special Events"]:
                if reaction == white_check_emoji and str(member_id) not in self.mission[mission_date_time]['absent'] and str(member_id) in self.mission[mission_date_time]['attending']:
                    del self.mission[mission_date_time]['attending'][str(member_id)]
                    fh.save_file(self.mission, 'mission')
                if reaction == x_emoji and str(member_id) not in self.mission[mission_date_time]['attending'] and str(member_id) in self.mission[mission_date_time]['absent']:
                    del self.mission[mission_date_time]['absent'][str(member_id)]
                    fh.save_file(self.mission, 'mission')

                if mission_type == "Torsdags Mission":
                    self.load_data()
                    for group_name, group_emoji in self.g_emoji.guild_groups.items():
                        key_group = discord.utils.get(guild.roles, name = group_name)
                        medlem_role = discord.utils.get(guild.roles, name = "Medlem")
                        prøve_role = discord.utils.get(guild.roles, name = "Prøve Medlem")
                        orlov_role = discord.utils.get(guild.roles, name = "Orlov")                        
                        if prøve_role in member.roles:
                            self.mission[mission_date_time]['deltagerliste'][member_id] = {}
                            self.mission[mission_date_time]['deltagerliste'][member_id]['user_name'] = member_nick 
                            self.mission[mission_date_time]['deltagerliste'][member_id]['group'] = "Prøve Medlem"
                            self.mission[mission_date_time]['deltagerliste'][member_id]['emoji_member_id'] = f"{self.g_emoji.guild_groups['Prøve Medlem']} <@{member_id}>"
                            continue 
                        if orlov_role in member.roles:
                            self.mission[mission_date_time]['deltagerliste'][member_id] = {}
                            self.mission[mission_date_time]['deltagerliste'][member_id]['user_name'] = member_nick 
                            self.mission[mission_date_time]['deltagerliste'][member_id]['group'] = "Orlov"
                            self.mission[mission_date_time]['deltagerliste'][member_id]['emoji_member_id'] = f":palm_tree: <@{member_id}>"
                            continue 
                        if member_group == "Gruppeløs":
                            self.mission[mission_date_time]['deltagerliste'][member_id] = {}
                            self.mission[mission_date_time]['deltagerliste'][member_id]['user_name'] = member_nick 
                            self.mission[mission_date_time]['deltagerliste'][member_id]['group'] = "Gruppeløs"
                            self.mission[mission_date_time]['deltagerliste'][member_id]['emoji_member_id'] = f":grey_question: <@{member_id}>"
                            continue 
                        if medlem_role in member.roles and key_group in member.roles:
                            for role_name, role_emoji in self.g_emoji.guild_roles.items():
                                key_role = discord.utils.get(guild.roles, name = role_name)
                                if key_role in member.roles:
                                    self.mission[mission_date_time]['deltagerliste'][member_id] = {}
                                    self.mission[mission_date_time]['deltagerliste'][member_id]['user_name'] = member_nick 
                                    self.mission[mission_date_time]['deltagerliste'][member_id]['group'] = group_name
                                    self.mission[mission_date_time]['deltagerliste'][member_id]['role'] = role_name
                                    self.mission[mission_date_time]['deltagerliste'][member_id]['emoji_member_id'] = f"{role_emoji} <@{member_id}>"
                                    break  
                            else:
                                self.mission[mission_date_time]['deltagerliste'][member_id] = {}
                                self.mission[mission_date_time]['deltagerliste'][member_id]['user_name'] = member_nick 
                                self.mission[mission_date_time]['deltagerliste'][member_id]['group'] = group_name
                                self.mission[mission_date_time]['deltagerliste'][member_id]['emoji_member_id'] = f"{group_emoji} <@{member_id}>"
                                continue                    
                    fh.save_file(self.mission, 'mission')

                await asyncio.sleep(0.2)
                if mission_type == "Torsdags Mission":
                    await self.u_mission.UpdateMissionEmbed(guild, mission_date_time, "Torsdags Mission", False)       # Update "Torsdags Mission" with data from json
                    await self.u_mission.UpdateMissionEmbed(guild, mission_date_time, "Deltagerliste", False)          # Update "Deltagerliste" with data from json  

                if mission_type in ["Hygge Mission", "Special Events"]:
                    if mission_type == "Special Events":
                        special_needs_role = discord.utils.get(guild.roles, name='Special-Needs')
                        if special_needs_role in member.roles and reaction == white_check_emoji:
                            await member.remove_roles(special_needs_role)                                               # removes "Special Needs" role
                    await self.u_mission.UpdateHyggeSpecialEmbed(guild, mission_date_time, mission_type, False)     # Update "Hygge Mission" / "Special Events" with data from json



def setup(bot):
    bot.add_cog(MissionSignup(bot))
