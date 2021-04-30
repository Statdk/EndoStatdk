import asyncio
import json
import random
import string
import time
from datetime import datetime
from os import path

import discord
import youtube_dl
from discord import player
from discord.ext import tasks, commands

if path.exists('./bot/config.json'):
    with open('./bot/config.json') as f:
        CONFIG = json.load(f)
        f.close()
else:
    with open('/home/pi/Desktop/config.json') as f:
        CONFIG = json.load(f)
        f.close()


client = commands.Bot(command_prefix='.')
logChannel = 722277448934359073

# region Methods/Functions


def testNumber(arg):
    """outputs True if 'f' is a number"""
    try:
        x = float(arg)
    except ValueError:
        return False
    return True


async def log(arg):
    await client.get_channel(logChannel).send(formatCode(f'Error:\n{arg}\n{datetime.now()}\n...'), "diff")


def formatCode(arg, type=""):
    """Converts formatting to one suited for discord

    "diff" = red;
    "css" = red-orange;
    "fix" = yellow;
    "ini" with [] = blue;
    "json" with "" = green;
    " " = none
    """
    toSend = f"```{type}\n{arg}\n```"
    return toSend

# endregion

# region Events


@client.event
async def on_ready():
    print(
        f"Logged in as\n{client.user.name}\n{client.user.id}\n{datetime.now()}\n...")

    await client.get_channel(logChannel).send(f'Logged in as\n{client.user.name}\n{client.user.id}\n{datetime.now()}\n...')
    await client.change_presence(activity=discord.Activity(name="", type=4))

# endregion

# region Commands


class Fun():
    @client.command(aliases=['8ball'])
    async def _8ball(self, *, question=None):
        """Ask the 8ball a question"""
        if question == None:
            await self.send(f"Command syntax: `.8ball [question]`")
        elif testNumber(question):
            await self.send(f"You imbecil! {question} is a number!")
        else:
            responses = ["It is certain.",
                         "It is decidedly so.",
                         "Without a doubt.",
                         "Yes - definitely.",
                         "You may rely on it.",
                         "As I see it, yes.",
                         "Most likely.",
                         "Outlook good.",
                         "Yes.",
                         "Signs point to yes.",
                         "Reply hazy, try again.",
                         "Ask again later.",
                         "Better not tell you now.",
                         "Cannot predict now.",
                         "Concentrate and ask again.",
                         "Don't count on it.",
                         "My reply is no.",
                         "My sources say no.",
                         "Outlook not so good.",
                         "Very doubtful."]
            await self.send(f"{random.choice(responses)}")

    @client.command()
    async def status(self, text=None, type=1):
        if text == None:
            await client.change_presence(activity=discord.Activity(name="", type=4))
            return
        await client.change_presence(activity=discord.Activity(name=text, type=type))

    @client.command(aliases=['random'])
    async def rand(self, *, args="0 100 1"):
        """Returns an amount of random numbers"""
        # Arguments are: Minimum, Maximum, and Amount
        args = args.split()

        tosend = ""
        try:
            for i in range(int(args[2])):
                tosend += f"{random.choice(range(int(args[0]), int(args[1])))}\n"
        except Exception as e:
            await log(e)
            await self.send("Command syntax: '.random <minimum> <maximum> <number of messages>'")
            return

        await self.send(tosend)


class Moderation():
    @client.command(aliases=['purge', 'prune', 'del'])
    @commands.has_permissions(manage_messages=True)
    async def delete(self, *, amount=""):
        """Clears a number of messages"""
        if amount == "":
            await self.channel.purge(limit=1)
            await self.send(formatCode("Command syntax: `.delete <number of messages>`", "diff"), delete_after=3)
        elif not testNumber(amount):
            await self.channel.purge(limit=1)
            await self.send(formatCode("That's not a number...", "diff"), delete_after=3)
        else:
            await self.channel.purge(limit=int(amount) + 1)
            log(f"Deleted {amount} messages in {self.get_channel}")


