# Import Libary discord to access to Discord's API
import discord
from discord.ext import commands
from discord.utils import get
# Import Libary youtube-dl for download videos from youtube.com or other video platforms
import youtube_dl
# Import Libary asyncio which can help to reduce using of time
import asyncio
from async_timeout import timeout
# Import partial for creating function with fixed parameter
from functools import partial
# Import itertools for using islice function
import itertools
# Import YoutubeDL for downloding the song
from youtube_dl import YoutubeDL


# Get Token from env file
import os
from dotenv import load_dotenv
load_dotenv()
token = os.getenv('Token')



# Declare prefix of the command
bot = commands.Bot(command_prefix = '*', help_command = None)


# Runtime Error Bug fixed in HEROKU
OPUS_LIBS = ['libopus-0.x86.dll', 'libopus-0.x64.dll', 'libopus-0.dll', 'libopus.so.0', 'libopus.0.dylib']


# Silence useless bug reports messages
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'extractaudio': True,
    'audioformat': 'mp3',
    'outtmpl': 'downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s', # For out put name
    'restrictfilenames': True, # Don't allow "&" and spaces in file names
    'noplaylist': True, # Don't allow any playlist link
    'nocheckcertificate': True, # Don't verify SSL certificates
    'ignoreerrors': False, # Stop if download is error.
    'no_warnings': True, # Do not print out anything for warnings.
    'default_search': 'auto', # Prepend this string if an input url is not valid. 'auto' for elaborate guessing
}

ytdl = YoutubeDL(ytdl_format_options)


# This is for Song's bug, So the song won't be played until the end if you don't have this line 
ffmpeg_options = {
    'options': '-vn',
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
}
#ref https://stackoverflow.com/questions/57688808/playing-music-with-a-bot-from-youtube-without-downloading-the-file
 

