from src.commands.basecmd import *

class CommandClean(Command):
    def __init__(self):
        super().__init__('clean', 'cleans commands and bot responses from chat', permission=2)

    async def on_exec(self, data):
        lim = 10 if len(data['args']) == 0 else int(data['args'][0])
        async for msg in data['bot'].logs_from(data['channel'], limit=lim):
            if 'dex-bot' in str(msg.author):
                try:
                    await data['bot'].delete_message(msg)
                except:
                    pass  # prevents crashes if the message was already deleted
        await send_message('Cleaned bot messages from past %d messages.' % lim, data, 5)
        return await super().on_exec(data)

