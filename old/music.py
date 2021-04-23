import discord
import wavelink 
import re
import asyncio
import random 
import typing as t
import datetime as dt

from discord.ext import commands 
from enum import Enum
from lib import FileHandler # pylint: disable=no-name-in-module

fh = FileHandler()


URL_REGEX = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
OPTIONS = {
    "1️⃣": 0,
    "2⃣": 1,
    "3⃣": 2,
    "4⃣": 3,
    "5⃣": 4,
}

class AlreadyConnectedToChannel(commands.CommandError):
    pass 

class NoVoiceChannel(commands.CommandError):
    pass 

class QueueIsEmpty(commands.CommandError):
    pass

class NoTracksFound(commands.CommandError):
    pass

class PlayerIsAlreadyPaused(commands.CommandError):
    pass

class NoMoreTracks(commands.CommandError):
    pass 

class NoPreviousTracks(commands.CommandError):
    pass

class InvalidRepeatMode(commands.CommandError):
    pass



class RepeatMode(Enum):
    NONE = 0
    ONE = 1
    ALL = 2


class Queue:
    def __init__(self):
        self._queue = []
        self.position = 0
        self.repeat_mode = RepeatMode.NONE 

    @property 
    def is_empty(self):
        return not self._queue 

    # @property
    # def first_track(self):
    #     if not self._queue:
    #         raise QueueIsEmpty

    #     return self._queue[0]

    @property 
    def current_track(self):
        if not self._queue:
            raise QueueIsEmpty

        if self.position <= len(self._queue) - 1:
            return self._queue[self.position]

    @property 
    def upcomming(self):
        if not self._queue:
            raise QueueIsEmpty

        return self._queue[self.position + 1:]

    @property 
    def history(self):
        if not self._queue:
            raise QueueIsEmpty

        return self._queue[:self.position]

    @property 
    def length(self):
        return len(self._queue)

    def add(self, *args):
        self._queue.extend(args)

    def get_next_track(self):
        if not self._queue:
            raise QueueIsEmpty

        self.position += 1

        if self.position < 0:
            return None 
        elif self.position > len(self._queue) -1:
            if self.repeat_mode == RepeatMode.ALL:
                self.position = 0
            else:
                return None 

        return self._queue[self.position]

    def shuffle(self):
        if not self._queue:
            raise QueueIsEmpty

        upcomming = self.upcomming 
        random.shuffle(upcomming)
        self._queue = self._queue[:self.position + 1]
        self._queue.extend(upcomming)

    def set_repeat_mode(self, mode):
        if mode == "none":
            self.repeat_mode = RepeatMode.NONE
        elif mode == "1":
            self.repeat_mode = RepeatMode.ONE 
        elif mode == "all":
            self.repeat_mode = RepeatMode.ALL

    def empty(self):
        self._queue.clear()
        self.position = 0


