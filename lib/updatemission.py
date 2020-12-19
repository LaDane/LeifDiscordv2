import discord
import json 

from discord.utils import get 
from lib import FileHandler, GuildEmojis, ListRoles

fh = FileHandler()

class UpdateMission:
    def __init__(self, bot):
        self.bot = bot 

    def load_data(self):
        self.id = fh.load_file('id')
        self.mission = fh.load_file('mission')

# UPDATE "TORSDAGS MISSION" / "DELTAGERLISTE" embed
    async def UpdateMissionEmbed(self, guild, mission_date_time, expected_update, ended):
        self.load_data()
        self.g_emoji = GuildEmojis(guild)
        self.listroles = ListRoles(self.bot)
        if expected_update not in ["Torsdags Mission", "Deltagerliste"]:
            return
        if expected_update == "Torsdags Mission":
            channel = discord.utils.get(guild.text_channels, name = "torsdags-mission")
            original_embed_msg = await channel.fetch_message(self.mission[mission_date_time]['torsdags_mission_embed_msg_id'])
            absent_members = await self.listroles.list_emoji_member_id_json(mission_date_time, "absent", "None", expected_update)           # absent members
            absent_members_amount = len(absent_members.split())
            absent_members_amount //= 2
            state = "attending"

            if ended == True:
                await original_embed_msg.delete()
                channel = discord.utils.get(guild.text_channels, name = "deltagerliste")
                original_embed_msg = await channel.fetch_message(self.mission[mission_date_time]['deltagerliste_reserved_embed_msg_id'])
                            
        if expected_update == "Deltagerliste":
            channel = discord.utils.get(guild.text_channels, name = "deltagerliste")
            original_embed_msg = await channel.fetch_message(self.mission[mission_date_time]['deltagerliste_not_responded_embed_msg_id'])
            orlov_members = await self.listroles.list_emoji_member_id_json(mission_date_time, "deltagerliste", "Orlov", expected_update)    # orlov members
            orlov_members_amount = len(orlov_members.split())
            orlov_members_amount //= 2
            state = "deltagerliste"

        group_members = {}                                                                                                                  # members in groups
        group_members_amount = {}        
        for group in self.g_emoji.guild_groups.keys():
            group_members[group] = await self.listroles.list_emoji_member_id_json(mission_date_time, state, group, expected_update)
            group_members_amount[group] = len(group_members[group].split())
            group_members_amount[group] //= 2

        groupless_members = await self.listroles.list_emoji_member_id_json(mission_date_time, state, "Gruppeløs", expected_update)          # groupless members
        groupless_members_amount = len(groupless_members.split())
        groupless_members_amount //= 2 

        total_members = 0
        for member_amount in group_members_amount.values():
            total_members += member_amount
        total_members += groupless_members_amount

        if expected_update == "Torsdags Mission":
            if ended == False:
                embed = discord.Embed(title="Torsdags Mission", description=f"Tilladte mods: **RDF's Torsdags Mission** + **RDF QoL mods**",color=0x00ff00)
            if ended == True:
                embed = discord.Embed(title="Torsdags Mission - __**Afsluttet**__",color=0xf70000)
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/729712343923294301/730044952687542273/RDF3.png")

        if expected_update == "Deltagerliste":
            embed = discord.Embed(title="Torsdags Mission - Mangler deltagelse status",color=0x000000)
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/730077877546123289/731108594963185764/Mangler_at_svare.png")
            total_members += orlov_members_amount       # need to remember orlov amount

        embed.add_field(name="\u200B", value=f"{self.g_emoji.guild_formatting['People']} **{total_members}**")
        embed.add_field(name="\u200B", value=f"{self.g_emoji.guild_formatting['Date']} **{self.mission[mission_date_time]['date']}**")
        embed.add_field(name="\u200B", value=f"{self.g_emoji.guild_formatting['Time']} **{self.mission[mission_date_time]['time']}**")
        for group, emoji in self.g_emoji.guild_groups.items():
            embed.add_field(name="\u200B", value=f"{emoji} **{group} ({group_members_amount[group]})**\n{group_members[group]}")
        embed.add_field(name="\u200B", value=f":grey_question: **Gruppeløs ({groupless_members_amount})**\n{groupless_members}")

        if expected_update == "Torsdags Mission":
            embed.add_field(name="\u200B", value=f":x: **Fraværende ({absent_members_amount})**\n{absent_members}")
        if expected_update == "Deltagerliste":
            embed.add_field(name="\u200B", value=f":palm_tree: **Orlov ({orlov_members_amount})**\n{orlov_members}")

        await original_embed_msg.edit(embed=embed)

        if ended == True:
            del self.mission[mission_date_time]
            fh.save_file(self.mission, 'mission')


