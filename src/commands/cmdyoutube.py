from src.commands.basecmd import *

class CommandYoutube(Command):
    def __init__(self, name='yt', link=None):
        super().__init__(name, 'shortcut for playing youtube video' if link else 'plays linked youtube video', args=[] if link else ['link'], permission=0)
        self.link = link

    async def on_exec(self, data):
        await reset_audio(data)
        try:
            if data['author'].voice.voice_channel:
                data['voice'] = await data['bot'].join_voice_channel(data['author'].voice.voice_channel)
                data['player'] = await data['voice'].create_ytdl_player(self.link if self.link else data['args'][0])
                data['player'].start()
            else:
                await send_message('You must be in a voice channel to use this command.', data)
        except Exception as ex:
            print(ex)
            await reset_audio(data)
        return await super().on_exec(data)
