import discord

def begin_phrase(msg, listA: list) -> bool:
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
        elif begin_phrase(message, ["!hello"]):
            await message.channel.send('Hello {0.author.mention}'.format(message))
        elif begin_phrase(message, ["!8ball","!Eightball","!8b"]):
            await message.channel.send("Gamer")
        elif begin_phrase(message, ["!m", "!members"]):
            #channel_members = ""    
            for member in message.channel.members:
                #channel_members += member.name + ", "
                await message.channel.send(f"{member.name}'s status is {member.status}")
                await message.channel.send(f"{member.name}'s color is {member.color}")
                await message.channel.send(f"{member.name}'s role is {member.roles}")
                
            #await message.channel.send(f"{channel_members} are in the channel")
    
    async def on_message_delete(self, message):
        await message.channel.send(f"{message.author.name} tried to delete this message: {message.content}")

        

client = MyClient()
client.run("NzM4MTM1NTE0ODUwNTI1MzM3.XyHgRA.4nQ2q7_IqeKMKm_STOlhyJLV9pU")