class ytdlsource(discord.PCMVolumeTransformer):

    def __init__(self, source, *, data, requester):
        super().__init__(source)
        self.requester = requester
        # declare requester's information
        self.title = data.get('title')
        # declare title of the song
        self.web_url = data.get('webpage_url')
        # declare web_url

    @classmethod
    # Download the song function
    async def create_source(cls, ctx, search: str, *, loop, download=False):
        # Creating event loop which is intermediaries for managing all the event.
        loop = loop or asyncio.get_event_loop()
        # Use partial class to fix the parameter
        # from Youtube_dl by ytdl format option as ytdl
        to_run = partial(ytdl.extract_info, url=search, download=download)
        print(search)
        print('naheeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee')
        # the type of data is a dict
        data = await loop.run_in_executor(None, to_run)
        # Finding and Getting the information of the song(in only typing the song's name :search the name of the song and pick up the first video from Youtube)
        # Downloading  the song by using ytdl_format_option
        print('kuayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy')
        if 'entries' in data:
            # take first item from a data beacause we don't need them
            # Using only the first index of the list in the value of 'entrtries'(key)
            data = data['entries'][0]

        await ctx.send('```ini\n[Added {0} to the Queue.]\n```'.format(data["title"]), delete_after = 30)

        # just for using the return
        if download:
            source = ytdl.prepare_filename(data)
        else:
            return {'webpage_url': data['webpage_url'], 'requester': ctx.author, 'title': data['title']}
            
        return cls(discord.FFmpegPCMAudio(source, **ffmpeg_options), data=data, requester=ctx.author)
        # Using cls due to @classmethod (cls is for the class, self is for the object)
        # Add function 'ffmepeg_options' for plying until the end(Bug fixed)
    @classmethod
    # Preaparing to Stream function
    async def regather_stream(cls, data, *, loop):
        """Used for preparing a stream"""
        # Creating event loop which is intermediaries for managing all the event.
        loop = loop or asyncio.get_event_loop()
        # Getting value from requester(key) in data(dict)
        requester = data['requester']

        # Use partial to fix the parameter 
        to_run = partial(ytdl.extract_info, url=data['webpage_url'], download=False)
        print('nahaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
        print(data['webpage_url'])
        data = await loop.run_in_executor(None, to_run)
        # Download the rest part that we need to stream
        print('huaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaakuayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy')
        return cls(discord.FFmpegPCMAudio(data['url'], **ffmpeg_options), data=data, requester=requester)
        # Using cls due to @classmethod (cls is for the class, self is for the object)
        # Add function 'ffmepeg_options' for plying until the end(Bug fixed)


# Creating player
class MusicPlayer:                 

    def __init__(self, ctx):
        self.bot = ctx.bot # Bot
        self._guild = ctx.guild # Server
        self._channel = ctx.channel # Channel
        self._cog = ctx.cog 

        self.queue = asyncio.Queue() #Queue Class
        self.event = asyncio.Event() #Event Class

        self.np = None  # Now playing message
        self.volume = .5 # volume .5 is the best
        self.current = None 

        # Creating task and it will do the task
        asyncio.create_task(self.player_loop())
        
    async def player_loop(self):
        """Main player loop."""
        await self.bot.wait_until_ready()
        # Waits until the client’s internal cache is all ready.

        while not self.bot.is_closed():
        # Looping if connection is not closed
            self.event.clear()
            #clear all the event
            try:
                # A bot will wait for the next song. If it timeout, it will cancel the player and disconnect automatically
                async with timeout(300):  # 5 minutes...
                    source = await self.queue.get()
            except asyncio.TimeoutError:
                await self._channel.send('See ya Dude!')
                return self.destroy(self._guild)
                # return the destroy function below

            source = await ytdlsource.regather_stream(source, loop=self.bot.loop)

            source.volume = self.volume
            self.current = source

            self._guild.voice_client.play(source, after=lambda _: self.bot.loop. call_soon_threadsafe(self.event.set))
            self.np = await self._channel.send('**Now Playing:** `{0}` requested by `{1}`'.format(source.title, source.requester))\
            # Sending Now Playing
            await self.event.wait()
            # Wait until the song end

            # After the song end. Make sure the FFmpeg process is cleaned up.
            source.cleanup()
            #run a cleanup function
            self.current = None
            
            # Now Playing message will also be delete
            try:
                # Now Playing message will be delete
                await self.np.delete()
                # delete now playing message
            except discord.HTTPException:
                pass

    def destroy(self, guild):
        """Disconnect and cleanup the player."""
        return self.bot.loop.create_task(self._cog.cleanup(guild))


class Song(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    # Cleanup Function
    async def cleanup(self, guild):
        # After Timeout Error, a bot will disconnect automatically
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass
        
        # Then deleting music player
        try:
            del self.players[guild.id]
        except KeyError:
            pass


    # In case, there are many sever that our bot are running in. We need to seperate the music player for preventing the song overlapping.
    # Creating this function will be very helpful. The music player will be generate in server by sever. 
    players = {}
    # This variable is for storing an information about the music player and the amount of sever
    # the key is guild.id, the value is like '<__main__.MusicPlayer object at 0x000001EE4B4706D0(code of player in each sever)>'
    def get_player(self, ctx):
    # It will check if there is any music player in {players}
        try:
            player = self.players[ctx.guild.id]
            # If the sever already has players, it will = player 
        except:
            player = MusicPlayer(ctx)
            self.players[ctx.guild.id] = player
            # If there is not, it will create a new object from MusicPlayer Class and put it = player 
        return player
        # Then return player


    # Play the Song Command
    @commands.command(name='play', aliases=['p'])
    async def play_(self, ctx ,* ,search: str, my_channel: discord.VoiceChannel = None):
        print('play')
        self.bot = ctx.bot
        self._guild = ctx.guild
        # is where the channel you are
        voice_client = get(self.bot.voice_clients, guild=ctx.guild)
        # is the variable that is the information for a bot, get is a function that store the information in a channel
        try:
            # Check if you're not in any sever
            my_channel = ctx.author.voice.channel
            if voice_client == None:
            # Check if a bot isn't in any sever
                await ctx.channel.send('Lil Krit has joined to **`{0}`**\nWhat\'s up Dude!'.format(my_channel), delete_after = 8)
                await my_channel.connect()
                # A bot will connect to the sever you were on

                await ctx.trigger_typing()
                # Putting 'Bot's Krit is typing...' just for decorate a bot

                startplayer = self.get_player(ctx)
                # Get the player from get_player function
                source = await ytdlsource.create_source(ctx, search, loop=bot.loop, download=False)
                # Starting downloading the song via ytdlsource Class
                print('Playing song')
                await startplayer.queue.put(source)
                # Add the song in to queue
        except:
            await ctx.channel.send('You aren\'t in any channel', delete_after = 8)

    # Pause the Song Command
    @commands.command(name='pause')
    async def pause_(self, ctx):
        print('pause')
        my_channel = ctx.author.voice.channel
        # is where the channel you are
        voice_client = get(self.bot.voice_clients, guild=ctx.guild)
        # is the variable that store the sound for a bot, (get is function that store the information in a channel)
        bot_channel = voice_client.channel
        # is where the channel your bot is
        if voice_client == None:
            # Check if a bot isn't in any sever
            await ctx.channel.send("Lil Krit is not playing any song", delete_after = 8)
            return

        if bot_channel != my_channel:
            # Check if a bot and you are not in the same sever  
            # 'voice_client.channel' = where the channel bot is, 'channel' = where the channel you are
            await ctx.channel.send("Can't do that. Lil Krit is currently connected to **`{0}`**".format(bot_channel), delete_after = 8)
            return

        else:
            # A bot will pause the song
            voice_client.pause()


    # Resume the Song Command
    @commands.command(name='resume')
    async def resume_(self, ctx):
        print('resume')
        my_channel = ctx.author.voice.channel
        # is where the channel you are
        voice_client = get(self.bot.voice_clients, guild=ctx.guild)
        # is the variable that store the sound for a bot, (get is function that store the information in a channel)
        bot_channel = voice_client.channel
        # is where the channel your bot is
        if voice_client == None:
            # Check if a bot isn't in any sever
            await ctx.channel.send("Lil Krit is not playing any song", delete_after = 8)
            return

        if bot_channel != my_channel:
            # Check if a bot and you are not in the same sever  
            # 'voice_client.channel' = where the channel bot is, 'channel' = where the channel you are
            await ctx.channel.send("Can't do that. Lil Krit is currently connected to **`{0}`**".format(bot_channel), delete_after = 8)
            return

        else:
            # A bot will resume the song
            voice_client.resume()


    # Stop the Song Command
    @commands.command(name='stop')
    async def stop_(self, ctx):
        print('stop')
        my_channel = ctx.author.voice.channel
        # is where the channel you are
        voice_client = get(self.bot.voice_clients, guild=ctx.guild)
        # is the variable that store the sound for a bot, (get is function that store the information in a channel)
        bot_channel = voice_client.channel
        # is where the channel your bot is
        if voice_client == None:
            # Check if a bot isn't in any sever
            await ctx.channel.send("Lil Krit is not playing any song", delete_after = 8)
            return

        if bot_channel != my_channel:
            # Check if a bot and you are not in the same sever  
            # 'voice_client.channel' = where the channel bot is, 'channel' = where the channel you are
            await ctx.channel.send("Can't do that. Lil Krit is currently connected to **`{0}`**".format(bot_channel), delete_after = 8)
            return

        else:
            # A bot will stop the song
            voice_client.stop()


    # Skip the Song in Queue Command
    @commands.command(name='skip')
    async def skip_(self, ctx):
        print('skip')
        my_channel = ctx.author.voice.channel
        # is where the channel you are
        voice_client = get(self.bot.voice_clients, guild=ctx.guild)
        # is the variable that store the sound for a bot, (get is function that store the information in a channel)
        bot_channel = voice_client.channel
        # is where the channel your bot is
        if voice_client == None:
            # Check if a bot isn't in any sever
            await ctx.channel.send("Lil Krit is not playing any song", delete_after = 8)
            return

        if bot_channel != my_channel:
            # Check if a bot and you are not in the same sever  
            # 'voice_client.channel' = where the channel bot is, 'channel' = where the channel you are
            await ctx.channel.send("Can't do that. Lil Krit is currently connected to **`{0}`**".format(bot_channel), delete_after = 8)
            return

        else:
            await ctx.send('**`{0}`**: Skipped the song!'.format(ctx.author))
            voice_client.stop()


    # Open Queue List Command
    @commands.command(name='queue', aliases=['q', 'playlist'])
    async def queue_info(self, ctx):
        print('queue')
        voice_client = get(self.bot.voice_clients, guild=ctx.guild)
        # is the variable that store the sound for a bot, (get is function that store the information in a channel)
        if voice_client == None:
            # Check if a bot isn't in any sever
            await ctx.channel.send("Lil Krt is not connected to any Voice Channel", delete_after = 8)
            return
            
        player = self.get_player(ctx)
        # We need player for get information about list of the song
        if player.queue.empty():
            # Check if there is no song in the queue
            await ctx.send('There are currently no more queued songs', delete_after = 6)
            return
            
        upcoming = list(itertools.islice(player.queue._queue,0,player.queue.qsize()))
        # The asyncio queue is similar to list but it isn't. So we create list for storage the song from the asyncio queue
        listtostr = '\n'.join('**`{0}`**'.format(song["title"]) for song in upcoming)
        # Format list to string
        embed = discord.Embed(title=f'Upcoming - Next {len(upcoming)}', description=listtostr, color=0xFF7A33)
        await ctx.send(embed=embed, delete_after = 45)


    # Leave Channel Command
    @commands.command(name='leave', aliases=['l'])
    async def leave_(self, ctx: commands.Context):
        print('Leave')
        # deleting music player profile
        await ctx.channel.send('See ya Dude!')
        await self.cleanup(ctx.guild)


##########################################################################################################################################

# Turning on Bot
@bot.event
async def on_ready():
    # When Bot is ready
    print('We have logged in as {0.user}'.format(bot))
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='*help'))

