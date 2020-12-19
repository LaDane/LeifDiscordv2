import discord 
import time 
import asyncio

from discord.ext import commands 
from discord.utils import get 
from datetime import datetime 
from lib import FileHandler # pylint: disable=no-name-in-module

fh = FileHandler()
# now = datetime.now()
sendReminderTime = "Tuesday 12:00:01"        # Tuesday 12:00:01

class Reminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 

    def load_data(self):
        self.id = fh.load_file('id')
        self.mission = fh.load_file('mission')


    @commands.Cog.listener()
    async def on_ready(self):
        while not self.bot.is_closed():
            current = datetime.now()
            current_day_time = current.strftime("%A %H:%M:%S")
            if current_day_time == sendReminderTime:
                await self.RemindMemberSignup()
                await asyncio.sleep(1)    
            else:
                await asyncio.sleep(1)


    async def RemindMemberSignup(self):
        print("Sending reminders")
        self.load_data()
        guild = self.bot.get_guild(self.id['RDF']['guild_id'])
        medlem_role = discord.utils.get(guild.roles, name='Medlem')
        prøve_role = discord.utils.get(guild.roles, name='Prøve Medlem')
        orlov_role = discord.utils.get(guild.roles, name="Orlov")
        hyggechatten_channel = discord.utils.get(guild.text_channels, name="hyggechatten")
        udviklerchatten_channel = discord.utils.get(guild.text_channels, name="udviklerchatten")

        no_response_members = []
        orlov_members = []
        cant_msg_members = []
        blocket_bot = []

        for mission_date_time, value in self.mission.items():
            if value['type'] == "Torsdags Mission":
                for str_memberID in value['deltagerliste'].keys():
                    memberID = int(str_memberID)
                    member_name = self.mission[mission_date_time]['deltagerliste'][str_memberID]['user_name']
                    try:
                        member = guild.get_member(memberID)
                    except:
                        cant_msg_members.append(f"<@{memberID}> {member_name}\n")
                        continue

                    if member in guild.members:
                        if prøve_role in member.roles or medlem_role in member.roles:
                            if orlov_role in member.roles:
                                orlov_members.append(f"<@{memberID}>\n")
                                continue 

                            try:
                                await member.send("Du har ikke givet svar på om du kommer til **RDF's Torsdags Mission!**\nHusk at ændre din deltagelse status inde i RDF Discord kanalen under **torsdags-mission**")
                                no_response_members.append(f"<@{memberID}>\n")
                                continue 
                            except Exception:
                                blocket_bot.append(f"<@{memberID}>\n")
                                await hyggechatten_channel.send(f"Jeg kan ikke sende dig beskeder <@{memberID}>! Hvorfor vil du ikke snakke med mig? :( \nJeg ville bare minde dig om at du skal huske at signe up til vores **Torsdags Mission!**")

                    # if member_name == "A. Will":    # testing
                    #     await member.send("Hej")
                    #     return

        no_response_members_list = ''.join(no_response_members)
        orlov_members_list = ''.join(orlov_members)
        cant_msg_members_list = ''.join(cant_msg_members)
        blocket_bot_list = ''.join(blocket_bot)

        if orlov_members_list != '':
            await udviklerchatten_channel.send(f"Følgende medlemmer har **orlov** og er ikke blevet spammet af Leif\n{orlov_members_list}")
        if cant_msg_members_list != '':
            await udviklerchatten_channel.send(f"Følgende medlemmer er ikke muligt at skaffe data på, og har ikke fået en besked fra Leif\n{cant_msg_members_list}")
        if blocket_bot_list != '':
            await udviklerchatten_channel.send(f"Følgende medlemmer har blokeret botten eller slået DM's fra, så Leif har tagget dem i hyggechatten\n{blocket_bot_list}")
        if no_response_members_list != '':
            await udviklerchatten_channel.send(f"Følgende medlemmer har ikke svaret om de kommer til Torsdags Missionen, Leif har sendt en besked med en påmindelse om at de skal huske og svare\n{no_response_members_list}")

def setup(bot):
    bot.add_cog(Reminder(bot))

