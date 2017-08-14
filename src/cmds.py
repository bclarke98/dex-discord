import asyncio
from abc import ABC, abstractmethod


async def send_message(s, channel, client, duration=3):
    m = await client.send_message(channel, s)
    await asyncio.sleep(duration)
    await client.delete_message(m)


class Command(ABC):
    def __init__(self, name, desc, args=[], permission=0):
        self.name = name
        self.desc = desc
        self.args = args
        self.permission = permission

    @abstractmethod
    async def on_exec(self, data):
        pass


class CommandTest(Command):
    def __init__(self):
        super().__init__('test', 'test command')
    
    async def on_exec(self, data):
        await super().on_exec(data)
        await send_message('Test command worked', data['channel'], data['bot'])


class CommandClean(Command):
    def __init__(self):
        super().__init__('clean', 'cleans commands and bot responses from chat', permission=2)

    async def on_exec(self, data):
        await super().on_exec(data)
        lim = 10 if len(data['args']) == 0 else int(data['args'][0])
        async for msg in data['bot'].logs_from(data['channel'], limit=lim):
            if 'dex-bot' in str(msg.author):
                try:
                    await data['bot'].delete_message(msg)
                except:
                    pass  # prevents crashes if the message was already deleted
        await send_message('Cleaned bot messages from past %d messages.' % lim, data['channel'], data['bot'], 5)
        

 
class CommandHandler(object):
    def __init__(self, prefix):
        self.permissions = [
            [], # default, should remain empty
            [], # donator/special user
            [], # moderator
            []  # administrator
        ]
        try:
            with open('data/permissions.dat') as pr:
                for ln in pr.read().strip().split('\n'):
                    self.permissions[int(ln.split(':')[1])].append(ln.split(':')[0].lower())
        except IOError as ex:
            print('data/permissions.dat not found')
        except IndexError as iex:
            print('Permission rank out of range.')
            print('[1]: Special User')
            print('[2]: Moderator')
            print('[3]: Administrator')
        self.prefix = prefix
        self.bot_voice = None
        self.cmds = {
            'test':CommandTest(),
            'clean':CommandClean()
        }
 
    async def cant_exec(self, client, message):
        if message.content[0] == self.prefix:
            await client.delete_message(message)
            content = message.content[1:].lower()
            try:
                cmd = self.cmds[content.split(' ')[0]]
                args = [] if len(content.split(' ')) == 1 else content.split(' ')[1:]
                if len(args) < len(cmd.args):
                    return 'Wrong amount of parameters.'
                data = {
                    'msg':message,
                    'author':message.author,
                    'channel':message.channel,
                    'args':args,
                    'bot':client,
                    'voice':self.bot_voice
                }
                upermission = 0
                for r in data['author'].roles:
                    for i in range(3, 0, -1):
                        if r.name.lower() in self.permissions[i]:
                            upermission = i
                            break
                if upermission >= cmd.permission:
                    await cmd.on_exec(data)
                    return False # no issues running command
                return 'Permission Denied.'
            except KeyError as err:
                if 'help' in content.split(' ')[0]:
                    for n in self.cmds:
                        c = self.cmds[n]
                        s = '- %s%s ' % (self.prefix, c.name)
                        for a in c.args:
                            s += '[%s] ' % a
                        s += ' - ' + c.desc
                        await client.send_message(message.channel, s)
                    return False
                return 'Command not found.'



