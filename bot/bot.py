import discord
import time 

from discord.ext import commands
from pathlib import Path
from datetime import datetime 

rdfID = 475743507726991361      # guild id for RDF discord
now = datetime.now()

class DiscordLeif(commands.Bot):
    def __init__(self):
        self._cogs = [p.stem for p in Path(".").glob("./bot/cogs/*.py")]
        super().__init__(
            command_prefix=self.prefix, 
            case_insensitive=True, 
            intents=discord.Intents.all()
        )

    def setup(self):
        print("Running setup...")

        for cog in self._cogs:
            self.load_extension(f"bot.cogs.{cog}")
            print(f"Loaded '{cog} cog.")

        print("Setup complete.")

    def run(self):
        self.setup()

        with open("token/token.0", "r", encoding="utf-8") as f:
            TOKEN = f.read()

        print("Running bot...")
        super().run(TOKEN, reconnect=True)

    async def shutdown(self):
        print("Closing connection to Discord")
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

    async def on_ready(self):
        self.client_id = (await self.application_info()).id
        print("Bot ready.")
        guild = self.get_guild(rdfID)
        registeredTime = now.strftime("%A  %d-%m-%Y  %H:%M:%S")     # the time at which the bot started
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

    async def prefix(self, bot, msg):
        return commands.when_mentioned_or("+")(bot, msg)

    async def process_commands(self, msg):
        ctx = await self.get_context(msg, cls=commands.Context)

        if ctx.command is not None:
            await self.invoke(ctx)

    async def on_message(self, msg):
        if not msg.author.bot:
            await self.process_commands(msg)
