import discord
import time 
import asyncio 

from discord.ext import commands
from pathlib import Path
from datetime import datetime 

rdfID = 475743507726991361                  # guild id for RDF discord
leifBotChannelID = 788995949660995585       # channel id for leifbot channel on RDF discord
now = datetime.now()

class DiscordLeif(commands.Bot):
    def __init__(self):
        self._cogs = [p.stem for p in Path(".").glob("./cogs/*.py")]
        super().__init__(
            command_prefix=self.prefix, 
            case_insensitive=True, 
            intents=discord.Intents.all()
        )

    def setup(self):
        print("Running setup...")

        for cog in self._cogs:
            self.load_extension(f"cogs.{cog}")
            print(f"Loaded '{cog}' cog.")

        print("Setup complete.")

    def run(self):
        self.setup()

        with open("token/token.0", "r", encoding="utf-8") as f:
            TOKEN = f.read()

        print("Running bot...")
        super().run(TOKEN, reconnect=True)

    async def shutdown(self):
        print("Closing connection to Discord")
        
        starting = False
        await self.StartStopMessage(starting)

        await super().close()

    async def close(self):
        print("Closing on keyboard interrupt...")
        await self.shutdown()

    async def on_connect(self):
        print(f"Connected to Discord (latency: {self.latency*1000:,.0f} ms).")

    async def on_resumed(self):
        print("Bot resumed.")

    async def on_disconnect(self):
        print("Bot disconnected.")

    # async def on_error(self, err, *args, **kwargs):
    #     try:
    #         raise Exception()
    #     except Exception as e:
    #         raise e

    # async def on_command_error(self, ctx, exc):
    #     raise getattr(exc, "original", exc)

    async def on_ready(self):
        self.client_id = (await self.application_info()).id
        guild = self.get_guild(rdfID)
        registeredTime = now.strftime("%A  %d-%m-%Y  %H:%M:%S")     # the time at which the bot started
        print("Bot ready.")
        print("=================================================================================")
        print("")
        print("  _____ _____  _____  _____ ____  _____  _____      _      ______ _____ ______ ")
        print(" |  __ \_   _|/ ____|/ ____/ __ \|  __ \|  __ \    | |    |  ____|_   _|  ____|")
        print(" | |  | || | | (___ | |   | |  | | |__) | |  | |   | |    | |__    | | | |__   ")
        print(" | |  | || |  \___ \| |   | |  | |  _  /| |  | |   | |    |  __|   | | |  __| ")
        print(" | |__| || |_ ____) | |___| |__| | | \ \| |__| |   | |____| |____ _| |_| |     ")   
        print(" |_____/_____|_____/ \_____\____/|_|  \_\_____/    |______|______|_____|_|     ")   
        print("")   
        print("=================================================================================")
        print(f"Bot started at:            {registeredTime}")
        print(f"Bot logged in as:          {self.user.name}")
        print(f"Bot running on server:     {guild}")        
        print("=================================================================================")
        print("")

        starting = True
        await self.StartStopMessage(starting)

    async def prefix(self, bot, msg):
        return commands.when_mentioned_or("+")(bot, msg)

    async def process_commands(self, msg):
        ctx = await self.get_context(msg, cls=commands.Context)

        if ctx.command is not None:
            await self.invoke(ctx)

    async def on_message(self, msg):
        if not msg.author.bot:
            await self.process_commands(msg)


    async def StartStopMessage(self, starting):
        rdf_guild = self.get_guild(rdfID)
        leifbot_channel = rdf_guild.get_channel(leifBotChannelID)
        
        if starting == True:
            registeredTime = now.strftime("%A  %d-%m-%Y  %H:%M:%S")     # the time at which the bot started

            start_embed = discord.Embed(description = f"Discord Leif started at:\n\n**{registeredTime}**", color=0x303136)
            start_embed.set_image(url="https://media.discordapp.net/attachments/747967053050151014/789031811661561866/unknown.png")
            start_embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/729712343923294301/730044952687542273/RDF3.png")
            await leifbot_channel.send(embed = start_embed)

        if starting == False:
            current_time = datetime.now()
            registeredTime = current_time.strftime("%A  %d-%m-%Y  %H:%M:%S")     # the time at which the bot started
            await leifbot_channel.send(f"Leif died at **{registeredTime}**")

