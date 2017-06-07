## IMPORTS

import asyncio, aiohttp, discord, logging, random, sys, time
from mcstatus import MinecraftServer
from functools import wraps

## LOGGING

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

## COMMAND CLASSES

class Command():
    def __init__(self, fn, **kwargs):
        self.fn = fn
        self.kwargs = kwargs
        
    async def run(self, *args):
        await self.fn(*args, **self.kwargs)

class ChatCommand(Command):
    # location:
    # 0 - start of message
    # 1 - complete message
    # 2 - end of message
    # 3 - anywhere in message
    def __init__(self, keyword, location, fn, auth=0, denyReply=None, **kwargs):
        self.keyword = keyword
        if location < 0 or location > 3:
            raise ValueError('Location value must be between 0 and 3.')
        self.location = location
        self.auth = auth
        self.denyReply = denyReply
        super().__init__(fn, **kwargs)
        
    def matches(self, content):
        if   self.location == 0:
            return content.startswith(self.keyword)
        elif self.location == 1:
            return content == self.keyword
        elif self.location == 2:
            return content.endswith(self.keyword)
        else:
            return (content.find(self.keyword) >= 0)
            
class CommandList():
    def __init__(self):
        self.commands = set()   
             
    def add(self, command): # MUST NOT BE RUN IN CLIENT FUNCTIONS
        self.commands.add(command)
        
    async def getCommands(self):
        for command in self.commands:
            yield command
        
            
class ChatCommandList():
    def __init__(self, authRecords=dict()):
        self.commands = dict()
        self.authRecords = authRecords
        
    def add(self, command): # MUST NOT BE RUN IN CLIENT FUNCTIONS
        self.commands[command.keyword] = command
        
    async def containsCommands(self, content):
        for key in self.commands:
            if self.commands[key].matches(content.lower()):
                yield self.commands[key]
        
        

## PRE-INITIALIZATION

# Load authentication records
authRecords = dict()
authRecords[73007938238676992] = 5 # I am always an admin
onMessage = ChatCommandList(authRecords)
onMemberUpdate = CommandList()
client = discord.Client()

serverMain = MinecraftServer.lookup("127.0.0.1")
serverAlt = MinecraftServer.lookup("127.0.0.1:25566")

## CLIENT EVENTS

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    await client.change_presence(game=discord.Game(name="15-122"))
    
@client.event
async def on_message(message):
    authLevel = onMessage.authRecords[message.author.id] = onMessage.authRecords.get(int(message.author.id), 0)
    async for command in onMessage.containsCommands(message.content):
        if command.auth > authLevel:
            if command.denyReply != None:
                await client.send_message(message.channel, str(command.denyReply))
        else:
            await command.run(client, message)
            
@client.event
async def on_member_update(before, after):
    async for command in onMemberUpdate.getCommands():
        await command.run(before, after)
        
## COMMANDS
    
async def changeGame(client, message):
    words = message.content.split(' ')
    gameName = None
    if len(words) > 1:
        gameName = ' '.join(words[1:])
    await client.change_presence(game=discord.Game(name=gameName))
        
async def flipCoin(client, message):
    words = message.content.split()
    try:
        if len(words) == 1: raise Exception()
        count = int(words[1])
        if count < 2: raise Exception()
        stats = [0, 0]
        count = min(100000000, count)
        for i in range(count):
            stats[random.randint(0, 1)] += 1
        highest = ('', '')
        if stats[0] > stats[1]:
            highest = ('**', '*')
        elif stats[1] > stats[0]:
            highest = ('*', '**')
        em = discord.Embed(title='Heads: {0}{2}{0} | Tails: {1}{3}{1}'.format(*highest, *stats), colour=0x066BFB)
        await client.send_message(message.channel, embed=em)
    except:
        if len(words) == 2 and words[1] == 'me': return
        roll = 'Heads!' if random.randint(0, 1) else 'Tails!'
        em = discord.Embed(title=roll, colour=0x066BFB)
        await client.send_message(message.channel, embed=em)
    
