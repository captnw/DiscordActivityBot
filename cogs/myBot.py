from discord.ext import commands
import time

client = commands.Bot(command_prefix="!")
extensions = ["cogs.fun_commands"]
for ext in extensions:
    client.load_extension(ext)
client.run("NzM4MTM1NTE0ODUwNTI1MzM3.XyHgRA.4nQ2q7_IqeKMKm_STOlhyJLV9pU")