# UPDATE "HYGGE MISSION" / "SPECIAL EVENTS" embed
    async def UpdateHyggeSpecialEmbed(self, guild, mission_date_time, mission_type, ended):
        self.load_data()
        self.g_emoji = GuildEmojis(guild)
        self.listroles = ListRoles(self.bot)
        if mission_type not in ["Hygge Mission", "Special Events"]:
            return 
        if mission_type == "Hygge Mission":
            channel = discord.utils.get(guild.text_channels, name="hygge-mission")
        if mission_type == "Special Events":
            channel = discord.utils.get(guild.text_channels, name="special-events")
        original_embed_msg = await channel.fetch_message(self.mission[mission_date_time]['mission_msg_id'])

        if ended == True:
            await original_embed_msg.delete()
            channel = discord.utils.get(guild.text_channels, name="deltagerliste")
            original_embed_msg = await channel.fetch_message(self.mission[mission_date_time]['deltagerliste_reserved_embed_msg_id'])
        
        attending_users_chunk = await self.listroles.list_emoji_member_id_json(mission_date_time, "attending", "None", mission_type)
        attending_users_amount = attending_users_chunk[1]
        attending_users_chunk_1 = ''.join(list(attending_users_chunk[0][2]))
        if attending_users_chunk_1 == '':
            attending_users_chunk_1 = '\u200B'
        attending_users_chunk_2 = ''.join(list(attending_users_chunk[0][1]))
        if attending_users_chunk_2 == '':
            attending_users_chunk_2 = '\u200B'
        attending_users_chunk_3 = ''.join(list(attending_users_chunk[0][0]))
        if attending_users_chunk_3 == '':
            attending_users_chunk_3 = '\u200B'

        absent_users_chunk = await self.listroles.list_emoji_member_id_json(mission_date_time, "absent", "None", mission_type)
        absent_users_amount = absent_users_chunk[1]
        absent_users_chunk_1 = ''.join(list(absent_users_chunk[0][2]))
        if absent_users_chunk_1 == '':
            absent_users_chunk_1 = '\u200B'
        absent_users_chunk_2 = ''.join(list(absent_users_chunk[0][1]))
        if absent_users_chunk_2 == '':
            absent_users_chunk_2 = '\u200B'
        absent_users_chunk_3 = ''.join(list(absent_users_chunk[0][0]))
        if absent_users_chunk_3 == '':
            absent_users_chunk_3 = '\u200B'

        if mission_type == "Hygge Mission":
            hygge_special_embed = discord.Embed(title=f"{self.mission[mission_date_time]['title']}", description=f"{self.mission[mission_date_time]['description']}",color=0xfcbe03)
            hygge_special_embed.set_thumbnail(url="https://media.discordapp.net/attachments/730077877546123289/737652999090077796/beers.png")
        if mission_type == "Special Events":
            hygge_special_embed = discord.Embed(title=f"{self.mission[mission_date_time]['title']}", description=f"{self.mission[mission_date_time]['description']}",color=0x0390fc)
            hygge_special_embed.set_thumbnail(url="https://media.discordapp.net/attachments/730077877546123289/737674475168071680/special__events_blue_brighter.png")
        hygge_special_embed.add_field(name="\u200B", value=f"{self.g_emoji.guild_formatting['Date']} **{self.mission[mission_date_time]['date']}**")
        hygge_special_embed.add_field(name="\u200B", value=f"{self.g_emoji.guild_formatting['Time']} **{self.mission[mission_date_time]['time']}**")
        hygge_special_embed.add_field(name="\u200B", value=f":white_check_mark: **Deltagende ({attending_users_amount})**", inline=False)
        hygge_special_embed.add_field(name="\u200B", value=f"{attending_users_chunk_1}", inline=True)
        hygge_special_embed.add_field(name="\u200B", value=f"{attending_users_chunk_2}", inline=True)
        hygge_special_embed.add_field(name="\u200B", value=f"{attending_users_chunk_3}", inline=True)
        hygge_special_embed.add_field(name="\u200B", value=f":x: **Fraværende ({absent_users_amount})**", inline=False)
        hygge_special_embed.add_field(name="\u200B", value=f"{absent_users_chunk_1}", inline=True)
        hygge_special_embed.add_field(name="\u200B", value=f"{absent_users_chunk_2}", inline=True)
        hygge_special_embed.add_field(name="\u200B", value=f"{absent_users_chunk_3}", inline=True) 

        await original_embed_msg.edit(embed=hygge_special_embed)

        if ended == True:
            special_needs_role = discord.utils.get(guild.roles, name="Special-Needs") 
            for date_time, value in self.mission.items():
                if date_time == mission_date_time and value['type'] == "Special Events":
                    for userID_str in value['attending'].keys():
                        userID = int(userID_str)
                        special_needs_member = guild.get_member(userID)
                        await special_needs_member.remove_roles(special_needs_role)
            del self.mission[mission_date_time]
            fh.save_file(self.mission, 'mission')
