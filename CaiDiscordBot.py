import discord
import characterai
from characterai import PyCAI
from characterai import PyAsyncCAI
from discord.ext import commands
import difflib
import asyncio

#---confing

CaiToken = 'TOKEN'
DisToken = 'TOKEN'
DisPrefix = 'PREFIX'

#Dictionary with char characters bots, where keys are server names and values are char.
All_char = {'Server1': 'CHAR1', 
            'Server2': 'CHAR2'}

#Default char, enabled for servers that are not in All_char
Default_char = 'CHAR'

#A dictionary with Discord server names and their channels represented as IDs where the bot will communicate.
chats_servers = {'Server1': 'chat_id1', 
            'Server1': 'chat_id2'}

#The maximum packet size of messages, upon reaching which the bot will send messages to Characterai
Max_message = 5

#---end_config

All_servers = {}
intents = discord.Intents.default()
intents.message_content = True

#Cai Start
async def Cai(message_user, server, user_name):
    if message_user == '' or message_user == ' ':
        message_user = 'None'
    try:
        client = PyAsyncCAI(CaiToken)
        if server in All_char.keys():
            chat = await client.chat.get_chat(All_char[server])
        else:
            chat = await client.chat.get_chat(Default_char)

        participants = chat['participants']
        if not participants[0]['is_human']:
            tgt = participants[0]['user']['username']
        else:
            tgt = participants[1]['user']['username']

        if user_name != False:
            message = '[' + user_name + ']' + ' ' + message_user
        else:
            message = message_user
        data = await client.chat.send_message(
            chat['external_id'], tgt, message
        )

        text = data['replies'][0]['text']
        out = (f"{text}")

        print(out, 'CAI RESULT')

        #spoiler @
        if '@' in out:
            out = out.split('@')
            out = '||@||'.join(out)
        return out
    except Exception as e:
        print(e)

#Discord Start
bot = commands.Bot(command_prefix=DisPrefix, intents = intents)

async def pre_cai(ctx, server_name1, text1, MesID):
    ctx.message.id = MesID
    print('pre_cai part')
    await ctx.message.reply(await Cai(text1, server_name1, False))

@bot.event
async def on_message(message):
    global All_servers
    server_name = message.guild.name
    channel = message.channel.id
    if server_name not in chats_servers.keys():
        print(server_name, 'not in chats_servers')
        await bot.process_commands(message)
    elif message.author != bot.user:
        if message.content.startswith(DisPrefix):
            await bot.process_commands(message)
        else:
            if chats_servers[server_name] == str(channel):
                text = message.content
                user_name = message.author
                complete_message = '[' + str(user_name) + ']' + ' ' + text
                if server_name not in All_servers.keys():
                    All_servers[server_name] = complete_message
                else:
                    A_ssn = All_servers[server_name]
                    All_servers[server_name] = A_ssn + '\n' + complete_message
                A_ssn2 = str(All_servers[server_name])
                print(A_ssn2)
                if A_ssn2.count('\n') >= Max_message:
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

bot.run(DisToken)
