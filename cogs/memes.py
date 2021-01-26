import discord 

from discord.ext import commands 
from discord.utils import get 


class Memes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 


    @commands.command(name="memes")
    async def memes_command(self, ctx):
        guild = ctx.message.guild 
        medlem_role = discord.utils.get(guild.roles, name = 'Medlem')
        memer_role = discord.utils.get(guild.roles, name = 'memer')
        orlov_role = discord.utils.get(guild.roles, name = 'Orlov')
        user = ctx.message.author

        if medlem_role not in user.roles:
            await ctx.send("Du skal være medlem før du kan få adgang til Memes kanalen.")
            return

        if medlem_role in user.roles:
            if memer_role in user.roles:
                await user.send("Du er ikke længere en del af memes kanalen og dit tag er fjernet")
                await user.remove_roles(memer_role)
                return
            
            if orlov_role in user.roles:
                horvy_emoji = get(guild.emojis, name='horvy')
                await ctx.send(f"Du kan ikke være på orlov og have adgang til Memes kanalen på samme tid {horvy_emoji}")
                return 

            if memer_role not in user.roles and orlov_role not in user.roles:
                memes_channel = discord.utils.get(guild.text_channels, name="memes-migmigs")
                await memes_channel.send(f"@{user.id} har nu adgang til Memes!")
                await user.add_roles(memer_role)



def setup(bot):
    bot.add_cog(Memes(bot))