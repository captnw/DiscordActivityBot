import discord

def beginPhrase(msg, listA: list) -> bool:
    ''' Helper function to check for alias, returns bool '''
    returnVal = False
    for alias in listA:
        returnVal = returnVal or msg.content.startswith(alias)
    return returnVal


class MyClient(discord.Client):
    async def on_ready(self):
        print("Logged in as")
        print(self.user.name)
        print(self.user.id)
        print('------')

    async def on_message(self, message):
        # we do not want the bot to reply to itself
        if message.author.id == self.user.id:
            return
        elif beginPhrase(message, ["!hello"]):
            await message.channel.send('Hello {0.author.mention}'.format(message))
        elif beginPhrase(message, ["!8ball","!Eightball","!8b"]):
            await message.channel.send("Gamer")
        elif beginPhrase(message, ["!m", "!members"]):
            channelMembers = ""    
            for member in message.channel.members:
                channelMembers += member.name + ", "
            await message.channel.send(f"{channelMembers} are in the channel")

        

client = MyClient()
client.run("NzM4MTM1NTE0ODUwNTI1MzM3.XyHgRA.4nQ2q7_IqeKMKm_STOlhyJLV9pU")