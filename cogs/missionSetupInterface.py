import discord
import json 
import asyncio 
import datetime 
import sys 

from discord.ext import commands 
from discord.utils import get 
from lib import FileHandler # pylint: disable=no-name-in-module

fh = FileHandler()


class MissionSetupInterface(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 

    def load_data(self):
        self.id = fh.load_file('id')
        self.mission = fh.load_file('mission')

    def validate_date(self, date_text):
        try:
            datetime.datetime.strptime(date_text, '%Y-%m-%d')
        except ValueError as e:
            raise e

    def validate_time(self, time_text):
        try:
            datetime.datetime.strptime(time_text, '%H:%M')
        except ValueError as e:
            raise e


# USER COMMAND - MISSION SETUP
    @commands.command(name="missionsetup")
    async def missionsetup_command(self, ctx):
        guild = ctx.message.guild
        member = guild.get_member(ctx.author.id)
        udvikler_role = discord.utils.get(guild.roles, name='Udvikler')

        if udvikler_role in member.roles:
            self.load_data()
            ny_mission_channel = self.bot.get_channel(self.id["RDF"]["ny_mission_channel_id"])
            if ny_mission_channel == ctx.channel:
                await ny_mission_channel.purge(limit = 50)
                await self.NewMissionMessage(ny_mission_channel)
        else:
            await ny_mission_channel.send("This command requires 'Udvikler' role.")


# NEW MISSION MESSAGE
    async def NewMissionMessage(self, ny_mission_channel):
        self.load_data()

        new_mission_embed = discord.Embed(title="Opsæt nye missioner her!",color=0x303136)
        new_mission_embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/729712343923294301/730044952687542273/RDF3.png")
        new_mission_embed.add_field(name="\u200B", value="**React til denne besked med den type mission du vil opsætte**", inline=False)
        new_mission_embed.add_field(name="\u200B", value=":date: Torsdags Mission\n" +
                        ":beers: Hygge Mission\n:globe_with_meridians: Special Events")        
        new_mission_embed_message = await ny_mission_channel.send(embed = new_mission_embed)
        new_mission_embed_message_id = new_mission_embed_message.id 

        await new_mission_embed_message.add_reaction(emoji='\U0001F4C5')   # calender emoji       
        await new_mission_embed_message.add_reaction(emoji='\U0001F37B')   # beers emoji
        await new_mission_embed_message.add_reaction(emoji='\U0001F310')   # globe emoji

        self.id["RDF"]["ny_mission_message_id"] = new_mission_embed_message_id
        fh.save_file(self.id, "id")


# REACTION ADDED TO NEW MISSION MESSAGE
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        self.load_data()
        bot_id = self.id['RDF']['discord_bot_id']
        if payload.user_id == bot_id:
            return  # bot reacted

        member_reaction_message_id = payload.message_id 
        new_mission_embed_message_id = self.id["RDF"]["ny_mission_message_id"]

        if member_reaction_message_id == new_mission_embed_message_id:
            guild = self.bot.get_guild(payload.guild_id)
            ny_mission_channel = self.bot.get_channel(self.id["RDF"]["ny_mission_channel_id"])
            reaction = payload.emoji.name 

            if reaction == '\U0001F4C5':    # date emoji
                mission_type = "Torsdags Mission"
            if reaction == '\U0001F37B':    # beers emoji
                mission_type = "Hygge Mission"
            if reaction == '\U0001F310':    # globe emoji
                mission_type = "Special Events"
            if reaction not in ['\U0001F4C5', '\U0001F37B', '\U0001F310']:
                return
            await ny_mission_channel.purge(limit = 50)

            # Choose date embed
            date_bot_embed = discord.Embed(title=f"Du har valgt at opsætte en **{mission_type}**",color=0x303136)
            date_bot_embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/729712343923294301/730044952687542273/RDF3.png")
            date_bot_embed.add_field(name="\u200B", value="**Hvilken dato skal missionen afholdes på?**\nSkriv i denne kanal\n*ex: 2020-01-31*", inline=False)
            date_bot_embed.add_field(name="\u200B", value=":octagonal_sign: = cancel")
            date_bot_embed_message = await ny_mission_channel.send(embed=date_bot_embed)
            await date_bot_embed_message.add_reaction(emoji='\U0001F6D1')     # Add cancel reaction to message
            await asyncio.sleep(1) # Wait for bot to update                

            msg = await self.bot.wait_for('message', check=lambda message: message.author == message.author and message.channel == ny_mission_channel)
            mission_date = msg.content
            await ny_mission_channel.purge(limit=5)

            if mission_date == "cancel":
                await self.NewMissionMessage(ny_mission_channel)
                return 

            try:            # Check if response is correct date format
                self.validate_date(mission_date)
                if self.validate_date(mission_date) == None:
                    mission_date = mission_date
            except ValueError:
                await ny_mission_channel.send("Du har valgt en forkert dato format! Dato format skal være **YYYY-MM-DD**\nPrøv igen!")
                await asyncio.sleep(5)
                await self.NewMissionMessage(ny_mission_channel)
                return                       


            # Choose time embed
            time_bot_embed = discord.Embed(title=f"Den valgte dato for **{mission_type}** er **{mission_date}**",color=0x303136)
            time_bot_embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/729712343923294301/730044952687542273/RDF3.png")
            time_bot_embed.add_field(name="\u200B", value="**Hvilket tidspunkt på dagen skal missionen afholdes?**\nSkriv i denne kanal\n*ex: 19:00*", inline=False)
            time_bot_embed.add_field(name="\u200B", value=":octagonal_sign: = cancel")
            time_bot_embed_message = await ny_mission_channel.send(embed=time_bot_embed)
            await time_bot_embed_message.add_reaction(emoji='\U0001F6D1')     # Add cancel reaction to message
            await asyncio.sleep(1) # Wait for bot to update

            msg = await self.bot.wait_for('message', check=lambda message: message.author == message.author and message.channel == ny_mission_channel)
            mission_time = msg.content
            await ny_mission_channel.purge(limit=5)

            if mission_time == "cancel":
                await self.NewMissionMessage(ny_mission_channel)
                return

            try:        # Check if resonse is correct time format
                self.validate_time(mission_time)
                if self.validate_time(mission_time) == None:
                    mission_time = mission_time
            except ValueError:
                await ny_mission_channel.send("Du har valgt en forkert tid format! Tid format skal være **HH:MM**\nPrøv igen!")
                await asyncio.sleep(5)
                await self.NewMissionMessage(ny_mission_channel)
                return


            # Specify date-time name for saving data
            mission_date_time = f"{mission_date} {mission_time}:00"

            # Check if date_time is already registered in json
            if mission_date == self.mission[mission_date_time]['date']:
                if mission_time == self.mission[mission_date_time]['time']:
                    await ny_mission_channel("Du har valgt en dato og tid der allerede er registreret!\nPrøv igen, med en anden dato/tid!")
                    await asyncio.sleep(5)
                    await self.NewMissionMessage(ny_mission_channel)
                    return 

            # TORSDAGS MISSION 
            if mission_type == "Torsdags Mission":
                await self.NewTorsdagsMission(guild, mission_date_time, mission_date, mission_time)     # make new "Torsdags Mission"
                await ny_mission_channel.purge(limit = 5)
                setup_complete_bot_embed = discord.Embed(title="**Torsdags Mission** opsætning færdig!",color=0x303136)
                setup_complete_bot_embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/729712343923294301/730044952687542273/RDF3.png")
                setup_complete_bot_embed.add_field(name="**Dato**", value=f"*{mission_date}*", inline=False)
                setup_complete_bot_embed.add_field(name="**Tidspunkt**", value=f"*{mission_time}*")
                await ny_mission_channel.send(embed=setup_complete_bot_embed)
                await asyncio.sleep(6)      # Wait before deletion of embed
                await self.NewMissionMessage(ny_mission_channel)
                return

            # HYGGE MISSION / SPECIAL EVENTS
            if mission_type != "Torsdags Mission":
                # Choose title
                title_bot_embed = discord.Embed(title=f"Den valgte tid for **{mission_type}** er **{mission_time}**",color=0x303136)
                title_bot_embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/729712343923294301/730044952687542273/RDF3.png")
                title_bot_embed.add_field(name="\u200B", value="**Hvad skal missionens titel være?**\nSkriv i denne kanal\n*ex: A. Will's Hygge Mission*", inline=False)
                title_bot_embed.add_field(name="\u200B", value=":octagonal_sign: = cancel")
                title_bot_embed_message = await ny_mission_channel.send(embed=title_bot_embed)
                await title_bot_embed_message.add_reaction(emoji='\U0001F6D1')     # Add cancel reaction to message
                await asyncio.sleep(1) # Wait for bot to update

                msg = await self.bot.wait_for('message', check=lambda message: message.author == message.author and message.channel == ny_mission_channel)
                mission_title = msg.content
                await ny_mission_channel.purge(limit=5)                

                if mission_title == "cancel":
                    await self.NewMissionMessage(ny_mission_channel)
                    return

                # Choose description
                description_bot_embed = discord.Embed(title=f"Den valgte titel for **{mission_type}** er\n**{mission_title}**",color=0x303136)
                description_bot_embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/729712343923294301/730044952687542273/RDF3.png")
                description_bot_embed.add_field(name="\u200B", value="**Hvad skal missionens beskrivelse være?**\nSkriv i denne kanal\n*ex: (map, breifing, loadout, ai, opgave, info, modset, dlc, osv...)*\n\nMax 1020 characters", inline=False)
                description_bot_embed.add_field(name="\u200B", value=":octagonal_sign: = cancel")
                description_bot_embed_message = await ny_mission_channel.send(embed=description_bot_embed)
                await description_bot_embed_message.add_reaction(emoji='\U0001F6D1')     # Add cancel reaction to message
                await asyncio.sleep(1) # Wait for bot to update

                msg = await self.bot.wait_for('message', check=lambda message: message.author == message.author and message.channel == ny_mission_channel)
                mission_description = msg.content
                await ny_mission_channel.purge(limit=5)                

                if mission_description == "cancel":
                    await self.NewMissionMessage(ny_mission_channel)
                    return

                mission_description_character_length = len(mission_description)     # message too big for discord embeds
                if mission_description_character_length > 1020:
                    await ny_mission_channel.send(mission_description)
                    await ny_mission_channel.send("Din beskrivelse er større end 1020 characters og kan ikke sendes i en discord embed.\nDin beskrivelse er kopieret ovenover, kort den ned og prøv igen.")
                    await asyncio.sleep(6)
                    await self.NewMissionMessage(ny_mission_channel)

                # HYGGE MISSION / SPECIAL EVENTS
                await self.NewHyggeSpecialMission(guild, mission_date_time, mission_date, mission_time, mission_type, mission_title, mission_description)
                await ny_mission_channel.purge(limit=5)
                setup_complete_bot_embed = discord.Embed(title=f"**{mission_type}** opsætning færdig!",color=0x303136)
                setup_complete_bot_embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/729712343923294301/730044952687542273/RDF3.png")
                setup_complete_bot_embed.add_field(name="**Dato**", value=f"*{mission_date}*", inline=False)
                setup_complete_bot_embed.add_field(name="**Tidspunkt**", value=f"*{mission_time}*", inline=False)
                setup_complete_bot_embed.add_field(name="**Titel**", value=f"*{mission_title}*", inline=False)
                setup_complete_bot_embed.add_field(name="**Beskrivelse**", value=f"*{mission_description}*", inline=False)
                await ny_mission_channel.send(embed=setup_complete_bot_embed)
                await asyncio.sleep(6)      # Wait before deletion of embed
                await self.NewMissionMessage(ny_mission_channel)
                return


# NEW "TORSDAGS" MISSION
    async def NewTorsdagsMission(self, guild, mission_date_time, mission_date, mission_time):
        pass


# NEW "HYGGE / SPECIAL" MISSION
    async def NewHyggeSpecialMission(self, guild, mission_date_time, mission_date, mission_time, mission_type, mission_title, mission_description):
        pass


def setup(bot):
    bot.add_cog(MissionSetupInterface(bot))
