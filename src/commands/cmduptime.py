from src.commands.basecmd import *

class CommandUptime(Command):
    def __init__(self):
        super().__init__('uptime', 'displays how long the bot has been running')

    async def on_exec(self, data):
        await send_message(uptime_str(data['uptime']), data)
        return await super().on_exec(data)


