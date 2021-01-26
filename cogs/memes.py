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

        if medlem_role in user.roles:
            if memer_role in user.roles:
                await user.remove_roles(memer_role)
                return
            
            if orlov_role in user.roles:
                return 

            if memer_role not in user.roles and orlov_role not in user.roles:
                await user.add_roles(memer_role)

def setup(bot):
    bot.add_cog(Memes(bot))