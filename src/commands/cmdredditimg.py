import discord
from src.commands.basecmd import *

class CommandRedditImage(Command):
    def __init__(self):
        super().__init__('ri', 'pulls an image from the provided subreddit', args=['subreddit'])

    async def on_exec(self, data):
        try:
            redditdata = data['reddit'].get_sub_image_data(data['args'][0])
            em = discord.Embed(title='Random image from r/' + data['args'][0] + ' for ' + data['author'].name, description=data['reddit'].get_title(redditdata), color=int(0xcc00cc))
            em.set_image(url=data['reddit'].get_image_url(redditdata))
            em.set_footer(text=data['reddit'].get_thread_url(redditdata))
            await data['bot'].send_message(data['channel'], embed=em)
        except Exception as ex:
            print(ex)
            await send_message('Error getting reddit image.', data)
        return await super().on_exec(data)
