import discord 
import time
import asyncio 

from discord.ext import commands 
from discord.utils import get 
from datetime import datetime 
from lib import FileHandler, GuildEmojis, GuildUserGroup, UpdateMission # pylint: disable=no-name-in-module

fh = FileHandler()
updateTime = "05:00:00"          # 05:00:00


class DataUpdate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 

    def load_data(self):
        self.id = fh.load_file('id')
        self.mission = fh.load_file('mission')

# LOOP TIME CHECK
    @commands.Cog.listener()
    async def on_ready(self):
        has_updated = False
        while not self.bot.is_closed():
            current = datetime.now()
            current_time = current.strftime("%H:%M:%S")
            if (current_time == updateTime and has_updated == False):
                has_updated == True
                await self.DataUpdateEntries()
                await asyncio.sleep(60)
                has_updated == False
            elif (current_time == "05:00:15" and has_updated == False):
                has_updated == True
                await self.DataUpdateEntries()
                await asyncio.sleep(60)
                has_updated == False
            elif (current_time == "05:00:30" and has_updated == False):
                has_updated == True
                await self.DataUpdateEntries()
                await asyncio.sleep(60)
                has_updated == False
            elif (current_time == "05:00:45" and has_updated == False):
                has_updated == True
                await self.DataUpdateEntries()
                await asyncio.sleep(60)
                has_updated == False                 
            else:
                await asyncio.sleep(1)


# USER COMMAND - DATAUPDATE
    @commands.command(name="dataupdate")
    async def dataupdate_command(self, ctx):
        self.load_data()
        guild = ctx.message.guild 
        member = guild.get_member(ctx.author.id)
        udvikler_role = discord.utils.get(guild.roles, name='Udvikler')
        leifbot_channel = self.bot.get_channel(self.id["RDF"]["leifbot_channel_id"])

        if udvikler_role in member.roles:
            if leifbot_channel == ctx.channel:
                leifbot_embed = discord.Embed(title="Data update", description=f"<@{ctx.author.id}> has run **+dataupdate**, starting to update json data entries", color=0x303136)
                await leifbot_channel.send(embed=leifbot_embed)                
                await self.DataUpdateEntries()
            else:
                leifbot_embed = discord.Embed(title="Command Error", description=f"<@{ctx.author.id}> has tried to run **+dataupdate**, in the wrong channel**", color=0x303136)
                await leifbot_channel.send(embed=leifbot_embed) 
        else:
            leifbot_embed = discord.Embed(title="Command Error", description=f"<@{ctx.author.id}> har tried to run **+dataupdate**, but does not have 'Udvikler' role", color=0x303136)
            await leifbot_channel.send(embed=leifbot_embed) 


