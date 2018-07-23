import praw
import random
import asyncio
import datetime
import src.cmds as cmds

class RedditBot(object):
    def __init__(self, details):
        self.reddit = praw.Reddit(client_id=details['rcid'], client_secret=details['rcs'], user_agent='dex-bot by /u/overlysalty', username='d3x-bot', password=details['rpw'])

        self.subreddits = {}    
    def get_sub_image_data(self, subreddit):
        try:
            self.subreddits[subreddit][0]
        except Exception as ex:  # if the subreddit hasn't been cached or is empty
            submissions = self.reddit.subreddit(subreddit).hot(limit=50)
            self.subreddits[subreddit] = [[subreddit, s.url, s.id, s.title] for s in submissions if ('.jpg' in s.url or '.png' in s.url)]
        r = random.randint(0, len(self.subreddits[subreddit]) - 1)
        return self.subreddits[subreddit].pop(r)
        
    def get_thread_url(self, data):
        return 'www.reddit.com/r/' + data[0] + '/comments/' + data[2]
    
    def get_title(self, data):
        return data[3]
    
    def get_image_url(self, data):
        return data[1]


class Log(object):
    def __init__(self):
        self.data = self.load_stats()
        self.chatlogs = []

    def load_stats(self):
        data = {}
        try:
            with open('data/stats.dat', 'r') as fr:
                for ln in fr.read().split('\n'):
                    spl = ln.strip().split(';')
                    if len(spl) == 3:
                        data[spl[0]] = [int(spl[1]), int(spl[2])] # [msgs, cmds]
        except IOError as ioe:
            print('"data/stats.dat" not found... creating new file.')
            with open('data/stats.dat', 'w') as fw:
                fw.write('')
        return data

    def update_stats(user, cmd=False):
        try:
            self.data[user][0] += 1
            self.data[user][1] += 1 if cmd else 0
        except KeyError as ke:
            self.data[user] = [1, 1 if cmd else 0]

    def save_stats(self):
        with open('data/stats.dat', 'w') as fw:
            for n in self.data:
                fw.write('%s;%d;%d\n' % (n, self.data[n][0], self.data[n][1]))

    def add_chat_log(self, message):
        self.chatlogs.append('[%s][%s]: %s' % (est_time(), message.author.name, message.content))

    def save_logs(self):
        with open('data/logs.dat', 'a') as fw:
            for l in self.chatlogs:
                fw.write('%s\n' % self.chatlogs.pop(0))



class DiscordBot(object):
    def __init__(self, details):
        self.version = details['version']
        self.token = details['btkn']
        self.client = details['client']
        self.chandler = cmds.CommandHandler('!', self.client)
        self.reddit = RedditBot(details)
        self.logger = Log()
        self.uptime = 0      # uptime in seconds
        self.interval = 1.0  # tick rate in seconds
    
    def start(self):
        self.client.loop.create_task(self.on_heartbeat())
        self.client.run(self.token)

    async def on_ready(self):
        print('READY!')
        msgs = []
        for s in self.client.servers:
            # msgs.append(await self.client.send_message(s.default_channel, "The superior second version of the D3X Discord Bot is online."))
            pass
        await asyncio.sleep(5)
        for m in msgs:
            await self.client.delete_message(m)

    async def on_message(self, message):
        if not message.author.bot:
            self.logger.add_chat_log(message)
        flag = await self.chandler.check_exec(self.client, self.reddit, message)
        if flag:
            await self.client.send_message(message.channel, flag)
    
    async def on_heartbeat(self):
        await self.client.wait_until_ready()
        while not self.client.is_closed:
            self.uptime += self.interval
            await self.chandler.on_heartbeat(self.uptime, self.interval, self.client)
            if int(self.uptime) % 30 == 0:
                self.logger.save_stats()
                self.logger.save_logs()
            self.save_details()
            await asyncio.sleep(self.interval)

    def save_details(self):
        with open('details.dat', 'w') as dw:
            dw.write('Version|%s\n' % self.version)
            dw.write('Uptime|%s' % uptime_str(self.uptime))


def est_time():
    utcn = str(datetime.datetime.utcnow())[11:-7]
    hr = int(utcn[:2])
    hr = hr - 4 if (hr - 4 >= 0) else 24 + (hr - 4)
    return str(hr) + utcn[2:]


def uptime_str(uptime):
    return 'Days: ' + str(int(uptime // 86400)) + '  Hours: ' + str(int(uptime // 3600) % 24) + '  Minutes: ' + str(int(uptime / 60) % 60) + '  Seconds: ' + str(int(uptime) % 60)