class Math():
    @client.command(aliases=['addition', 'ad'])
    async def add(self, a, b):
        """Adds two numbers"""
        if testNumber(a) and testNumber(b):
            await self.send(formatCode(f"[{float(a) + float(b)}]", "ini"))
        else:
            await self.send(formatCode('Command syntax:: `.add [first] [second]`', "diff"))

    @client.command(aliases=['subtraction', 'sub'])
    async def subtract(self, a, b):
        """Subtracts two numbers"""
        if testNumber(a) and testNumber(b):
            await self.send(formatCode(f"[{float(a) - float(b)}]", "ini"))
        else:
            await self.send(formatCode('Command syntax:: `.subtract [first] [second]`', "diff"))

    @client.command(aliases=['multiplication', 'mult'])
    async def multiply(self, a, b):
        """Multiplies two numbers"""
        if testNumber(a) and testNumber(b):
            await self.send(formatCode(f"[{float(a) * float(b)}]", "ini"))
        else:
            await self.send(formatCode('Command syntax:: `.multiply [first] [second]`', "diff"))

    @client.command(aliases=['division', 'div'])
    async def divide(self, a, b):
        """Divides two numbers"""
        if testNumber(a) and testNumber(b):
            await self.send(formatCode(f"[{float(a) / float(b)}]", "ini"))
        else:
            await self.send(formatCode('Command syntax:: `.divide [first] [second]`', "diff"))

    @ client.command(aliases=['compute'])
    async def math(self, *, arg):
        """Performs simple math operations from left to right"""
        arg = arg.split()
        ans = float(arg[0])
        args = 0
        f = 1

        for i in arg:
            try:
                if i == "+":
                    ans += float(arg[f])
                    args += 1
                elif i == "-":
                    ans -= float(arg[f])
                    args += 1
                elif i == "*":
                    ans *= float(arg[f])
                    args += 1
                elif i == "/":
                    ans /= float(arg[f])
                    args += 1
                f += 1

            except Exception as e:
                await self.send(e)
                await self.send(formatCode("Command syntax:: `.math [a] [operator] [b] [operator] [c] ...`", "diff"))
                return

        await self.send(formatCode(f"Result: [{ans}] with [{args}] arguments", "ini"))


class Management():
    @ client.command()
    async def ping(self):
        await self.send(formatCode(f'Pong! [{round(client.latency * 1000)}ms]', "ini"))

    @ client.command()
    @ commands.has_permissions(manage_messages=True)
    async def shutdown(self):
        await self.send(formatCode(f"Shutting down\n{datetime.now()}\n...", "diff"))
        log("Shutting down")
        client.logout()
        exit()

    @ client.command()
    async def say(self, channel_id, message):
        try:
            if (client.is_owner(self.author)):
                toSend = client.get_channel(int(channel_id))
                await toSend.send(str(message))

        except Exception as e:
            await log(e)

        await self.message.delete()

# endregion

# region MUSIC


# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''


ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    # bind to ipv4 since ipv6 addresses cause issues sometimes
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queueList = []
        self.vol = 20

    @ commands.command()
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        """Joins a voice channel"""

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        if channel is not None:
            await channel.connect()
        elif ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send(formatCode("Could not connect to voice channel", "diff"))

    @ commands.command()
    async def play(self, ctx, *, url):
        """Streams from a url (same as yt, but doesn't predownload)"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print(
                'Player error: %s' % e) if e else None)

        await ctx.send(formatCode('Now playing: "{}"'.format(player.title), json))

        ctx.voice_client.source.volume = self.vol / 100
        await client.change_presence(activity=discord.Activity(name=player.title, type=2))

    @ commands.command(aliases=['vol', 'v'])
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""
        self.vol = volume

        if ctx.voice_client is None:
            return await ctx.send(formatCode("Not connected to a voice channel.", "diff"))

        ctx.voice_client.source.volume = volume / 100
        await ctx.send(formatCode("Changed volume to [{}%]".format(volume), "ini"))

    @ commands.command(aliases=['q'])
    async def queue(self, ctx, *, url):
        """Shows the current queue or adds songs"""
        toSend = ""

        try:
            self.queueList.append(await YTDLSource.from_url(url, loop=self.bot.loop, stream=True))
            await ctx.send(formatCode(f'Added "{self.queueList[-1]}"', json))

        except Exception as e:
            log(e)

        if not self.queueList == []:
            toSend += "Current Queue:"
            for item in self.queueList:
                toSend += f'\n> {self.queueList.index(item)}. "{item.title}"'
        else:
            await ctx.send(formatCode("Queue is empty", "fix"))

        if not toSend == "":
            await ctx.send(formatCode(toSend, "json"))

    @ tasks.loop(seconds=5)
    async def queuer(self, ctx):
        try:
            if self.queueList == [] or not self.player.is_connected():
                self.queuer.stop()
            if not self.player.is_playing():
                player = self.queueList[0]
                self.queueList.pop(0)

                ctx.voice_client.play(player, after=lambda e: print(
                    'Player error: %s' % e) if e else None)

                await ctx.send(formatCode('Now playing: "{}"'.format(player.title), json))
        except Exception as e:
            log(e)

    @ commands.command(aliases=['cl', 'cls'])
    async def clear(self, ctx):
        """Clears the queue"""
        self.queueList.clear()
        await ctx.send(formatCode("Queue Cleared", "fix"))

    @ commands.command()
    async def pause(self, ctx):
        """Pauses/Unpauses the bot"""
        try:
            if player.is_paused():
                player.resume()
            elif player.is_playing():
                player.pause()
            else:
                await ctx.send(formatCode("Play something first", "fix"))
        except Exception:
            await ctx.send(formatCode("Player is inactive", "fix"))

    @ commands.command()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""

        self.queueList.clear()

        await client.change_presence(activity=discord.Activity(name="", type=4))
        await ctx.voice_client.disconnect()

    @ play.after_invoke
    async def ensure_queuer(self, ctx):
        if not self.queuer.is_running():
            self.queuer.start()

    @ play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError(
                    "Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()

# endregion


client.add_cog(Music(client))
client.run(CONFIG["token"])
