import discord 

from discord.utils import get 


# returns a users group / role 
class GuildUserGroup:
    def __init__(self, bot):
        self.bot = bot 

    def find_group(self, guild, member, names):
        roles = []

        for name in names:      # finding all roles
            roles.append(discord.utils.get(guild.roles, name = name)) 

        for role in roles:
            if role in member.roles:
                return role.name
        return 'Gruppeløs'

    async def checkgroup(self, guild, member):
        return self.find_group(guild, member, ['Kompagni-Stab', '1. Del-Stab', '2. Del-Stab', '1-1', '1-2', '1-3', '2-1', '2-2', '2-3', 'Lima', 'Logi', 'Zeus', 'Prøve Medlem', 'Orlov', 'People', 'Date', 'Time'])

    async def checkrole(self, guild, member):
        return self.find_group(guild, member, ['DF', 'KC', 'ADMBM', 'SIGMD', 'SIKMD', 'DELSYHJ', 'LMG2', 'GV4', 'GV2', 'GF', 'NK', 'SYHJ', 'GV5', 'LMG1'])