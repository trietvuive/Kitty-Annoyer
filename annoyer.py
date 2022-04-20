import discord
import os
import requests
import json
import random
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option
from statistics import median, pstdev

client = discord.Client(intents=discord.Intents.all())
slash = SlashCommand(client, sync_commands=True)
prefix_words = {'bum': ['bum'],
                 'nerd': ['nerd'],
                 'potato': ['potato'],
                 'noob': ['noob', 'nu']}

TOKEN = os.getenv('TOKEN')
kitty_id = os.getenv('KITTY_ID')
tenor_api_key = os.getenv('TENOR_API_KEY')
n = 5000
stop_bullying = True
SERVER_ID = os.getenv('SERVER_ID')

MEOW_PATH = 'data/meow_balance.txt'
first_date_questions = open('questions/first_date.txt').read().split('\n')

# get cat pic from tenor API
def get_cat_pic():
    response = requests.get('https://api.thecatapi.com/v1/images/search')
    json_data = json.loads(response.text)
    url = json_data[0]['url']
    return url

# get gif from tenor API
def get_gif(query):
    response = requests.get('https://g.tenor.com/v1/random?q={0}&key={1}'.format(query, tenor_api_key))
    json_data = json.loads(response.text)
    url = json_data['results'][0]['media'][0]['gif']['url']
    return url

# return random capitalization of a message
def random_capitalization(message):
    return ''.join(choice((str.upper, str.lower))(c) for c in message)

# get response time in last N messages and print it

async def get_response_data(channel):
    responses_time = dict()
    last_author = None
    last_datetime = None
    first_datetime = None
    async for message in channel.history(limit=n, oldest_first = True):
        nick, time = message.author.name, message.created_at
        if last_author is not None and last_author is not nick:
            if nick not in responses_time:
                responses_time[nick] = []
            responses_time[nick].append((time - last_datetime).total_seconds())

        if first_datetime is None:
            first_datetime = time
        last_author = nick
        last_datetime = time
    await message.channel.send("For the last {0} messages".format(n))
    total_seconds = (last_datetime - first_datetime).total_seconds()
    await message.channel.send("For channel {0}, Average of {1} messages per minute".format(channel.name, n/total_seconds*60)) 
    for k,v in responses_time.items():
        await message.channel.send("Author: {0}, Median Response Time: {1}, Stdev {2}".format(k, median(v), pstdev(v)))


# count word frequency in last N messages
async def get_history_of_channel(channel):
    counter = dict()
    async for message in channel.history(limit=n):
        name = message.author.display_name
        for keyword, prefix in prefix_words.items():
            detected = False
            for s in prefix:
                if s in message.content:
                    detected = True
                    break
            if detected:
                counter[(name, keyword)] = counter.get((name, keyword), 0) + 1
    return counter

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Game('Bullying Kitty'))

guild_ids = [SERVER_ID] # Server ID

@slash.slash(name="gif",
             guild_ids = guild_ids,
             description="Get random gif",
             options=[
               create_option(
                 name="message",
                 description="Specify the gif you're trying to find",
                 option_type=3,
                 required=False
               )
             ])
async def slash_gif(ctx, message):
    await ctx.send(get_gif(message))

def read_file():
    try:
        myfile = open(MEOW_PATH)
    except:
        return 0
    return int(myfile.read())

def write_file(balance):
    with open(MEOW_PATH, 'w') as myfile:
        myfile.write(str(balance))

@slash.slash(name="increase",
             guild_ids = guild_ids,
             description="Increase meow balance",
             options=[
               create_option(
                 name="balance",
                 description="Specify the increase of meow",
                 option_type=3,
                 required=False
               )
             ])
async def increase_meow(ctx, balance):
    balance = int(balance)
    if balance > 10:
        await ctx.send("That's kinda large...")
        return
    meow_balance = read_file()
    meow_balance += balance
    write_file(meow_balance)
    await ctx.send("Increased by {0} meows! Current meow balance is {1}".format(
                    balance, meow_balance))

