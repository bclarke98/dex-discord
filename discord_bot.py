#!/usr/bin/env python3
import sys
import check
if check.check_bot_on():
    print('Bot already running!')
    sys.exit()

import discord
import asyncio
import praw
import random
import datetime
import operator
import youtube_dl
import os

PROCESS_ID = str(os.getpid())
with open('pid.txt', 'w') as pidw:
    pidw.write(PROCESS_ID)

VERSION = '1.2.1'
BOT_TOKEN, REDDIT_CID, REDDIT_CS, REDDIT_PW = '', '', '', ''
with open('logins.dat', 'r') as lr:
    BOT_TOKEN, REDDIT_CID, REDDIT_CS, REDDIT_PW = lr.read().strip().split('\n')

CMD_PREFIX = '.'
dex_bot = discord.Client()
audio_playing = None
bot_voice = None
 
can_interact = True
HEARTBEAT_INTERVAL = 1
uptime = 0

logdata = 'Initialized at: [' + str(datetime.datetime.utcnow())[:-7] + ' (UTC)]\n'

lastyoutubelink = ''

async def send_msg(s, duration, msg):
    m = await dex_bot.send_message(msg.channel, s)
    await asyncio.sleep(duration)
    await dex_bot.delete_message(m)


def get_uptime_str():
    return 'Days: ' + str(uptime // 1440) + '  Hours: ' + str((uptime // 60) % 24) + '  Minutes: ' + str(int(uptime % 60)) + '  Seconds: ' + str(int(uptime * 60) % 60)

async def update_details():
    with open('details.dat', 'w') as dw:
        dw.write('Version|%s\n' % VERSION)
        dw.write('Uptime|%s\n' % get_uptime_str())
        dw.write('Audio|%s' % lastyoutubelink)

class RedditBot:
    def __init__(self, subreddit):
        self.subreddit = subreddit
        self.reddit = None
        self.submissions = None
        self.images = []
        self.update()

    def update(self):
        self.reddit = praw.Reddit(client_id=REDDIT_CID, client_secret=REDDIT_CS, user_agent='dex-bot by /u/overlysalty', username='d3x-bot', password=REDDIT_PW)
        self.submissions = self.reddit.subreddit(self.subreddit).hot(limit=50)
        self.images = [[s.url, s.id, s.title] for s in self.submissions if ('.jpg' in s.url or '.png' in s.url)]

    def img_with_sub(self):
        r = random.randint(0, len(self.images) - 1)
        return str(self.images[r][0]), str('www.reddit.com/r/' + self.subreddit + '/comments/' + str(self.images[r][1])), '"' + str(self.images[r][2]) + '"'

    def get_random_image(self, sublink=True):
        return self.img_with_sub() if sublink else str(self.images[random.randint(0, len(self.images) - 1)][0])


reddit_bots = {
    'dankmemes': RedditBot('dankmemes'),
    'imgoingtohellforthis': RedditBot('imgoingtohellforthis')
}


def get_reddit_bot(s):
    global reddit_bots
    if s not in reddit_bots:
        reddit_bots[s] = RedditBot(s)
    return reddit_bots[s]

data_entries = []


class DataEntry:
    def __init__(self, args):
        self.name = args[0]
        self.msg_count = 0
        self.cmd_count = 0
        if len(args) > 1:
            self.msg_count = int(args[1])
        if len(args) > 2:
            self.cmd_count = int(args[2])
        self.ls = [self.name, self.msg_count, self.cmd_count]

    def update(self):
        self.ls = [self.name, self.msg_count, self.cmd_count]


def get_data_entry(s):
    for d in data_entries:
        if s in d.name or d.name in s:
            return d
    return None


directory_str = os.getcwd().replace('\\', '/') + '/data'
if not os.path.exists(directory_str):
    os.makedirs(directory_str)
datafile = open('data/stats.dat')
contents = datafile.readlines()
for i in range(len(contents)):
    if len(contents[i]) > 1:
        data_entries.append(DataEntry(contents[i].rstrip().split(';')))
datafile.close()


async def save_logs():
    global logdata
    logfile = open('data/logs.dat', 'a')
    logfile.write(logdata)
    logfile.close()
    logdata = ''


audio_queue = []  #stores songs to play

class Command:
    def __init__(self, name, description, method, permissions=None, args=-1, params=''):
        self.name, self.description, self.method, self.permissions, self.args, self.params = name, description, method, permissions, args, params

    def help(self):
        return '- ' + CMD_PREFIX + self.name + self.params + ' - ' + self.description

    async def execute(self, message):
        if not can_interact:
            for r in message.author.roles:
                if 'admin' in r.name:
                    break
            else:
                await dex_bot.send_message(message.author, 'Shhh. I\'m in monitoring mode and cannot respond. Contact an admin to disable monitoring mode.')
                return False
        if self.args != -1 and len(message.content.split(' ')[1:]) != self.args:
            await dex_bot.send_message(message.channel, '[Error]: Invalid parameters. Usage: "' + self.help() + '"')
            return False
        else:
            if self.permissions is not None:
                for r in message.author.roles:
                    if self.permissions in r.name:
                        break
                else:
                    await dex_bot.send_message(message.channel, '[Error]: You don\'t have permission to use this command')
                    return False
            await self.method(message)
            return True

    def __str__(self):
        return self.name

cmds = []


async def get_voice_channel(message):
    ch = None
    for c in message.channel.server.channels:
        for n in c.voice_members:
            if str(c.type) == 'voice' and message.author.name.lower() in n.name.lower():
                ch = c
    if not ch:
        await dex_bot.send_message(message.channel, '[Error]: You must be in a voice channel to use this command')
    return ch


async def cmd_help(message):
    s = ''
    for c in cmds:
        s += c.help() + '\n'
    await dex_bot.send_message(message.channel, s)


async def cmd_echo(message):
    s = ''
    for i in message.content.split(' ')[1:]:
        s += i + ' '
    if len(s) > 0:
        await dex_bot.send_message(message.channel, s)


async def cmd_debug(message):
    print('Version: %s' % VERSION)
    print('Sender Name: ' + str(message.author))
    print('Server ID: ' + str(message.author.server.id))
    print('Channel ID: ' + str(message.channel.id))
    server = message.channel.server.id
    print(server.members)
    print(server.channels)


def cmd_names_within(s):
    for c in cmds:
        if '.' + c.name in s:
            return True
    return False


async def cmd_clean(message):
    args = message.content.split(' ')[1:]
    lim = 10 if len(args) != 1 else int(args[0])
    async for msg in dex_bot.logs_from(message.channel, limit=lim):
        if 'dex-bot' in str(msg.author) or cmd_names_within(msg.content):
            await dex_bot.delete_message(msg)
    m = await dex_bot.send_message(message.channel, 'Cleaned commands and bot responses from the past ' + str(lim) + ' messages.')
    await asyncio.sleep(3)
    await dex_bot.delete_message(m)


async def cmd_wipe(message):
    args = message.content.split(' ')[1:]
    lim = 1 if len(args) != 1 else int(args[0])
    async for msg in dex_bot.logs_from(message.channel, limit=lim):
        await dex_bot.delete_message(msg)
    m = await dex_bot.send_message(message.channel, 'Removed the past ' + str(lim) + ' messages.')
    await asyncio.sleep(3)
    await dex_bot.delete_message(m)


async def cmd_toucan(message):
    await dex_bot.send_message(message.channel, '░░░░░░░░▄▄▄▀▀▀▄▄███▄░░░░░░░░░░░░░░'
                                            + '\n░░░░░▄▀▀░░░░░░░▐░▀██▌░░░░░░░░░░░░░'
                                            + '\n░░░▄▀░░░░▄▄███░▌▀▀░▀█░░░░░░░░░░░░░'
                                            + '\n░░▄█░░▄▀▀▒▒▒▒▒▄▐░░░░█▌░░░░░░░░░░░░'
                                            + '\n░▐█▀▄▀▄▄▄▄▀▀▀▀▌░░░░░▐█▄░░░░░░░░░░░'
                                            + '\n░▌▄▄▀▀░░░░░░░░▌░░░░▄███████▄░░░░░░'
                                            + '\n░░░░░░░░░░░░░▐░░░░▐███████████▄░░░'
                                            + '\n░░░░░le░░░░░░░▐░░░░▐█████████████▄ '
                                            + '\n░░░░toucan░░░░░░▀▄░░░▐█████████████▄'
                                            + '\n░░░░░░has░░░░░░░░▀▄▄███████████████'
                                            + '\n░░░░░arrived░░░░░░░░░░░░█▀██████░░░░')


async def cmd_speak(message):
    await dex_bot.delete_message(message)
    s = ''
    for i in message.content.split(' ')[1:]:
        s += i + ' '
    m = await dex_bot.send_message(message.channel, s, tts=True)
    await dex_bot.delete_message(m)


async def cmd_invite(message):
    inv = await dex_bot.create_invite(discord.Server(id='168735910559481856'), max_age=10)
    await dex_bot.send_message(message.channel, inv)


async def cmd_jail(message):
    args = message.content.split(' ')[1:]
    ogchannel = None
    for u in message.channel.server.members:
        if args[0].lower() in u.name.lower():
            user = u
            break
        for c in message.channel.server.channels:
            for n in c.voice_members:
                if args[0].lower() in n.name.lower():
                    ogchannel = c
    else:
        await dex_bot.send_message(message.channel, '[Error]: User not found')
        return
    m = await dex_bot.send_message(message.channel, 'Jailing User "' + str(user.name) + '" for ' + args[1] + ' seconds')
    await dex_bot.move_member(user, dex_bot.get_channel('168739118875017217'))
    jailed = None
    for r in message.channel.server.roles:
        if r.name == '@jailed':
            jailed = r
    await dex_bot.add_roles(user, jailed)
    await asyncio.sleep(min(600, int(args[1])))
    try:
        await dex_bot.remove_roles(user, jailed)
        await dex_bot.move_member(user, ogchannel)
    except:
        pass
    await dex_bot.delete_message(m)


async def cmd_uptime(message):
    await dex_bot.send_message(message.channel, 'Uptime: [' + get_uptime_str() + ']')


async def cmd_listen(message):
    global can_interact
    can_interact = not can_interact
    m = await dex_bot.send_message(message.channel, ('Exiting' if can_interact else 'Entering') + ' monitoring mode.')
    await asyncio.sleep(5)
    await dex_bot.delete_message(m)


async def cmd_dankmeme(message):
    get_reddit_bot('dankmemes').update()
    meme = get_reddit_bot('dankmemes').get_random_image()
    em = discord.Embed(title='Meme for ' + message.author.name.split('#')[0], description=meme[2], color=int(0xcc00cc))
    em.set_image(url=meme[0])
    em.set_footer(text='Link:  ' + meme[1])
    await dex_bot.send_message(message.channel, embed=em)


async def cmd_stop(message):
    await dex_bot.send_message(message.channel, 'Shutting down...')
    await dex_bot.close()


async def cmd_nice(message):
    global audio_playing, bot_voice
    await cmd_audio_stop(message)
    channel = await get_voice_channel(message)
    if not channel:
        return
    try:
        bot_voice = await dex_bot.join_voice_channel(channel)
        audio_playing = await bot_voice.create_ytdl_player('https://www.youtube.com/watch?v=L8ZqSW5j-AQ')
        audio_playing.volume = 0.25
        audio_playing.start()
        await asyncio.sleep(audio_playing.duration)
        await bot_voice.disconnect()
    except:
        pass


async def cmd_surprise(message):
    global audio_playing, bot_voice
    await cmd_audio_stop(message)
    channel = await get_voice_channel(message)
    if not channel:
        return
    try:
        bot_voice = await dex_bot.join_voice_channel(channel)
        audio_playing = await bot_voice.create_ytdl_player('https://www.youtube.com/watch?v=DT2X5b0tyDI')
        audio_playing.volume = 2.0
        audio_playing.start()
        await asyncio.sleep(audio_playing.duration)
        audio_playing.volume = 0.25
        await bot_voice.disconnect()
    except:
        pass


async def cmd_edge(message):
    get_reddit_bot('imgoingtohellforthis').update()
    meme = get_reddit_bot('imgoingtohellforthis').get_random_image()
    em = discord.Embed(title='Edgy Meme for ' + message.author.name.split('#')[0], description=meme[2], color=int(0xcc00cc))
    em.set_image(url=meme[0])
    em.set_footer(text='Link:  ' + meme[1])
    await dex_bot.send_message(message.channel, embed=em)


async def cmd_youtube(message, directlink=''):
    global audio_playing, bot_voice
    await cmd_audio_stop(message)
    channel = await get_voice_channel(message)
    if not channel:
        return
    try:
        args = message.content.split(' ')[1:]
        bot_voice = await dex_bot.join_voice_channel(channel)
        directlink = args[0] if len(directlink) == 0 else directlink
        global lastyoutubelink
        lastyoutubelink = directlink
        m = await dex_bot.send_message(message.channel, 'Playing youtube video: ' + directlink)
        audio_playing = await bot_voice.create_ytdl_player(directlink)
        audio_playing.volume = 0.25
        await audio_playing.start()
        await asyncio.sleep(audio_playing.duration)
        await bot_voice.disconnect()
        await dex_bot.delete_message(m)
    except Exception as ex:
        print(ex)


def get_yt_link(search):
    global lastyoutubelink
    lastyoutubelink = youtube_dl.YoutubeDL().extract_info('ytsearch:' + search, download=False)['entries'][0]['webpage_url']
    return lastyoutubelink


async def cmd_searchyt(message):
    global audio_playing, bot_voice
    await cmd_audio_stop(message)
    channel = await get_voice_channel(message)
    if not channel:
        return
    try:
        args = message.content.split(' ')[1:]
        search_query = ''
        for i in range(len(args)):
            search_query += args[i] + ('' if i + 1 == len(args) else '+')
        bot_voice = await dex_bot.join_voice_channel(channel)
        m = await dex_bot.send_message(message.channel, 'Attempting to find youtube video from a search of "' + search_query + '"')
        link = get_yt_link(search_query)
        n = await dex_bot.send_message(message.channel, 'Playing Video: %s' % link)
        audio_playing = await bot_voice.create_ytdl_player(link)
        audio_playing.volume = 0.25
        await dex_bot.delete_message(m)
        await audio_playing.start()
        await asyncio.sleep(audio_playing.duration)
        await dex_bot.delete_message(n)
        await bot_voice.disconnect()
    except:
        pass


async def cmd_audio_stop(message):
    global audio_playing
    if audio_playing:
        audio_playing.stop()
        await bot_voice.disconnect()
    global lastyoutubelink
    lastyoutubelink = ''
    async for msg in dex_bot.logs_from(message.channel, limit=100):
        if 'dex-bot' in str(msg.author) and 'youtube' in str(message.content):
            await dex_bot.delete_message(msg)
    


async def cmd_succ(message):
    global audio_playing, bot_voice
    await cmd_audio_stop(message)
    channel = await get_voice_channel(message)
    if not channel:
        return
    try:
        bot_voice = await dex_bot.join_voice_channel(channel)
        audio_playing = await bot_voice.create_ytdl_player('https://www.youtube.com/watch?v=RLHjpdH6YZk')
        audio_playing.volume = 0.25
        audio_playing.start()
        await asyncio.sleep(audio_playing.duration)
        await bot_voice.disconnect()
    except:
        pass


async def cmd_reddit_search(message):
    args = message.content.split(' ')[1:]
    get_reddit_bot(args[0]).update()
    meme = get_reddit_bot(args[0]).get_random_image()
    em = discord.Embed(title='Random Image from r/' + args[0] + ' for ' + message.author.name.split('#')[0], description=meme[2], color=int(0xcc00cc))
    em.set_image(url=meme[0])
    em.set_footer(text='Link:  ' + meme[1])
    await dex_bot.send_message(message.channel, embed=em)


async def cmd_userstats(message):
    d = get_data_entry(message.author.name)
    await dex_bot.send_message(message.channel, '[%s]:\nMessages Sent: %d\nCommands Sent: %d' % (message.author.name, d.msg_count, d.cmd_count))

async def cmd_jail_shawn(message):
    arg = 'swordrush14'
    ogchannel = None
    for u in message.channel.server.members:
        if arg in u.name.lower():
            user = u
            break
        for c in message.channel.server.channels:
            for n in c.voice_members:
                if arg in n.name.lower():
                    ogchannel = c
    else:
        await dex_bot.send_message(message.channel, '[Error]: User not found')
        return
    m = await dex_bot.send_message(message.channel, 'Jailing User "' + str(user.name) + '" for 30 seconds')
    await dex_bot.move_member(user, dex_bot.get_channel('277258808621924352'))
    jailed = None
    for r in message.channel.server.roles:
        if r.name == '@jailed':
            jailed = r
    await dex_bot.add_roles(user, jailed)
    await asyncio.sleep(30)
    try:
        await dex_bot.remove_roles(user, jailed)
        await dex_bot.move_member(user, ogchannel)
    except:
        pass
    await dex_bot.delete_message(m)

async def cmd_queue(message):
    global audio_queue
    args = message.content.lower().split(' ')[1:]
    if '-s' in args and len(audio_queue) < 10:
        arr = [i for i in args if '-s' not in i]
        query = ''.join(arr)
        link = get_yt_link(query)
        audio_queue.append(link)
        await dex_bot.send_message(message.channel, '[%s] - Queue Position [%d]' % (link, len(audio_queue)))
        if len(audio_queue) == 1:
            await cmd_youtube(message, directline=audio_queue[0])
    elif len(audio_queue) < 10:
        audio_queue.append(args[0])
        await dex_bot.send_message(message.channel, '[%s] - Queue Position [%d]' % (args[0], len(audio_queue)))
        if len(audio_queue) == 1:
            await cmd_youtube(message, directline=audio_queue[0])
    else:
        m = await dex_bot.send_message(message.channel, 'Queue is currently full. Type ".next" to play the next song in the queue.')
        await asyncio.sleep(5)
        await dex_bot.delete_message(m)


async def cmd_next_queue(message):
    global audio_queue
    if len(audio_queue) > 0:
        await cmd_youtube(message, directlink=audio_queue[0])
        audio_queue.pop(0)
    else:
        m = await dex_bot.send_message(message.channel, 'Queue is empty. Type ".queue -s [search query]" or ".queue [link]" to queue a message')
        await asyncio.sleep(5)
        await dex_bot.delete_message(m)

async def cmd_rocky(message):
    global audio_playing, bot_voice
    await cmd_audio_stop(message)
    channel = await get_voice_channel(message)
    if not channel:
        return
    try:
        bot_voice = await dex_bot.join_voice_channel(channel)
        audio_playing = await bot_voice.create_ytdl_player('https://www.youtube.com/watch?v=I33u_EHLI3w')
        audio_playing.volume = 0.25
        audio_playing.start()
        await asyncio.sleep(audio_playing.duration)
        audio_playing.volume = 0.25
        await bot_voice.disconnect()
    except:
        pass


@dex_bot.event
async def on_ready():
    cmds.append(Command('help', 'prints information on all commands', cmd_help))
    cmds.append(Command('echo', 'echos back the provided text', cmd_echo))
    cmds.append(Command('debug', 'prints debug information to the bot stdout', cmd_debug, permissions='admin'))
    cmds.append(Command('clean', 'cleans commands and bot responses from server', cmd_clean, permissions='salty'))
    cmds.append(Command('wipe', 'removes the specified amount of messages from the server', cmd_wipe, permissions='admin'))
    cmds.append(Command('speak', 'speaks the provided text', cmd_speak, permissions='admin'))
    cmds.append(Command('hush', 'toggles monitoring mode', cmd_listen, permissions='admin'))
    cmds.append(Command('close', 'shuts down the bot', cmd_stop, permissions='admin'))
    cmds.append(Command('toucan', 'le toucan has arrived', cmd_toucan))
    cmds.append(Command('uptime', 'displays how long the bot\'s been running', cmd_uptime))
    cmds.append(Command('invite', 'creates invite link', cmd_invite))
    cmds.append(Command('meme', '[NSFW] satisfies your meme needs', cmd_dankmeme))
    cmds.append(Command('edge', '[NSFW] 2edgy4u', cmd_edge))
    cmds.append(Command('nice', 'praises the quality of your dankest meme', cmd_nice))
    cmds.append(Command('surprise', 'surprise', cmd_surprise))
    cmds.append(Command('jail', 'temporarily jails the specified user', cmd_jail, args=2, params=' [username] [duration]', permissions='admin'))
    cmds.append(Command('yt', 'plays youtube video from the provided link', cmd_youtube, args=1, params=' [link]'))
    cmds.append(Command('syt', 'plays first youtube video found from provided search query', cmd_searchyt))
    cmds.append(Command('ar', 'resets the audio status of the bot', cmd_audio_stop))
    cmds.append(Command('succ', 'a tribute to joey', cmd_succ))
    cmds.append(Command('reddit-img', 'pulls random image from the top 50 posts of the provided subreddit', cmd_reddit_search, args=1, params=' [subreddit name]'))
    cmds.append(Command('stats', 'prints your user statistics', cmd_userstats))
    cmds.append(Command('sjail', 'shortcut to jailing', cmd_jail_shawn, permissions='admin'))
    cmds.append(Command('queue', 'adds youtube video to queue', cmd_queue, params=' [-s {search query} (optional)]'))
    cmds.append(Command('rocky', 'dun dun na naaaaaaaaaaaaaaa', cmd_rocky))
    cmds.append(Command('next', 'plays the next song in the queue', cmd_next_queue))
    cmds.sort(key=operator.attrgetter('name'))
    print('[Loading]: Success')
    print('[Version]: %s' % VERSION)
    print('[Logged in as]: ' + str(dex_bot.user.name))
    m = await dex_bot.send_message(discord.Object(id='168735910559481856'), 'Beep Boop.')
    await asyncio.sleep(5)
    try:
        await dex_bot.delete_message(m)
    except:
        pass


def utc_to_est():
    utcn = str(datetime.datetime.utcnow())[11:-7]
    hr = int(utcn[:2])
    hr = hr - 4 if (hr - 4 >= 0) else 24 + (hr - 4)
    return str(hr) + utcn[2:]


@dex_bot.event
async def on_message(message):
    global logdata
    if get_data_entry(str(message.author)):
        get_data_entry(str(message.author)).msg_count += 1
    elif 'dex-bot' not in str(message.author):
        data_entries.append(DataEntry([str(message.author)]))
        print('Created data entry for "' + str(message.author) + '"')
    if 'dex-bot' not in str(message.author):
        logdata += '[' + utc_to_est() + ']' + '[' + message.author.name + ']' + message.content + '\n' 
    if 'dex-bot' not in str(message.author) and message.content.startswith(CMD_PREFIX):
        try:
            await asyncio.sleep(1)
            await dex_bot.delete_message(message)
        except:
            pass
        get_data_entry(str(message.author)).cmd_count += 1
        for c in cmds:
#            if message.content.lower()[1:].startswith(c.name):
            if message.content.lower()[1:].split(' ')[0] == c.name:
                try:
                    await c.execute(message)
                except:
                    pass
                break
        else:
            if can_interact:
                await dex_bot.send_message(message.channel, '[Error]: Unknown Command "' + message.content + '"')
            else:
                for r in message.author.roles:
                    if 'admin' in r.name:
                        await dex_bot.send_message(message.channel, '[Error]: Unknown Command "' + message.content + '"')
                        break
                else:
                    await dex_bot.send_message(message.author, 'Shhh. I\'m in monitoring mode and cannot respond. Contact an admin to disable monitoring mode.')

async def saveuserdata():
    f = open('data/stats.dat', 'w+')
    for d in data_entries:
        d.update()
        s = ''
        for n in range(len(d.ls)):
            s += str(d.ls[n]) + (';' if n + 1 < len(d.ls) else '')
        f.write(s + '\n')
    f.close()


async def on_heartbeat():
    global uptime, bot_voice, audio_playing
    await dex_bot.wait_until_ready()
    while not dex_bot.is_closed:
        # try:
        #     if bot_voice and bot_voice.is_connected() and not audio_playing.is_playing():
        #         await bot_voice.disconnect()
        # except:
        #     pass
        uptime += HEARTBEAT_INTERVAL / 60.0
        if uptime % 30 == 0:
            await saveuserdata()
            await save_logs()
        await update_details()
        await asyncio.sleep(HEARTBEAT_INTERVAL)

dex_bot.loop.create_task(on_heartbeat())
dex_bot.run(BOT_TOKEN)

# https://praw.readthedocs.io/en/latest/code_overview/models/subreddit.html#praw.models.Subreddit
# http://discordpy.readthedocs.io/en/latest/api.html#
# http://discordpy.readthedocs.io/en/latest/api.html#voice
# https://discordapp.com/oauth2/authorize?client_id=298508884413513729&scope=bot&permissions=0

