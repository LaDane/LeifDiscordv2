import discord 

from discord.utils import get 
from lib import FileHandler, GuildEmojis # pylint: disable=no-name-in-module

fh = FileHandler()

class ListRoles:
    def __init__(self, bot):
        self.bot = bot 

    def load_data(self):
        self.mission = fh.load_file('mission')


# "TORSDAGS MISSION" - list entries by "emoji_member_id" from mission.json    
    async def list_emoji_member_id_json(self, mission_date_time, state, group, expected_update):
        self.load_data()
        print_str = ""
        for date_time, value in self.mission.items():
            if date_time == mission_date_time:
                for items in value[state].values():
                    if expected_update in ["Torsdags Mission", "Deltagerliste"]:
                        if state == 'attending' or state == 'deltagerliste':
                            for key_group, entry_group in items.items():
                                if key_group == 'group' and entry_group == group:
                                    print_str += f"{items['emoji_member_id']}\n"                    
                        if state == 'absent':
                            print_str += f"{items['emoji_member_id']}\n"
                    if expected_update in ["Hygge Mission", "Special Events"]:
                        print_str += f"{items['emoji_member_id']}\n,"
        
        if expected_update in ["Hygge Mission", "Special Events"]:
            print_str = print_str.strip(',')
            print_str_amount = len(print_str.split())
            print_str_amount //= 2
            print_str = list(print_str.split(','))
            print_str_len = len(print_str)
            print_str = list([print_str[i*print_str_len // 3: (i+1)*print_str_len // 3] for i in range(3)])
            return [print_str, print_str_amount]
        else:
            return print_str 




# # NEW "TORSDAGS MISSION" - list users and their emojis with a specified role - used when creating a new torsdags mission for "deltagerliste"
#     async def deltagerliste_list_members_with_group(self, guild, group):
#         self.g_emoji = GuildEmojis(guild)
#         group = discord.utils.get(guild.roles, name = group) 

#         print_str = ""
#         for member in guild.members:
#             if group in member.roles:
#                 for key_group, group_emoji in self.g_emoji.guild_groups.items():
#                     loop_group = discord.utils.get(guild.roles, name = key_group)
#                     if loop_group == group:
#                         member_id = member.id
#                         for key_role, role_emoji in self.g_emoji.guild_roles.items():
#                             loop_role = discord.utils.get(guild.roles, name = key_role)
#                             if loop_role in member.roles:
#                                 print_str += f"{role_emoji} <@{member_id}>\n"
#                         else:
#                             print_str += f"{group_emoji} <@{member_id}>\n"
#         return print_str 


# # NEW "TORSDAGS MISSION" - return a list of users that dont have "Grupper" from guild for "deltagerliste"
#     async def deltagerliste_list_members_groupless(self, guild):
#         self.g_emoji = GuildEmojis(guild)
#         medlem_role = discord.utils.get(guild.roles, name = "Medlem")
#         orlov_role = discord.utils.get(guild.roles, name = "Orlov")

#         print_str = ""
#         for member in guild.members:
#             if orlov_role in member.roles:      # dont add user is member har "orlov" role
#                 continue
#             if medlem_role in member.roles:
#                 for key_group in self.g_emoji.guild_groups.keys():
#                     loop_group = discord.utils.get(guild.roles, name = key_group)
#                     if loop_group in member.roles:
#                         break
#                 else:
#                     member_id = member.id 
#                     print_str += f":grey_question: <@{member_id}>\n"
#         return print_str 


# # NEW "TORSDAGS MISSION" - # return a list of users that have "Orlov" role from guild
#     async def deltagerliste_list_members_orlov(self, guild):
#         medlem_role = discord.utils.get(guild.roles, name = "Medlem")
#         orlov_role = discord.utils.get(guild.roles, name = "Orlov")

#         print_str = ""
#         for member in guild.members:
#             if medlem_role in member.roles:
#                 if orlov_role in member.roles:
#                     member_id = member.id
#                     print_str += f":palm_tree: <@{member_id}>\n"
#         return print_str 