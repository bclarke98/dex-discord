from src.commands.basecmd import *

class CommandFreeze(Command):
    def __init__(self):
        super().__init__('freeze', 'third grader nightmare fuel', permission=0)

    async def on_exec(self, data):
        link = 'https://cdn.discordapp.com/attachments/125062545064067072/348674401409040405/Ice_barrage_sound.mp3'
        await reset_audio(data)
        if data['author'].voice.voice_channel:
            data['voice'] = await data['bot'].join_voice_channel(data['author'].voice.voice_channel)
            data['player'] = data['voice'].create_ffmpeg_player('res/barrage.mp3')
            data['player'].start()
        else:
            await send_message('You must be in a voice channel to use this command.', data)
        return await super().on_exec(data)

 