# Test Command
@bot.command()
async def test(ctx, *, message):
    # '*' is for spacebar
    await ctx.channel.send(message)


# Clear Command
@bot.command()
async def clear(ctx, amount = 1):
    await ctx.channel.purge(limit = amount + 1)


# Logout Command
@bot.command()
async def logout(ctx):
    print('logout')
    await ctx.channel.send('Loging Out...')
    await bot.logout()


@bot.command()
async def ajarnsun(ctx):
    await ctx.channel.send('A handsome teacher who is a big-hearted and generous person ever')


# Design 'Help' Command by emBed
@bot.command()
async def help(ctx):
    print('help')
    emBed = discord.Embed(title = 'Tutorial Lil Krit', description = 'Let\'s see what\'s Lil Krit can do for you', color = 0xFF7A33)
    emBed.add_field(name='*help', value = 'Get help commands', inline = False)
    emBed.add_field(name='*test <text>', value = 'Respond message you\'ve send', inline = False)
    emBed.add_field(name='*clear <number of messages>', value = 'Delete the previous messages', inline = False)
    emBed.add_field(name='*play or p <URL or name of the song>', value = 'Play the song and add it in to a queue', inline = False)
    emBed.add_field(name='*pause', value = 'Pause the song', inline = False)
    emBed.add_field(name='*resume', value = 'Resume the song', inline = False)
    emBed.add_field(name='*skip', value = 'Skip the song', inline = False)
    emBed.add_field(name='*stop', value = 'Stop the song', inline = False)
    emBed.add_field(name='*queue or q or playlist', value = 'Show the queue list', inline = False)
    emBed.add_field(name='*leave or l', value = 'Leave bot out of channel', inline = False)
    emBed.set_thumbnail(url='https://i.postimg.cc/W1CR8p3c/IMG-6998.jpg')
    emBed.set_author(name='Krithoolychit\'s Project', url = 'https://discord.com/users/496281331060178944', icon_url='https://i.postimg.cc/Vv2s2xBJ/Presentation1.png')
    await ctx.channel.send(embed = emBed)


bot.add_cog(Song(bot))

# Putting token in for activating Bot
bot.run(token)
