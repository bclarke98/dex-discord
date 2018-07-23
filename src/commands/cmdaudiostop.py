from src.commands.basecmd import *

class CommandAudioStop(Command):
    def __init__(self):
        super().__init__('ar', 'disconnects bot voice', permission=0)

    async def on_exec(self, data):
        data['audioembed'].paused = True
        await reset_audio(data)
        return await super().on_exec(data)

