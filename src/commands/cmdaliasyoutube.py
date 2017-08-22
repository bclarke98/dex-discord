import src.commands.cmdyoutube as cmdyoutube
from src.commands.basecmd import *

class CommandAliasYoutube(Command):
    def __init__(self):
        super().__init__('ayt', 'creates a command shortcut for the provided youtube link', args=['name', 'link'], permission=0)

    async def on_exec(self, data):
        try:
            data['cmds'][data['args'][0]]
            await send_message('Error: Command already exists', data)
        except Exception as ex:
            data['cmds'][data['args'][0]] = cmdyoutube.CommandYoutube(data['args'][0], data['args'][1])
            await send_message('Created command: "%s"' % data['args'][0], data)
        return await super().on_exec(data)
