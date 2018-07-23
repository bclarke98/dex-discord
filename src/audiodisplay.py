import discord

class QueueTrack(object):
    def __init__(self, link, title, msg, duration):
        self.link = link
        self.title = title
        self.msg = msg
        self.duration = duration
        self.embed = discord.Embed(color=int(0xcc00cc))
        self.timer = 0
    
    def is_done(self):
        return self.timer >= self.duration


class AudioDisplay(object):
    def __init__(self, client):
        self.client = client
        self.paused = True
        self.queue = []
    
    def current_song(self):
        return None if len(self.queue) == 0 else self.queue[0]
    
    async def reset(self, link, title, msg, duration):
        if len(self.queue) == 0:
            self.paused = False
        newtrack = QueueTrack(link, title, msg, duration)
        self.queue.append(newtrack)
        if self.current_song().is_done():
            await self.client.delete_message(self.current_song().msg)
            self.queue.pop(0)
            self.paused = False
        
    async def on_tick(self):
        if not self.paused and self.current_song():
            try:
                self.current_song().timer += 1
                self.current_song().embed.description = self.description_text()
                self.current_song().msg = await self.client.edit_message(self.current_song().msg, embed=self.current_song().embed)
            except:
                pass

    def format_time(self, n):
        s = ['0', '0', ':', '0', '0']
        s[0] = str((n // 600) % 10)
        s[1] = str((n // 60) % 10)
        s[3] = str((n % 60) // 10)
        s[4] = str((n % 60) % 10)
        return ''.join(s)

    def description_text(self):
        return 'Title: %s\nDuration: %s\nTimer: %s' % (self.current_song().title, self.format_time(self.current_song().duration), self.format_time(self.current_song().timer))
        
