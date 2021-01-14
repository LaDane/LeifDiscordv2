import discord 

from discord.utils import get 


class GuildEmojis:
    def __init__(self, guild):
        # self.guild = {'Kompagni-Stab' : self.kompagni_emoji(guild), '1. Del-Stab' : self.del_emoji(guild), '2. Del-Stab' : self.to_del_emoji(guild),
        #              '1-1' : self.en_en_emoji(guild), '1-2' : self.en_to_emoji(guild), '1-3' : self.en_tre_emoji(guild),
        #              '2-1' : self.to_en_emoji(guild), '2-2' : self.to_to_emoji(guild), '2-3' : self.to_tre_emoji(guild),
        #              'Lima' : self.lima_emoji(guild), 'Logi' : self.logi_emoji(guild), 'Zeus' : self.zeus_emoji(guild),
        #              'Prøve Medlem' : self.prve_emoji(guild),
        #              'People' : self.people_emoji(guild), 'Date' : self.mission_date(guild),
        #              'Time' : self.mission_time(guild), 'DF' : self.df_emoji(guild),
        #              'ADMBM' : self.admbm_emoji(guild), 'SIGMD' : self.sigmd_emoji(guild),
        #              'DELSYHJ' : self.delsyhj_emoji(guild), 'LMG2' : self.lmg2_emoji(guild),
        #              'GV4' : self.gv4_emoji(guild), 'GV2' : self.gv2_emoji(guild),
        #              'GF' : self.gf_emoji(guild), 'NK' : self.nk_emoji(guild),
        #              'SYHJ' : self.syhj_emoji(guild), 'GV5' : self.gv5_emoji(guild),
        #              'LMG1' : self.lmg1_emoji(guild),
        #              }

        self.guild_groups = {'Kompagni-Stab' : self.kompagni_emoji(guild), '1. Del-Stab' : self.del_emoji(guild), '2. Del-Stab' : self.to_del_emoji(guild),
                     '1-1' : self.en_en_emoji(guild), '1-2' : self.en_to_emoji(guild), '1-3' : self.en_tre_emoji(guild),
                     '2-1' : self.to_en_emoji(guild), '2-2' : self.to_to_emoji(guild), '2-3' : self.to_tre_emoji(guild),
                     'Lima' : self.lima_emoji(guild), 'Logi' : self.logi_emoji(guild), 'Zeus' : self.zeus_emoji(guild),
                     'Prøve Medlem' : self.prve_emoji(guild)
                     }

        self.guild_formatting = {'People' : self.people_emoji(guild), 'Date' : self.mission_date(guild),
                     'Time' : self.mission_time(guild)
                     }

        self.guild_roles = {'DF' : self.df_emoji(guild), 'KC' : self.kc_emoji(guild),
                     'ADMBM' : self.admbm_emoji(guild), 'SIGMD' : self.sigmd_emoji(guild),
                     'SIKMD' : self.sikmd_emoji(guild), 'DELSYHJ' : self.delsyhj_emoji(guild), 
                     'LMG2' : self.lmg2_emoji(guild), 'GV4' : self.gv4_emoji(guild), 
                     'GV2' : self.gv2_emoji(guild), 'GF' : self.gf_emoji(guild), 
                     'NK' : self.nk_emoji(guild), 'SYHJ' : self.syhj_emoji(guild), 
                     'GV5' : self.gv5_emoji(guild), 'LMG1' : self.lmg1_emoji(guild),
                     }


# GROUPS
    def en_en_emoji(self, guild):
        return get(guild.emojis, name='11')

    def en_to_emoji(self, guild):
        return get(guild.emojis, name='12')

    def en_tre_emoji(self, guild):
        return get(guild.emojis, name='13')


    def to_en_emoji(self, guild):
        return get(guild.emojis, name='21')

    def to_to_emoji(self, guild):
        return get(guild.emojis, name='22')

    def to_tre_emoji(self, guild):
        return get(guild.emojis, name='23')


    def kompagni_emoji(self, guild):
        return get(guild.emojis, name='Kompagni')

    def del_emoji(self, guild):
        return get(guild.emojis, name='1DEL')
    
    def to_del_emoji(self, guild):
        return get(guild.emojis, name='2DEL')


    def lima_emoji(self, guild):
        return get(guild.emojis, name='LIMA')

    def logi_emoji(self, guild):
        return get(guild.emojis, name='Logi')

    def zeus_emoji(self, guild):
        return get(guild.emojis, name='ZEUS')

    def prve_emoji(self, guild):
        return get(guild.emojis, name='PRVE')


# FORMATTING
    def mission_date(self, guild):
        return get(guild.emojis, name='CALENDAR')

    def mission_time(self, guild):    
        return get(guild.emojis, name='CLOCK')

    def people_emoji(self, guild):    
        return get(guild.emojis, name='PEOPLE')     


# ROLES
    def df_emoji(self, guild):
        return get(guild.emojis, name='DF')  

    def kc_emoji(self, guild):
        return get(guild.emojis, name='KC')

    def admbm_emoji(self, guild):
        return get(guild.emojis, name='ADMBM')     

    def sigmd_emoji(self, guild):
        return get(guild.emojis, name='SIGMD')

    def sikmd_emoji(self, guild):
        return get(guild.emojis, name="SIKMD")

    def delsyhj_emoji(self, guild):
        return get(guild.emojis, name='DELSYHJ')

    def lmg2_emoji(self, guild):
        return get(guild.emojis, name='LMG2') 

    def gv4_emoji(self, guild):
        return get(guild.emojis, name='GV4')

    def gv2_emoji(self, guild):
        return get(guild.emojis, name='GV2')

    def gf_emoji(self, guild):
        return get(guild.emojis, name='GF') 

    def nk_emoji(self, guild):
        return get(guild.emojis, name='GV1')

    def syhj_emoji(self, guild):
        return get(guild.emojis, name='SYHJ')

    def gv5_emoji(self, guild):
        return get(guild.emojis, name='GV5')

    def lmg1_emoji(self, guild):
        return get(guild.emojis, name='LMG1') 



    