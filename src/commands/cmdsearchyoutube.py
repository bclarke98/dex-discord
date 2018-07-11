import youtube_dl
from src.commands.basecmd import *

class CommandSearchYoutube(Command):
    def __init__(self):
        super().__init__('syt', 'plays youtube video from search query', args=['search query'], permission=0)

    async def on_exec(self, data):
        await reset_audio(data)
        try:
            if data['author'].voice.voice_channel:
                data['voice'] = await data['bot'].join_voice_channel(data['author'].voice.voice_channel)
                url = youtube_dl.YoutubeDL().extract_info('ytsearch:' + '+'.join(data['args']), download=False)['entries'][0]['webpage_url']
                data['player'] = await data['voice'].create_ytdl_player(url)
                data['player'].start()
                await send_message('Playing youtube video: ' + url, data, -1)
            else:
                await send_message('You must be in a voice channel to use this command.', data)
        except Exception as ex:
            print(ex)
            await reset_audio(data)
        return await super().on_exec(data)
