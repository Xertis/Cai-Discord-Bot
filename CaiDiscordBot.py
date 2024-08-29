import discord
import random
from characterai import aiocai
from discord.ext import commands
import difflib

#conf

DATA = {
    "AA": {
        "char": "CHAR",
        "cai_chat": "CHAT",
        "discord_chat": "DCHAT"
    },
    "BB": {
        "char": "CHAR",
        "cai_chat": "CHAT",
        "discord_chat": "DCHAT"
    },
    "CC": {
        "char": "CHAR",
        "cai_chat": "CHAT",
        "discord_chat": "DCHAT"
    },
}

DEFAULT = {"char": "CHAR",
           "cai_chat": "CHAT"}

DIS_TOKEN = "TOKEN"
CAI_TOKEN = "TOKEN"
DIS_PREFIX = ">>"
TARGET_WORDS = ['A', 'B', 'C', 'A', 'B', 'C', 'A', 'B', 'C', 'A']
MAX_MESSAGES = 15

##############################

client = aiocai.Client(CAI_TOKEN)

intents = discord.Intents().all()
intents.message_content = True

All_servers = {}

async def CheckMessage(text):
    words_to_censor = set(TARGET_WORDS)
    
    async def is_banned(word):
        for banned_word in words_to_censor:
            if difflib.SequenceMatcher(None, word.lower(), banned_word.lower()).ratio() > 0.8:
                return True
        return False

    censored_string = []
    for word in text.split():
        if await is_banned(word):
            word_check = list(word)
            word_check.pop(0)
            random.shuffle(word_check)
            censored_string.append(''.join(word_check))
        else:
            censored_string.append(word)

    return ' '.join(censored_string)
    
#Cai Start
async def Cai(message_user, server, user_name):
    if message_user == '' and message_user == ' ':
        message_user = "Image"
    try:
        message_user = await CheckMessage(message_user)
        
        char = ''
        chat_id = ''
        if server in DATA.keys():
            char = DATA[server]["char"]
            chat_id = DATA[server]["cai_chat"]
        else:
            char = DEFAULT["char"]
            chat_id = DEFAULT["cai_chat"]
        
        text = ''
        if user_name != False:
            text = f"[{user_name}] {message_user}"
        else:
            text = message_user

        async with await client.connect() as chat:

            message = await chat.send_message(
                char, chat_id, text
            )
            out = message.text
            print(out, 'CAI RESULT')
            if '@' in out:
                out = out.split('@')
                out = '||@||'.join(out)
            out = await CheckMessage(out)
            return out

    except Exception as e:
        print(e)

#Discord Start
bot = commands.Bot(command_prefix=DIS_PREFIX, intents = intents)

async def pre_cai(ctx, server_name1, text1, MesID):
    ctx.message.id = MesID
    print('pre_cai is ONLINE')
    await ctx.message.reply(await Cai(text1, server_name1, False))

@bot.event
async def on_message(message):
    global All_servers

    server_name = message.guild.name
    channel = message.channel.id
    if server_name not in DATA.keys():
        print(server_name, 'не находится в списке серверов')
        await bot.process_commands(message)
    elif message.author != bot.user:
        if message.content.startswith(DIS_PREFIX):
            await bot.process_commands(message)
        else:
            if DATA[server_name]["discord_chat"] == str(channel):
                text = message.content
                user_name = message.author
                complete_message = f"[{user_name}] {text}"
                if server_name not in All_servers.keys():
                    All_servers[server_name] = complete_message
                else:
                    A_ssn = All_servers[server_name]
                    All_servers[server_name] = A_ssn + '\n' + complete_message
                A_ssn2 = str(All_servers[server_name])
                print(A_ssn2)
                if A_ssn2.count('\n') >= MAX_MESSAGES:
                    MesID = message.id
                    ctx = await bot.get_context(message)
                    del All_servers[server_name]
                    print(All_servers.keys())
                    await pre_cai(ctx, server_name, A_ssn2, MesID)
        
@bot.command()
async def server(ctx):
    server_name = ctx.guild.name
    await ctx.message.reply(server_name)

@bot.command()
async def send(ctx, *, message):
    server_name = ctx.guild.name
    user_name = ctx.author.name
    try:
        await ctx.message.reply(await Cai(message, server_name, user_name))
    except Exception as e:
        print(e)

bot.run(DIS_TOKEN)