async def rollRNG(client, message):
    try:
        words = message.content.split()
        diceRoll = (0, 0)
        if words[1][0] == 'd':
            diceRoll = (1, int(words[1][1:]))
        else:
            bounds = words[1].split(',')
            if len(bounds) < 2:
                bounds.add(words[2])
            elif bounds[1] == '':
                bounds[1] = words[2]
            diceRoll = (int(bounds[0]), int(bounds[1]))
        roll = random.randint(*diceRoll)
        em = discord.Embed(title='You rolled a {}!'.format(roll), colour=0x066BFB)
        await client.send_message(message.channel, embed=em)
    except:
        em = discord.Embed(title='Bad syntax!', colour=0x066BFB)
        await client.send_message(message.channel, embed=em)
        
async def serverStatus(client, message, **servers):
    words = message.content.split()
    mainResponse = ''
    try:
        status = servers['main'].status()
        playerCount = status.players.online
        playerWord = '' if playerCount == 1 else 's'
        players = ''
        playerNames = []
        if status.players.sample:
            for player in status.players.sample:
                playerNames.append(player.name)
            players = " [{}]".format(str(playerNames)[1:-1])
        desc = status.description['text']
        mainResponse = 'Main Server: {} player{} online{}, "{}"'.format(playerCount, playerWord, players, desc)
    except:
            mainResponse = 'Could not contact main server!'
    altResponse = ''
    try:
        status = servers['alt'].status()
        playerCount = status.players.online
        playerWord = '' if playerCount == 1 else 's'
        players = ''
        playerNames = []
        if status.players.sample:
            for player in status.players.sample:
                playerNames.append(player.name)
            players = " [{}]".format(str(playerNames)[1:-1]).replace("'", "")
        desc = status.description['text']
        altResponse = 'Alt. Server: {} player{} online{}, "{}"'.format(playerCount, playerWord, players, desc)
    except:
        altResponse = 'Could not contact alternate server!'
    currentTime = time.strftime('%B %d at %I:%M %p')
    em = discord.Embed(title=currentTime, description='{}\n{}'.format(mainResponse, altResponse), colour=0x066BFB)
    await client.send_message(message.channel, embed=em)
    
async def rpMute(client, message):
    author = message.author
    server = message.server
    seconds = 15
    muteRole = None
    muteChannel = None
    for role in server.roles:
        if str(role) == 'Muted':
            muteRole = role
            break
    for channel in server.channels:
        if str(channel) == 'muted':
            muteChannel = channel
            break
    if not muteRole or not muteChannel: return
    await client.add_roles(author, muteRole)
    await asyncio.sleep(3)
    await client.send_message(muteChannel, '{} has been muted for {} seconds.'.format(author.name, seconds))
    await asyncio.sleep(seconds-1)
    await client.remove_roles(author, muteRole)
    
async def sendPoyo(client, message):
    tmp = await client.send_message(message.channel, 'https://i.imgur.com/72Whn87.png')
    asyncio.sleep(120)
    await client.delete_message(tmp)


## INITIALIZATION

token=''
with open('token.txt', 'r') as tokenFile:
    token=tokenFile.readLine()

game = ChatCommand('!game', 0, changeGame, auth=3)
roll = ChatCommand('!roll', 0, rollRNG)
flip = ChatCommand('!flip', 0, flipCoin)
status = ChatCommand('!status', 0, serverStatus, main=serverMain, alt=serverAlt)
mute = ChatCommand('!flip me', 0, rpMute)
poyo = ChatCommand('poyo', 0, sendPoyo)



onMessage.add(game)
onMessage.add(roll)
onMessage.add(flip)
onMessage.add(status)
onMessage.add(mute)
onMessage.add(poyo)

def run():
    client.run(token)
    
if __name__ == '__main__':
    run()
    