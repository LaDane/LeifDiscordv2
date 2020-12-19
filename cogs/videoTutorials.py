import discord 
import json 

from discord.ext import commands 
from discord.utils import get 
from lib import FileHandler # pylint: disable=no-name-in-module

fh = FileHandler()


class VideoTutorials(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 

    def load_data(self):
        self.id = fh.load_file('id')
        self.vtuts = fh.load_file('vtuts')


    @commands.command(name="vtuts")
    async def vtuts_command(self, ctx):
        self.load_data()
        guild = ctx.message.guild
        video_tutorials_channel = self.bot.get_channel(self.id['RDF']['video_tutorials_channel_id'])
        udvikler_role = discord.utils.get(guild.roles, name='Udvikler')
        if ctx.channel == video_tutorials_channel and udvikler_role in ctx.message.author.roles:
            await self.SendVideoTutorialEmbed()

    # @commands.command(name="vtutseditor")
    # async def vtutseditor_command(self, ctx):
    #     self.load_data()
    #     leifbot_channel = self.bot.get_channel(self.id['RDF']['leifbot_channel_id'])
    #     if ctx.channel == leifbot_channel:
    #         await self.SendVideoTutorialsEditorEmbed()


    async def SendVideoTutorialEmbed(self):
        self.load_data()
        video_tutorials_channel = self.bot.get_channel(self.id['RDF']['video_tutorials_channel_id'])           
        await video_tutorials_channel.purge(limit = 5)
        video_tutorial_embed = discord.Embed(title="Her kan du finde tutorials lavet til RDF medlemmer",color=0x303136)
        video_tutorial_embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/729712343923294301/730044952687542273/RDF3.png")
        video_tutorial_embed.add_field(name="\u200B", value="Konstabel Håndbogen kan læses [her](https://docs.google.com/document/d/1MwWPoQ4jht26IHfqRxKo7F2UBbV_sYNWz2PXXN8LP_8/edit)", inline=False)
        for index, link in enumerate(self.vtuts['RDF']):
            video_tutorial_embed.add_field(name="\u200B", value=f"**#{index + 1} - {link}**", inline=False)
        await video_tutorials_channel.send(embed=video_tutorial_embed)


    # async def SendVideoTutorialsEditorEmbed(self):
    #     self.load_data
    #     leifbot_channel = self.bot.get_channel(self.id['RDF']['leifbot_channel_id'])
    #     tutorial_editor_menu_embed = discord.Embed(title="Ændre på databasen af video tutorials her!",color=0x303136)
    #     tutorial_editor_menu_embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/729712343923294301/730044952687542273/RDF3.png")
    #     tutorial_editor_menu_embed.add_field(name="\u200B", value="**React til denne besked med den ændring du gerne vil lave**", inline=False)
    #     tutorial_editor_menu_embed.add_field(name="\u200B", value=":star: Tilføj ny video tutorial\n" +
    #         ":balloon: Fjern en video tutorial")   
    #     tutorial_editor_menu_message = await leifbot_channel.send(embed=tutorial_editor_menu_embed)
    #     tutorial_editor_menu_message_id = tutorial_editor_menu_message.id

    #     await tutorial_editor_menu_message.add_reaction(emoji='\u2B50')         # star
    #     await tutorial_editor_menu_message.add_reaction(emoji='\U0001F388')     # balloon

    #     self.id['RDF']["video_tutorials_editor_message_id"] = tutorial_editor_menu_message_id      # Save embed message id to msgid.json
    #     fh.save_file(self.id, 'id')     



def setup(bot):
    bot.add_cog(VideoTutorials(bot))
