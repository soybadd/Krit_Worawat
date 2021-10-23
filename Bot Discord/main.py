# Client ID : 901118179986776094
# Token: OTAxMTE4MTc5OTg2Nzc2MDk0.YXLNtA.sEPXRNrvsKYEq6wh3vO8ab8cuQc
# Permision Integer: 8


# Import Libary Discord
import discord
from discord.embeds import Embed
from discord.ext import commands
from datetime import datetime, timedelta

bot = commands.Bot(command_prefix = '.', help_command = None)

@bot.event
# Turning on Bot
async def on_ready():
    # When Bot is ready
    print('We have logged in as {0.user}'.format(bot))


@bot.command()
async def test(ctx, *, message):
    # '*' is for spacebar
    # Respond your message
      await ctx.channel.send(message)


@bot.command()
async def clear(ctx, amount = 1):
    # Deleting the amount of message
    await ctx.channel.purge(limit = amount + 1)


@bot.command()
async def logout(ctx):
    await ctx.channel.send('Krit has been logout')
    await bot.logout()

@bot.command()
# Using emBed to design 'help' Command
async def help(ctx):
    print('help')
    emBed = discord.Embed(title = 'Toturial Bot\'s Krit help', description = 'Let\'s see what\'s Krit can do for you', color = 0xFF7A33)
    emBed.add_field(name='.help', value = 'Get help commands', inline = False)
    emBed.add_field(name='.test <text>', value = 'Respond message that you\'ve send', inline = False)
    emBed.add_field(name='.clear <number of messages>', value = 'Delete the previous messages', inline = False)
    emBed.add_field(name='.logout', value = 'Log bot out', inline = False)
    emBed.set_thumbnail(url='https://i.postimg.cc/W1CR8p3c/IMG-6998.jpg')
    emBed.set_author(name='KritHoolychit', url = 'https://discord.com/users/496281331060178944', icon_url='https://i.postimg.cc/Vv2s2xBJ/Presentation1.png')
    await ctx.channel.send(embed = emBed)



# Putting Client ID in '' for activating Bot
bot.run('OTAxMTE4MTc5OTg2Nzc2MDk0.YXLNtA.sEPXRNrvsKYEq6wh3vO8ab8cuQc')