class Player(wavelink.Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = Queue()

    async def connect(self, ctx, channel=None):
        if self.is_connected:
            raise AlreadyConnectedToChannel

        if (channel := getattr(ctx.author.voice, "channel", channel)) is None:
            raise NoVoiceChannel 

        await super().connect(channel.id)
        return channel 


    async def teardown(self):             # disconnect
        try:
            await self.destroy()
        except KeyError:
            pass 

    async def add_tracks(self, ctx, tracks):
        if not tracks:
            raise NoTracksFound

        if isinstance(tracks, wavelink.TrackPlaylist):
            self.queue.add(*tracks.tracks)

        elif len(tracks) == 1:
            self.queue.add(tracks[0])
            # await ctx.send(f"Added {tracks[0].title} to the queue.")

        else:
            if (track := await self.choose_track(ctx, tracks)) is not None:
                self.queue.add(track)
                # await ctx.send(f"Added {track.title} to the queue.")

        if not self.is_playing and not self.queue.is_empty:
            await self.start_playback()

    async def choose_track(self, ctx, tracks):
        def _check(r, u):
            return (
                r.emoji in OPTIONS.keys()
                and u == ctx.author 
                and r.message.id == msg.id 
            )

        embed = discord.Embed(
            title = "Choose a song",
            description = (
                "\n".join(
                    f"**{i+1}.** {t.title} ({t.length//60000}:{str(t.length%60).zfill(2)})"
                    for i, t in enumerate(tracks[:5])
                )
            ),
            color = ctx.author.color,
            timestamp = dt.datetime.utcnow()
        )
        embed.set_author(name = "Query Results")
        embed.set_footer(text = f"Invoked by {ctx.author.display_name}", icon_url = ctx.author.avatar_url)

        msg = await ctx.send(embed = embed)
        for emoji in list(OPTIONS.keys())[:min(len(tracks), len(OPTIONS))]:
            await msg.add_reaction(emoji)

        try:
            reaction, _ = await self.bot.wait_for("reaction_add", timeout = 60.0, check = _check)
        except asyncio.TimeoutError:
            await msg.delete()
            await ctx.message.delete()
        else:
            await msg.delete()
            return tracks[OPTIONS[reaction.emoji]]

    async def start_playback(self):
        await self.play(self.queue.current_track)

    async def advance(self):
        try:
            if (track := self.queue.get_next_track()) is not None:
                await self.play(track)
        except QueueIsEmpty:
            pass

    async def repeat_track(self):
        await self.play(self.queue.current_track)



class Music(commands.Cog, wavelink.WavelinkMixin):
    def __init__(self, bot):
        self.bot = bot 
        self.wavelink = wavelink.Client(bot=bot)
        self.bot.loop.create_task(self.start_nodes())

    def load_data(self):
        self.id = fh.load_file('id')

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not member.bot and after.channel is None:                            # checking if member is not bot && check if member left the channel
            if not [m for m in before.channel.members if not m.bot]:            # Disconnect the bot from the channel
                await self.get_player(member.guild).teardown()

    @wavelink.WavelinkMixin.listener()
    async def on_node_ready(self, node):
        print(f"Wavelink node '{node.identifier}' ready.")

    @wavelink.WavelinkMixin.listener("on_track_stuck")
    @wavelink.WavelinkMixin.listener("on_track_end")
    @wavelink.WavelinkMixin.listener("on_track_exception")
    async def on_player_stop(self, node, payload):
        if payload.player.queue.repeat_mode == RepeatMode.ONE:
            await payload.player.repeat_track()
        else:
            await payload.player.advance()

    async def cog_check(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("Music commands are not avaible in DMs.")
            return False 
        
        return True

    async def start_nodes(self):
        await self.bot.wait_until_ready()

        nodes = {
            "MAIN": {
                "host": "127.0.0.1",
                "port": 2333,
                "rest_uri": "http://127.0.0.1:2333",
                "password": "youshallnotpass",
                "identifier": "MAIN",
                "region": "europe",
            }
        }

        for node in nodes.values():
            await self.wavelink.initiate_node(**node)

    def get_player(self, obj):
        if isinstance(obj, commands.Context):
            # print(obj.guild.id)
            return self.wavelink.get_player(obj.guild.id, cls=Player, context=obj)
        elif isinstance(obj, discord.Guild):
            # print(obj.id)
            return self.wavelink.get_player(obj.id, cls=Player)


# CONNECT
    @commands.command(name="connect", aliases=["join"])
    async def connect_command(self, ctx, *, channel: t.Optional[discord.VoiceChannel]):
        player = self.get_player(ctx)
        channel = await player.connect(ctx, channel)
        # await ctx.send(f"Connected to {channel.name}.")

    @connect_command.error 
    async def connect_connect_error(self, ctx, exc):
        if isinstance(exec, AlreadyConnectedToChannel):
            await ctx.send("Already connected to a voice channel.")
        elif isinstance(exc, NoVoiceChannel):
            await ctx.send("No suitable voice channel was provided.")


# DISCONNECT
    @commands.command(name="disconnect", aliases=["leave"])
    async def disconnect_command(self, ctx):
        player = self.get_player(ctx)
        await player.teardown()
        # await ctx.send("Disconnect.")


# PLAY
    @commands.command(name="play", aliases=["dj"])
    async def play_command(self, ctx, *, query: t.Optional[str]):
        player = self.get_player(ctx)

        if not player.is_connected:
            await player.connect(ctx)

        if query is None:
            if player.queue.is_empty:
                raise QueueIsEmpty

            await player.set_pause(False)
            # await ctx.send("Playback resumed.")

        else:
            query = query.strip("<>")
            if not re.match(URL_REGEX, query):
                query = f"ytsearch:{query}"

            self.load_data()
            dj_lama_leif_channel = self.bot.get_channel(self.id["RDF"]["dj_lama_leif_channel_id"])
            await dj_lama_leif_channel.purge(limit = 1) 

            await player.add_tracks(ctx, await self.wavelink.get_tracks(query))

    @play_command.error
    async def play_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("No songs to play as the queue is empty.")
        elif isinstance(exec, NoVoiceChannel):
            await ctx.send("No suitable voice channel was provided.")


# PAUSE
    @commands.command(name="pause")
    async def pause_command(self, ctx):
        player = self.get_player(ctx)
        # if player == None:
            # player = self.wavelink.get_player(guild.id, cls=Player, context=payload)


        if player.is_paused:
            raise PlayerIsAlreadyPaused

        await player.set_pause(True)
        # await ctx.send("Playback paused.")

    @pause_command.error 
    async def pause_command_error(self, ctx, exc):
        if isinstance(exc, PlayerIsAlreadyPaused):
            await ctx.send("Already paused.")


# STOP
    @commands.command(name="stop")
    async def stop_command(self, ctx):
        player = self.get_player(ctx)
        player.queue.empty()
        await player.stop()
        # await ctx.send("Playback stopped.")


# NEXT
    @commands.command(name="next", aliases=["skip"])
    async def next_command(self, ctx):
        player = self.get_player(ctx)

        if not player.queue.upcomming:
            raise NoMoreTracks

        await player.stop()
        # await ctx.send("Playing next track in queue.")

    @next_command.error 
    async def next_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("This skip could not be executed as the queue is currently empty.")
        elif isinstance(exc, NoMoreTracks):
            await ctx.send("There are no more tracks in the queue.")


# PREVIOUS
    @commands.command(name="previous")
    async def previous_command(self, ctx):
        player = self.get_player(ctx)

        if not player.queue.history:
            raise NoPreviousTracks

        player.queue.position -= 2
        await player.stop()
        # await ctx.send("Playing previous track in queue.")        

    @previous_command.error 
    async def previous_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("This previous skip could not be executed as the queue is currently empty.")
        elif isinstance(exc, NoPreviousTracks):
            await ctx.send("There are no previous tracks in the queue.")


# SHUFFLE
    @commands.command(name="shuffle")
    async def shuffle_command(self, ctx):
        player = self.get_player(ctx)
        player.queue.shuffle()
        # await ctx.send("Queue shuffled.")

    @shuffle_command.error 
    async def shuffle_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("The queue could not be shuffled as it is currently empty.")


# REPEAT
    @commands.command(name="repeat")
    async def repeat_command(self, ctx, mode: str):
        if mode not in ("none", "1", "all"):
            raise InvalidRepeatMode

        player = self.get_player(ctx)
        player.queue.set_repeat_mode(mode)
        # await ctx.send(f"The repeat mode has been set to {mode}.")


# QUEUE
    @commands.command(name="queue")
    async def queue_command(self, ctx, show: t.Optional[int] = 10):
        player = self.get_player(ctx)

        if player.queue.is_empty:
            raise QueueIsEmpty

        embed = discord.Embed(
            title = "Queue",
            description = f"Showing up to next {show} tracks",
            color = ctx.author.color,
            timestamp = dt.datetime.utcnow()
        )
        embed.set_author(name = "Query Results")
        embed.set_footer(text = f"Requested by {ctx.author.display_name}", icon_url = ctx.author.avatar_url)
        embed.add_field(
            name = "Currently playing", 
            value = getattr(player.queue.current_track.title, "title", "No Tracks currently playing."), 
            inline = False)
        if upcomming := player.queue.upcomming:
            embed.add_field(
                name = "Next up",
                value = "\n".join(t.title for t in player.queue.upcomming[:show]),
                inline = False 
            )

        msg = await ctx.send(embed = embed)

    @queue_command.error 
    async def queue_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("The queue is currently empty.")

    @commands.command(name="musicinterface")
    async def musicinterface_command(self, ctx):
        guild = ctx.message.guild 
        member = guild.get_member(ctx.author.id)
        udvikler_role = discord.utils.get(guild.roles, name='Udvikler')

        if udvikler_role in member.roles:
            self.load_data()
            dj_lama_leif_channel = self.bot.get_channel(self.id["RDF"]["dj_lama_leif_channel_id"])
            if dj_lama_leif_channel == ctx.channel:
                await dj_lama_leif_channel.purge(limit = 50) 
                await self.musicinterface_message()

    async def musicinterface_message(self):
        self.load_data()
        dj_lama_leif_channel = self.bot.get_channel(self.id["RDF"]["dj_lama_leif_channel_id"])

        musicinterface_embed = discord.Embed(title="DJ Lama Leif",color=0x303136)
        musicinterface_embed.set_thumbnail(url="https://media.discordapp.net/attachments/747967053050151014/797675061833105418/RDF_leif_round.png")
        musicinterface_embed.add_field(name="\u200B", value="Skriv **+dj** og titlen på en sang som DJ Lama Leif skal afspille")
        musicinterface_embed_message = await dj_lama_leif_channel.send(embed = musicinterface_embed)
        musicinterface_embed_message_id = musicinterface_embed_message.id 

        await musicinterface_embed_message.add_reaction(emoji="\u23EA")         # rewind
        await musicinterface_embed_message.add_reaction(emoji="\u23EF")         # play/pause
        await musicinterface_embed_message.add_reaction(emoji="\u23E9")         # fast forward
        await musicinterface_embed_message.add_reaction(emoji="\U0001F504")     # repeat

        self.id["RDF"]["musicinterface_embed_message_id"] = musicinterface_embed_message_id
        fh.save_file(self.id, "id")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        self.load_data()
        bot_id = self.id['RDF']['discord_bot_id']
        if payload.user_id == bot_id:
            return  # bot reacted

        reaction = payload.emoji.name 

        rewind_reaction = "\u23EA"
        play_pause_reaction = "\u23EF"
        fast_forward_reaction = "\u23E9"
        repeat_reaction = "\U0001F504"

        if reaction in [rewind_reaction, play_pause_reaction, fast_forward_reaction, repeat_reaction]:
            dj_lama_leif_channel = self.bot.get_channel(self.id["RDF"]["dj_lama_leif_channel_id"])
            dj_lama_leif_voice_channel = self.bot.get_channel(self.id["RDF"]["dj_lama_leif_voice_channel_id"])
            payload_channel = self.bot.get_channel(payload.channel_id)

            if payload_channel == dj_lama_leif_channel:
                guild = self.bot.get_guild(payload.guild_id)
                member = guild.get_member(payload.user_id)

                if member not in dj_lama_leif_voice_channel.members:
                    return

                member_voice_channel = member.voice.channel 
                if member_voice_channel != dj_lama_leif_voice_channel:
                    return

                if member_voice_channel == dj_lama_leif_voice_channel and member in dj_lama_leif_voice_channel.members:
                    player = self.wavelink.get_player(guild.id, cls=Player, context=payload)
                    if player.queue.is_empty:
                        return

                    if reaction == rewind_reaction:
                        if not player.queue.history:
                            return 
                        player.queue.position -= 2
                        await player.stop()

                    if reaction == play_pause_reaction:
                        if player.is_paused:    
                            await player.set_pause(False)
                        else:
                            await player.set_pause(True)

                    if reaction == fast_forward_reaction:
                        if not player.queue.upcomming:
                            return 
                        await player.stop()
                        return 
                        
                    if reaction == repeat_reaction:
                        if player.queue.repeat_mode == RepeatMode.NONE:
                            player.queue.set_repeat_mode("1")
                            print (player.queue.repeat_mode)
                            return
                        if player.queue.repeat_mode == RepeatMode.ONE:
                            player.queue.set_repeat_mode("none")
                            print (player.queue.repeat_mode)
                            return



def setup(bot):
    bot.add_cog(Music(bot))
