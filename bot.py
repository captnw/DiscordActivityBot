import discord
from csvfile_reader import *
import time

def begin_phrase(msg, listA: list) -> bool:
    ''' Helper function to check for alias, returns bool '''
    returnVal = False
    for alias in listA:
        returnVal = returnVal or msg.content.startswith(alias)
    return returnVal


class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        print("Logged in as")
        print(self.user.name)
        print(self.user.id)
        print('------')

        # csv_bootup()
        # time.sleep(20)
        # csv_shutdown()


    async def on_message(self, message):
        # we do not want the bot to reply to itself
        if message.author.id == self.user.id:
            return
        elif begin_phrase(message, ["!hello"]):
            await message.channel.send(f"Hello {message.author.mention}")
        elif begin_phrase(message, ["!8ball","!Eightball","!8b"]):
            await message.channel.send("Gamer")
        elif begin_phrase(message, ["!m", "!members"]):
            channel_members = ""    
            for member in message.channel.members:
                channel_members += member.name + ", "
                await message.channel.send(f"{member.name}'s status is {member.status}")
                await message.channel.send(f"{member.name}'s color is {member.color}")
                await message.channel.send(f"{member.name}'s role is {member.roles}")
            await message.channel.send(f"{channel_members} are in the channel")
        elif begin_phrase(message, ["!up"]):
            csv_bootup()
        elif begin_phrase(message, ["!down"]):
            csv_shutdown()
            
    
    async def on_message_delete(self, message):
        await message.channel.send(f"{message.author.name} tried to hide this message: {message.content}")

    async def on_member_update(self, before, after):
        print("A member's status has changed or something Idk")
        csv_write_into([after.name, after.status])
        print("Before: {}".format(big_struct))
        print("After: {}".format(big_struct))

    async def csv_manager(self):
        await self.wait_until_ready()
        csv_bootup()

        while not self.is_closed():
            # literally do nothing until it closes
            pass

        print("DisconnectedW")
        csv_shutdown()
        
if __name__ == "__main__":

    client = MyClient()
    client.run("NzM4MTM1NTE0ODUwNTI1MzM3.XyHgRA.4nQ2q7_IqeKMKm_STOlhyJLV9pU")
    # DO NOT ADD CODE AFTER THIS B/C client.run NEVER RETURNS