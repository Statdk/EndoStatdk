#!/usr/bin/env python

import json
import random
import string
import time
from datetime import datetime
from os import path

import discord
import youtube_dl
from discord.ext import commands

if path.exists('config.json'):
    with open('config.json') as f:
        CONFIG = json.load(f)
        f.close()
else:
    with open('/home/pi/Desktop/config.json') as f:
        CONFIG = json.load(f)
        f.close()


client = commands.Bot(command_prefix = '.')
logChannel =  722277448934359073
vol = 20

#Methods/Functions______________________________________________________________

#outputs True if 'f' is a number
def testNumber(arg):
    try:
        x = float(arg)
    except ValueError:
        return False
    return True

async def log(arg):
    await client.get_channel(logChannel).send(f'Error:\n{arg}\n{datetime.now()}\n...')

#Events_________________________________________________________________________

@client.event
async def on_ready():
    print(f"Logged in as\n{client.user.name}\n{client.user.id}\n{datetime.now()}\n...")
    await client.get_channel(logChannel).send(f'Logged in as\n{client.user.name}\n{client.user.id}\n{datetime.now()}\n...')
    await client.change_presence(activity = discord.Activity(name="", type=4))

#Commands_______________________________________________________________________

@client.command()
async def ping(ctx):
    await ctx.send(f'Pong! `{round(client.latency * 1000)}ms`')

@client.command(aliases=['8ball'])
async def _8ball(ctx, *, question = None):
    """Ask the 8ball a question"""
    if question == None:
        await ctx.send(f"Command syntax: `.8ball [question]`")
    elif testNumber(question):
        await ctx.send(f"You imbecil! {question} is a number!")
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
        await ctx.send(f"{random.choice(responses)}")

@client.command(aliases=['purge', 'prune', 'delete', 'del'])
@commands.has_permissions(manage_messages=True)
async def clear(ctx, *, amount = ""):
    """Clears a number of messages"""
    if amount == "":
        await ctx.channel.purge(limit = 1)
        await ctx.send("Command syntax: `.delete <number of messages>`", delete_after = 3)
    elif not testNumber(amount):
        await ctx.channel.purge(limit = 1)
        await ctx.send("That's not a number...", delete_after = 3)
    else:
        await ctx.channel.purge(limit=int(amount) + 1)
        log(f"Deleted {amount} messages in {ctx.get_channel}")

@client.command(aliases=['random'])
async def rand(ctx, *, args = "0 100 1"):
    ##Arguments are: Minimum, Maximum, and Amount
    args = args.split()
    
    tosend = ""
    try:
        for i in range(int(args[2])):
            tosend += f"{random.choice(range(int(args[0]), int(args[1])))}\n"
    except Exception as e:
        await log(e)
        await ctx.send("Command syntax: '.random <minimum> <maximum> <number of messages>'")
        return

    await ctx.send(tosend)

@client.command(aliases=['addition', 'ad'])
async def add(ctx, a, b):
    if testNumber(a) and testNumber(b):
        await ctx.send(float(a) + float(b))
    else:
        await ctx.send('Command syntax:: `.add [first] [second]`')

@client.command(aliases=['subtraction', 'sub'])
async def subtract(ctx, a, b):
    if testNumber(a) and testNumber(b):
        await ctx.send(float(a) - float(b))
    else:
        await ctx.send('Command syntax:: `.subtract [first] [second]`')

@client.command(aliases=['multiplication', 'mult'])
async def multiply(ctx, a, b):
    if testNumber(a) and testNumber(b):
        await ctx.send(float(a) * float(b))
    else:
        await ctx.send('Command syntax:: `.multiply [first] [second]`')

@client.command(aliases=['division', 'div'])
async def divide(ctx, a, b):
    if testNumber(a) and testNumber(b):
        await ctx.send(float(a) / float(b))
    else:
        await ctx.send('Command syntax:: `.divide [first] [second]`')

@client.command()
async def math(ctx, *, arg):
    """Performs simple math operations from left to right"""
    arg = arg.split()
    ans = float(arg[0])
    
    args = 0
    f = 0
    for i in arg:
        f += 1

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
        except Exception as e:
            await ctx.send(e)
            await ctx.send("Command syntax:: `.math a operator b operator c ...`")
            return

    await ctx.send(f"Result: {ans}")

@client.command()
@commands.has_permissions(manage_messages=True)
async def shutdown(ctx):
    await ctx.send(f"Shutting down\n{datetime.now()}")
    exit()

@client.command()
async def status(ctx, text = None, type = 1):
    if text == None:
        await client.change_presence(activity = discord.Activity(name="", type=4))
        return
    await client.change_presence(activity = discord.Activity(name=text, type=type))


##MUSIC_________________________________________________________________________________

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
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
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

    @commands.command()
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        """Joins a voice channel"""

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()

    @commands.command()
    async def play(self, ctx, *, query):
        """Plays a file from the local filesystem"""

        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(query))
        ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send('Now playing: {}'.format(query))

        ctx.voice_client.source.volume = vol / 100
        await client.change_presence(activity = discord.Activity(name=player.title, type=2))

    @commands.command()
    async def yt(self, ctx, *, url):
        """Plays from a url (almost anything youtube_dl supports)"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop)
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send('Now playing: {}'.format(player.title))

        ctx.voice_client.source.volume = vol / 100
        await client.change_presence(activity = discord.Activity(name=player.title, type=2))

    @commands.command()
    async def stream(self, ctx, *, url):
        """Streams from a url (same as yt, but doesn't predownload)"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send('Now playing: {}'.format(player.title))

        ctx.voice_client.source.volume = vol / 100
        await client.change_presence(activity = discord.Activity(name=player.title, type=2))

    @commands.command(aliases = ['vol', 'v'])
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""
        vol = volume

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        ctx.voice_client.source.volume = volume / 100
        await ctx.send("Changed volume to {}%".format(volume))

    @commands.command()
    async def pause(self, ctx):
        """Pauses and unpauses the player"""
        if client.is_paused():
            client.resume()
        else:
            client.pause()

    @commands.command()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""

        await client.change_presence(activity = discord.Activity(name="", type=4))
        await ctx.voice_client.disconnect()

    @play.before_invoke
    @yt.before_invoke
    @stream.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()

client.add_cog(Music(client))
client.run(CONFIG["token"])
