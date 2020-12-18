import discord 

from discord.utils import get 
from discord.ext import commands 
from lib import FileHandler # pylint: disable=no-name-in-module

fh = FileHandler()

class CancelMenu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def load_data(self):
        self.id = fh.load_file('id')

# If two stopsign reactions are given on a message, bot will send "cancel" in chat

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        self.load_data()
        allowed_cancel_channels = [self.id["RDF"]["ny_mission_channel_id"], self.id["RDF"]["leifbot_channel_id"]]

        if payload.channel_id in allowed_cancel_channels:
            if payload.emoji.name == '\U0001F6D1':
                guild = self.bot.get_guild(payload.guild_id)  # You need the guild to get the member who reacted
                channel = guild.get_channel(payload.channel_id)
                message = await channel.fetch_message(payload.message_id)                      
                reaction = get(message.reactions, emoji=payload.emoji.name)
                if reaction and reaction.count > 1:
                    await channel.send("cancel")

def setup(bot):
    bot.add_cog(CancelMenu(bot))