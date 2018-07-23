import youtube_dl
from src.commands.basecmd import *

class CommandNext(Command):
    def __init__(self):
        super().__init__('next', 'skips to the next song in the queue', args=[], permission=0)

    async def on_exec(self, data):
        await reset_audio(data)
        try:
            if data['author'].voice.voice_channel:
                if len(data['audioembed'].queue) > 0:
                    await data['bot'].delete_message(data['audioembed'].current_song().msg)
                    data['audioembed'].queue.pop(0)
                if len(data['audioembed'].queue) == 0:
                    return
                data['voice'] = await data['bot'].join_voice_channel(data['author'].voice.voice_channel)
                data['player'] = await data['voice'].create_ytdl_player(data['audioembed'].current_song().link)
                data['player'].start()
                # await send_message('Playing youtube video: ' + url, data, -1)
                # if data['audioembed'].current_song():
                #    await data['bot'].send_message(data['channel'], data['audioembed'].current_song().msg)
            else:
                await send_message('You must be in a voice channel to use this command.', data)
        except Exception as ex:
            print(ex)
            await reset_audio(data)
        return await super().on_exec(data)
