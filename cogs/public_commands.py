from asyncio import sleep as asyncioSLEEP
from discord import File as discordFILE, User as discordUser
from discord.ext import commands
from library.graph_producer import produce_user_graph, produce_server_graph
from library.sqlite_handler import fetch_timezone, replace_timezone, fetch_schedule, online_freq
from library.id_obfuscater import encrypt
import library.timezones as timezones


class public_commands(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    
    @commands.command(aliases = ["Myactivity","MyActivity", "ma", "MA"])
    async def myactivity(self, context, private="True"):
        ''' Print out your current discord online activity. (see the data for the last 10 days)
            The second argument denotes whether you want the bot to dm you the activity graph or 
            post it in the server chat. '''
        user_name = str(context.message.author).split("#")[0]
        hashed_user_id = encrypt(context.message.author.id)
        user_tz = fetch_timezone(hashed_user_id)

        lista = fetch_schedule(hashed_user_id, user_tz)
        adjusted_lista = timezones.adjust_schedule_timezone(lista, user_tz)
        produce_user_graph(adjusted_lista, hashed_user_id, user_name, user_tz)
        
        if private == "False" or private == "false":
            image_message = await context.send(file=discordFILE(f"./graph_folder/UserAct_{hashed_user_id}.png"))
            emoji = "\N{THUMBS UP SIGN}"
            
            try:
                await context.message.add_reaction(emoji) # React with success
                # Delete the image 1min, 30 seconds after sending it to prevent clogging up space
                await asyncioSLEEP(90)
                await image_message.delete()
            except Exception as _:
                # User has deleted their own message before bot can react to it.
                # Or the image has already been deleted, do nothing.
                pass
        else:
            # DM the user with the image, no need to delete the image.
            image_message = await context.message.author.send(file=discordFILE(f"./graph_folder/UserAct_{hashed_user_id}.png"))
            emoji = "\N{THUMBS UP SIGN}"
            try:
                await context.message.add_reaction(emoji) # React with success
            except Exception as _:
                # User has deleted their own message before bot can react to it.
                pass


    @commands.command(aliases = ["Serveractivity", "serverActivity", "ServerActivity", "sa", "SA"])
    async def serveractivity(self, context, tz="UTC"):
        ''' Print a bar graph displaying how many people on average (in the span of a week) are online at various hours. 
            The second argument is a valid timezone to display the correct day and times for any region. '''
        if isinstance(context.message.author, discordUser):
            # this is a DM and the command is invalid
            await context.send("This command should only be invoked in a server, not in a DM with the bot.")
            emoji = "\N{THUMBS DOWN SIGN}"
            try:
                await context.message.add_reaction(emoji)
            except Exception as _:
                # User has deleted their own message before bot can react to it.
                pass
        else:
            if tz in timezones.valid_timezones:
                guild_hash = hash(context.message.author.guild)
                guild_name = str(context.message.guild.name)
                days_data_recorded = online_freq[guild_hash]["DAYS"]
                adjusted_freq_graph = timezones.adjust_server_frequency_timezone(online_freq[guild_hash]["FREQ"], tz)

                produce_server_graph(adjusted_freq_graph, guild_name, guild_hash, days_data_recorded, tz) # Get the respective freq graph for the server
                image_message = await context.send(file=discordFILE(f"./graph_folder/GuildAct_{guild_hash}.png"))
                emoji = "\N{THUMBS UP SIGN}"
                try:
                    await context.message.add_reaction(emoji) # React with success
                    # Delete the image 1min, 30 seconds after sending it to prevent clogging up space
                    await asyncioSLEEP(90)
                    await image_message.delete()
                except Exception as _:
                    # User has deleted their own message before bot can react to it.
                    # Or, the image has already been deleted, do nothing.
                    pass
            else:
                await context.send("Invalid timezone. Say =tz for valid timezones.")
                emoji = "\N{THUMBS DOWN SIGN}"
                try:
                    await context.message.add_reaction(emoji)
                except Exception as _:
                    # User has deleted their own message before bot can react to it.
                    pass


    @commands.command(aliases = ["GetTimeZone", "GetTZ", "Gettz", "gettz"])
    async def gettimezone(self, context):
        ''' See what is your personal timezone (the bot will direct message you)'''
        user_tz = fetch_timezone(encrypt(context.message.author.id))
        await context.message.author.send(f"Your timezone is currently: {user_tz}\n")


    @commands.command(aliases = ["SetTimeZone", "SetTZ", "Settz", "settz"])
    async def settimezone(self, context, tz="UTC"):
        ''' Set your personal timezone for "myactivity" command. If you don't know what timezone
            to set as, you can try saying: "=timezones" to check all valid timezones. '''
        emoji = "\N{THUMBS UP SIGN}"
        if tz in timezones.valid_timezones:
            replace_timezone(encrypt(context.message.author.id), tz)
        else:
            await context.send("Invalid timezone. Say =tz for valid timezones.")
            emoji = "\N{THUMBS DOWN SIGN}"
        await context.message.add_reaction(emoji)


    @commands.command(aliases = ["Timezones", "timeZones", "TimeZones", "TZ", "tz"])
    async def timezones(self, context, option="main"):
        ''' Display a list of all of the valid timezones for the "myactivity" and "serveractivity" command.
            The second argument is "main" so you can list all of the main timezones, or the name of any regional continent. '''
        message_sent = ""
        if option == "main":
            message_sent = "Universal timezones:\n| "+timezones.universalTimeZoneFormatted+"\nContinents (Say =tz {continent name} for more specific timezones):\n"
            message_sent += "| "+timezones.continentsFormatted+"\n"
        elif option in timezones.mainTimeZonesClean:
            message_sent = f"{option} Timezones:\n| "+(", ".join([item for item in timezones.common_timezones_set if item.split("/",1)[0] == option])).rstrip(", ")
        else:
            message_sent = "Invalid option/continent"
        await context.send(message_sent)


def setup(client):
    client.add_cog(public_commands(client))