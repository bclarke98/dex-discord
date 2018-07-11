from src.commands.basecmd import *

class CommandWipe(Command):
    def __init__(self):
        super().__init__('wipe', 'removes the specified amount of messages from chat', permission=2)

    async def on_exec(self, data):
        try:
            lim = 1 if len(data['args']) == 0 else int(data['args'][0])
            async for msg in data['bot'].logs_from(data['channel'], limit=lim):
                await data['bot'].delete_message(msg)
            await send_message('Removed %d message(s).' % lim, data)
        except:
            pass
        return await super().on_exec(data)

