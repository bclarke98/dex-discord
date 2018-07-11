from src.commands.basecmd import *

class CommandTest(Command):
    def __init__(self):
        super().__init__('test', 'test command')

    async def on_exec(self, data):
        await send_message('Test command worked', data)
        return await super().on_exec(data)


