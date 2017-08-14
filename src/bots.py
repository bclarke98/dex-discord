import praw
import random
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


class DiscordBot(object):
    def __init__(self, details):
        self.token = details['btkn']
        self.client = details['client']
        self.chandler = cmds.CommandHandler('!')
    
    def start(self):
        self.client.loop.create_task(self.on_heartbeat())
        self.client.run(self.token)

    async def on_ready(self):
        print('READY!')

    async def on_message(self, message):
        flag = await self.chandler.cant_exec(self.client, message)
        if flag:
            await self.client.send_message(message.channel, flag)
    
    async def on_heartbeat(self):
        pass


