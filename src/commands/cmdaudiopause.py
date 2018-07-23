import youtube_dl
from src.commands.basecmd import *

class CommandAudioPause(Command):
    def __init__(self):
        super().__init__('pause', 'pauses audio', args=[], permission=0)

    async def on_exec(self, data):
        try:
            if data['author'].voice.voice_channel:
                if data['player'] and data['player'].is_playing():
                    data['player'].pause()
                    data['audioembed'].paused = True
                await send_message('Audio Paused.', data, -1)
            else:
                await send_message('You must be in a voice channel to use this command.', data)
        except Exception as ex:
            print(ex)
            await reset_audio(data)
        return await super().on_exec(data)