@slash.slash(name="decrease",
             guild_ids = guild_ids,
             description="Decrease meow balance",
             options=[
               create_option(
                 name="balance",
                 description="Specify the decrease of meow",
                 option_type=3,
                 required=False
               )
             ])
async def decrease_meow(ctx, balance):
    balance = int(balance)
    if balance > 10:
        await ctx.send("That's kinda large...")
        return
    meow_balance = read_file()
    meow_balance -= balance
    await ctx.send("Decreased by {0} meows! Current meow balance is {1}".format(
                    balance, meow_balance))
    write_file(meow_balance)




@slash.slash(name="questions",
             guild_ids = guild_ids,
             description="Get a fun questions!")
async def slash_gif(ctx):
    await ctx.send(random.choice(first_date_questions))

@slash.slash(name="meow",
             guild_ids = guild_ids,
             description="Meow!")
async def meow(ctx):
    await ctx.send(get_gif("meow"))

@slash.slash(name="pout",
             guild_ids = guild_ids,
             description="HMPH!")
async def pout(ctx):
    await ctx.send(get_gif("pout anime"))

@slash.slash(name="ihy",
             guild_ids = guild_ids,
             description="Say ihy!")
async def slash_gif(ctx):
    if ctx.author.name == 'Kitty':
        await ctx.send("IHYYYYY Tree!")
    else:
        await ctx.send("IHYYYYY Kitty!")

@slash.slash(name="bum",
             guild_ids = guild_ids,
             description="Say ur a bum!")
async def slash_gif(ctx):
    if ctx.author.name == 'Kitty':
        await ctx.send("Ur a bum Tree!")
    else:
        await ctx.send("Ur a bum Kitty!")

@slash.slash(name="poke",
             guild_ids = guild_ids,
             description="Poke!")
async def slash_gif(ctx):
    await ctx.send(get_gif("poke anime"))
    
@client.event
async def on_message(message):
    global stop_bullying

    print(message.content)
    
    if message.author == client.user:
        return

    if 'hello' in message.content.lower():
        await message.channel.send('Hello!')

    if 'cat pic' in message.content.lower():
        await message.channel.send(get_cat_pic())

    if 'cat gif' in message.content.lower():
        await message.channel.send(get_gif('cat'))
        
    if 'good bot' in message.content.lower():
        await message.channel.send(get_gif('pat happy anime'))
        
    if 'bad bot' in message.content.lower():
        await message.channel.send(get_gif('cry anime'))

    # send star gif
    if any(item in message.content.lower().split() for item in ['sunset', 'aurora', 'star', 'stars']):
        await message.channel.send(get_gif(message.content))

    # count frequency of words in last N messages
    if message.content == 'kowalski, analysis':
        channel = message.channel
        history = await get_history_of_channel(channel)
        await message.channel.send('From the last {0} messages:'.format(n))
        for key, value in sorted(history.items()):
            await message.channel.send('{0} said {1} {2} times'.format(key[0], key[1], value))

    # analysis to get last N messages's response time
    if message.content == "analysis":
        await get_response_data(message.channel)
        
    if message.content.lower().startswith('stop bullying'):
        await message.channel.send('Ight no more bullying')
        stop_bullying = True
        
    if message.content.lower().startswith('start bullying'):
        await message.channel.send('Bully Kitty time!!')
        stop_bullying = False

    if not stop_bullying:
        # random capitalization to mock Kitty
        if 'leave' in message.content and message.author.name == 'Kitty':
            await message.channel.send(random_capitalization(message.content))


        # Tell her she's a bum, nerd, nub,...
        for keyword, prefix in prefix_words.items():
            detected = False
            for s in prefix:
                if s in message.content.lower():
                    detected = True
                    break
            if detected:
                await message.channel.send('%s, you\'re a %s' % (kitty_id, keyword))
        
def main():
    client.run(TOKEN)

if __name__ == "__main__":
    main()
