from asyncio import sleep as asyncioSLEEP
from discord import File as discordFILE
from discord.ext import commands
from pathlib import Path
from sys import path as sysPATH
sysPATH.insert(1, str(Path.cwd()))

from graph_producer import produce_user_graph, produce_server_graph
from sqlite_handler import fetch_timezone, replace_timezone, fetch_schedule, online_freq
import timezones


class public_commands(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    
    @commands.command(aliases = ["Myactivity","MyActivity", "ma", "MA"])
    async def myactivity(self, context, private="True"):
        ''' Print out your current discord online activity. (see the data for the last 10 days)
            The second argument denotes whether you want the bot to dm you the activity graph or 
            post it in the server chat. '''
        user_name = str(context.message.author).split("#")[0]
        user_id = context.message.author.id
        user_tz = fetch_timezone(user_id)
        now = timezones.DateTime.now(timezones.pytzTIMEZONE(user_tz)) # current time according to timezone tzone

        lista = fetch_schedule(user_id, timezones.pytzUTC)
        produce_user_graph(lista, user_id, user_name, user_tz)
        
        if private == "False" or private == "false":
            image_message = await context.send(file=discordFILE(f"./graph_folder/UserAct_{user_id}.png"))
            emoji = "\N{THUMBS UP SIGN}"
            await context.message.add_reaction(emoji) # React with success

            # Delete the image 1min, 30 seconds after sending it to prevent clogging up space
            await asyncioSLEEP(90)
            try:
                await image_message.delete()
            except Exception as _:
                # The image has already been deleted, do nothing.
                pass
        else:
            # DM the user with the image, no need to delete the image.
            image_message = await context.message.author.send(file=discordFILE(f"./graph_folder/UserAct_{user_id}.png"))
            emoji = "\N{THUMBS UP SIGN}"
            await context.message.add_reaction(emoji) # React with success


    @commands.command(aliases = ["Serveractivity", "serverActivity", "ServerActivity", "sa", "SA"])
    async def serveractivity(self, context, tz="UTC"):
        ''' Print a bar graph displaying how many people on average (in the span of a week) are online at various hours. 
            The second argument is a valid timezone to display the correct day and times for any region. '''
        if tz in timezones.valid_timezones:
            guild_hash = hash(context.message.author.guild)
            guild_name = str(context.message.guild.name)
            days_data_recorded = online_freq[guild_hash]["DAYS"]
            now = timezones.DateTime.now(timezones.pytzTIMEZONE(tz)) # current time according to timezone tzone

            produce_server_graph(online_freq[guild_hash]["FREQ"], guild_name, guild_hash, days_data_recorded, tz) # Get the respective freq graph for the server
            image_message = await context.send(file=discordFILE(f"./graph_folder/GuildAct_{guild_hash}.png"))
            emoji = "\N{THUMBS UP SIGN}"
            await context.message.add_reaction(emoji) # React with success

            # Delete the image 1min, 30 seconds after sending it to prevent clogging up space
            await asyncioSLEEP(90)
            try:
                await image_message.delete()
            except Exception as _:
                # The image has already been deleted, do nothing.
                pass
        else:
            await context.send("Invalid timezone. Say =tz for valid timezones.")
            emoji = "\N{THUMBS DOWN SIGN}"
            await context.message.add_reaction(emoji)


    @commands.command(aliases = ["SetTimeZone", "SetTZ", "Settz", "settz"])
    async def settimezone(self, context, tz="UTC"):
        ''' Set your personal timezone for "myactivity" command. '''
        if tz in timezones.valid_timezones:
            replace_timezone(context.message.author.id, tz)
            emoji = "\N{THUMBS UP SIGN}"
            await context.message.add_reaction(emoji)
        else:
            await context.send("Invalid timezone. Say =tz for valid timezones.")
            emoji = "\N{THUMBS DOWN SIGN}"
            await context.message.add_reaction(emoji)


    @commands.command(aliases = ["Timezones", "timeZones", "TimeZones", "TZ", "tz"])
    async def timezones(self, context, option="main"):
        ''' Display a list of all of the valid timezones for the "myactivity" and "serveractivity" command.
            The second argument is "main" so you can list all of the main timezones, or the name of any regional continent. '''
        if option == "main":
            await context.send("Universal timezones:")
            await context.send("|| "+timezones.universalTimeZoneFormatted)
            await context.send("Continents (Say =tz {continent name} for more specific timezones):")
            await context.send("|| "+timezones.continentsFormatted)
        elif option in timezones.mainTimeZonesClean:
            await context.send(f"{option} Timezones:")
            await context.send("|| "+(", ".join([item for item in timezones.common_timezones_set if item.split("/",1)[0] == option])).rstrip(", "))
        else:
            await context.send("Invalid option/continent")


def setup(client):
    client.add_cog(public_commands(client))