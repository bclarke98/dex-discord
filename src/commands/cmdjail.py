import time
import discord
from src.commands.basecmd import *

async def get_jailed_role(data):
    role = None
    for r in data['server'].roles:
        if str(r) == '@jailed':
            role = r
            break
    else:
        role = await data['bot'].create_role(data['server'], name='@jailed')
    overrides = {}
    for i in data['server'].default_channel.overwrites_for(role):
        overrides[str(i[0])] = False
    rpo = discord.PermissionOverwrite(**overrides)
    for c in data['server'].channels:
        for o in c.overwrites:
            if o[0].name == '@jailed':
                break
        else:
            await data['bot'].edit_channel_permissions(c, role, rpo)
            print('Added @jailed override to channel: %s' % c.name)
    return role

class CommandJail(Command):
    def __init__(self):
        super().__init__('jail', 'locks user to AFK channel for specified duration in seconds', args=['user', 'duration'], permission=2)
        self.jailedrole = None

    async def on_exec(self, data):
        if not self.jailedrole:
            self.jailedrole = await get_jailed_role(data)
        uname = data['args'][0]
        juser = data['server'].get_member(uname[2:-1]) if uname[:2] == '<@' else data['server'].get_member_named(uname)
        if juser:
            if data['server'].afk_channel:
                await data['bot'].add_roles(juser, self.jailedrole)
                data['jail'][str(juser)] = [
                    int(data['args'][1]), 
                    time.time(),
                    juser.voice.voice_channel
                ]
                await data['bot'].move_member(juser, data['server'].afk_channel)
                await send_message('Jailing %s for %d seconds.' % (juser.name, int(data['args'][1])), data)
            else:
                await send_message('Server needs an AFK channel in order to use this command.', data)
        else:
            await send_message('No user found with name: %s' % str(data['args'][0]), data)
        return await super().on_exec(data)