# UPDATE DATA IN MISSION JSON 
    async def DataUpdateEntries(self):
        print(" ")
        print("Starting data entries update.")
        self.load_data()
        guild = self.bot.get_guild(self.id['RDF']['guild_id'])
        leifbot_channel = self.bot.get_channel(self.id["RDF"]["leifbot_channel_id"])

        returned_members_check1 = ""
        for mission_date_time, value in self.mission.items():
            if value['type'] == "Torsdags Mission":
                attending_values = list(value['attending'])
                absent_values = list(value['absent'])
                deltagerliste_values = list(value['deltagerliste'])                
                for member in guild.members:
                    returned_member_1 = await self.CheckMember("CheckMemberInList", guild, leifbot_channel, member, mission_date_time, "Torsdags Mission", "deltagerliste", attending_values, absent_values, deltagerliste_values)
                    if returned_member_1 != None:
                        returned_members_check1 += f"{returned_member_1}"

        print("Checked for missing members in Torsdags Mission deltagerliste")
        if returned_members_check1 != "":
            leifbot_embed = discord.Embed(title="Checked for missing members in 'Torsdags Mission deltagerliste'\nFollowing members have been added to database:", description=f"{returned_members_check1}", color=0x303136)
            await leifbot_channel.send(embed=leifbot_embed)
        self.load_data()

        mission_states = ["attending", "absent", "deltagerliste"]
        for mission_state in mission_states:
            for mission_date_time, value in self.mission.items():
                mission_type = value['type']
                if mission_type != "Torsdags Mission" and mission_state == "deltagerliste":
                    continue 
                returned_members_check2 = {}
                removed_members = ""                
                for member_id in list(value[mission_state]):
                    member = guild.get_member(int(member_id))
                    if member == None:
                        removed_members += f"<@{self.mission[mission_date_time][mission_state][member_id]['user_name']}> \n"
                        del self.mission[mission_date_time][mission_state][member_id]
                        fh.save_file(self.mission, 'mission')
                        await asyncio.sleep(0.3)
                        continue 
                    returned_member_2 = await self.CheckMember("CheckMemberGroupRole", guild, leifbot_channel, member, mission_date_time, mission_type, mission_state, "None", "None", "None")
                    if returned_member_2 != None:
                        returned_members_check2.update(returned_member_2)

                if returned_members_check2 != {}:
                    sorted_list = ""
                    for name, userID in sorted(returned_members_check2.items()):
                        _ = name
                        sorted_list += userID
                    sorted_list = sorted_list.strip(',')
                    sorted_list = list(sorted_list.split(','))
                    sorted_list_len = len(sorted_list)
                    sorted_list_chunks = list([sorted_list[i*sorted_list_len // 3: (i+1)*sorted_list_len // 3] for i in range(3)])
                    sorted_list_chunk_1 = ''.join(list(sorted_list_chunks[0]))
                    sorted_list_chunk_2 = ''.join(list(sorted_list_chunks[1]))
                    sorted_list_chunk_3 = ''.join(list(sorted_list_chunks[2]))

                    leifbot_embed = discord.Embed(title=f"Member database entries updated.\n\n{mission_type}\n{mission_date_time}\n{mission_state}", color=0x303136)
                    if sorted_list_chunk_1 != "":
                        leifbot_embed.add_field(name="\u200B", value=f"{sorted_list_chunk_1}")
                    if sorted_list_chunk_2 != "":
                        leifbot_embed.add_field(name="\u200B", value=f"{sorted_list_chunk_2}")
                    if sorted_list_chunk_3 != "":
                        leifbot_embed.add_field(name="\u200B", value=f"{sorted_list_chunk_3}")
                    leifbot_embed.add_field(name="\u200B", value=f"Updated **{sorted_list_len}** entries", inline=False)
                    await leifbot_channel.send(embed=leifbot_embed)
                    await asyncio.sleep(0.3)

                if removed_members != "":
                    leifbot_embed = discord.Embed(title=f"Members removed from database entry:\n{mission_type}**{mission_date_time}**\n{mission_state}", description=f"{removed_members}", color=0x303136)
                    await leifbot_channel.send(embed=leifbot_embed) 
                    await asyncio.sleep(0.3)
        print("Checked through member roles in database entries")

        self.u_mission = UpdateMission(self.bot)
        for mission_date_time, value in self.mission.items():
            for mission_type in value.values():
                if mission_type == "deltagerliste":
                    mission_type = "Deltagerliste"

                if mission_type in ["Torsdags Mission", "Deltagerliste"]:
                    await self.u_mission.UpdateMissionEmbed(guild, mission_date_time, mission_type, False)          # Update embed with data from json
                if mission_type in ["Hygge Mission", "Special Events"]:
                    await self.u_mission.UpdateHyggeSpecialEmbed(guild, mission_date_time, mission_type, False)     # Update embed with data from json

        leifbot_embed = discord.Embed(title="Data update **COMPLETE**", color=0x303136)
        await leifbot_channel.send(embed=leifbot_embed) 
        print("Data entries update complete")        


    async def CheckMember(self, check_type, guild, leifbot_channel, member, mission_date_time, mission_type, mission_state, attending_values, absent_values, deltagerliste_values):
        self.g_emoji = GuildEmojis(guild)
        self.g_usergroup = GuildUserGroup(self.bot)
        medlem_role = discord.utils.get(guild.roles, name="Medlem")
        prøve_role = discord.utils.get(guild.roles, name="Prøve Medlem")
        orlov_role = discord.utils.get(guild.roles, name="Orlov")
        member_id = str(member.id)
        member_nick = member.nick 
        if member_nick == None:
            member_nick = member.name

        if check_type == "CheckMemberInList":
            if (member_id not in attending_values and member_id not in absent_values and member_id not in deltagerliste_values):
                if (medlem_role in member.roles or prøve_role in member.roles):
                    can_continue = True
                else:
                    return
            else:
                return 

        elif check_type == "CheckMemberGroupRole":
            self.load_data()
            if member_id in self.mission[mission_date_time][mission_state]:
                del self.mission[mission_date_time][mission_state][member_id]
                fh.save_file(self.mission, 'mission')
                if (medlem_role in member.roles or prøve_role in member.roles):
                    can_continue = True
                else:
                    return                
            else:
                return 

        else:
            return
            
        if can_continue == True:
            self.load_data()
            member_group = await self.g_usergroup.checkgroup(guild, member)

            for group_name, group_emoji in self.g_emoji.guild_groups.items():
                key_group = discord.utils.get(guild.roles, name = group_name)
                if prøve_role in member.roles:
                    self.mission[mission_date_time][mission_state][member_id] = {}
                    self.mission[mission_date_time][mission_state][member_id]['user_name'] = member_nick 
                    self.mission[mission_date_time][mission_state][member_id]['group'] = "Prøve Medlem"
                    self.mission[mission_date_time][mission_state][member_id]['emoji_member_id'] = f"{self.g_emoji.guild_groups['Prøve Medlem']} <@{member_id}>"                    
                    continue             
                if orlov_role in member.roles:
                    self.mission[mission_date_time][mission_state][member_id] = {}
                    self.mission[mission_date_time][mission_state][member_id]['user_name'] = member_nick 
                    self.mission[mission_date_time][mission_state][member_id]['group'] = "Orlov"
                    self.mission[mission_date_time][mission_state][member_id]['emoji_member_id'] = f":palm_tree: <@{member_id}>"
                    continue 
                if member_group == "Gruppeløs":
                    self.mission[mission_date_time][mission_state][member_id] = {}
                    self.mission[mission_date_time][mission_state][member_id]['user_name'] = member_nick 
                    self.mission[mission_date_time][mission_state][member_id]['group'] = "Gruppeløs"
                    self.mission[mission_date_time][mission_state][member_id]['emoji_member_id'] = f":grey_question: <@{member_id}>"
                    continue

                if medlem_role in member.roles and key_group in member.roles:
                    for role_name, role_emoji in self.g_emoji.guild_roles.items():
                        if mission_type == "Torsdags Mission" or mission_state == "deltagerliste":
                            key_role = discord.utils.get(guild.roles, name = role_name)
                            if key_role in member.roles:
                                self.mission[mission_date_time][mission_state][member_id] = {}
                                self.mission[mission_date_time][mission_state][member_id]['user_name'] = member_nick 
                                self.mission[mission_date_time][mission_state][member_id]['group'] = group_name
                                self.mission[mission_date_time][mission_state][member_id]['role'] = role_name
                                self.mission[mission_date_time][mission_state][member_id]['emoji_member_id'] = f"{role_emoji} <@{member_id}>"
                                break   
                    else:
                        self.mission[mission_date_time][mission_state][member_id] = {}
                        self.mission[mission_date_time][mission_state][member_id]['user_name'] = member_nick 
                        self.mission[mission_date_time][mission_state][member_id]['group'] = group_name
                        self.mission[mission_date_time][mission_state][member_id]['emoji_member_id'] = f"{group_emoji} <@{member_id}>"
                        continue
            fh.save_file(self.mission, 'mission')
            await asyncio.sleep(0.2)

            # if check_type == "CheckMemberInList":
            #     leifbot_embed = discord.Embed(title="Member added to database", description=f"<@{int(member_id)}> - Entry added to 'deltagerliste' ", color=0x303136)
            #     await leifbot_channel.send(embed=leifbot_embed) 
            #     await asyncio.sleep(0.3)
            # if check_type == "CheckMemberGroupRole":
            #     leifbot_embed = discord.Embed(title="Updated member entry", description=f"<@{int(member_id)}> - Entry updated in '{mission_state}' ", color=0x303136)
            #     await leifbot_channel.send(embed=leifbot_embed)
            #     await asyncio.sleep(0.3)

            if check_type == "CheckMemberInList":
                return_value = f"<@{int(member_id)}> \n"
            elif check_type == "CheckMemberGroupRole":
                return_value = {member_nick: f"<@{int(member_id)}>\n,"}
                
            # print(return_value)
            return return_value

def setup(bot):
    bot.add_cog(DataUpdate(bot))
