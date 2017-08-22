import src.empty as empty
from src.commands import *


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
        self.bot_voice = empty.EmptyAudio()
        self.audio_player = empty.EmptyAudio()
        self.cmds = {
            'test':cmdtest.CommandTest(),
            'clean':cmdclean.CommandClean(),
            'wipe':cmdwipe.CommandWipe(),
            'sponge':cmdspongebob.CommandSpongebob(),
            'freeze':cmdfreeze.CommandFreeze(),
            'ar':cmdaudiostop.CommandAudioStop(),
            'yt':cmdyoutube.CommandYoutube(),
            'syt':cmdsearchyoutube.CommandSearchYoutube(),
            'ri':cmdredditimg.CommandRedditImage(),
        }
 
    async def check_exec(self, client, reddit, message):
        if message.author.bot:
            return False
        if message.content[0] == self.prefix:
            await client.delete_message(message)
            content = message.content[1:]
            try:
                cmd = self.cmds[content.lower().split(' ')[0]]
                args = [] if len(content.split(' ')) == 1 else content.split(' ')[1:]
                if len(args) < len(cmd.args):
                    return 'Wrong amount of parameters.'
                data = {
                    'msg':message,
                    'author':message.author,
                    'channel':message.channel,
                    'args':args,
                    'bot':client,
                    'reddit':reddit,
                    'voice':self.bot_voice,
                    'player':self.audio_player
                }
                upermission = 0
                for r in data['author'].roles:
                    for i in range(3, 0, -1):
                        if r.name.lower() in self.permissions[i]:
                            upermission = i
                            break
                if upermission >= cmd.permission:
                    rdata = await cmd.on_exec(data)
                    self.bot_voice = rdata['voice']
                    self.audio_player = rdata['player']
                    return False # no issues running command
                return 'Permission Denied.'
            except KeyError as err:
                if 'help' in content.split(' ')[0]:
                    s = ''
                    for n in sorted(self.cmds):
                        c = self.cmds[n]
                        s += '- %s%s ' % (self.prefix, c.name)
                        for a in c.args:
                            s += '[%s] ' % a
                        s += ' - ' + c.desc + '\n'
                    await client.send_message(message.channel, s)
                    return False
                return 'Command not found.'

    async def on_heartbeat(self, uptime, interval):
        pass





