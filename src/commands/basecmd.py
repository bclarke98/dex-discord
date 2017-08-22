import asyncio
import datetime
import src.empty as empty
from abc import ABC, abstractmethod

async def send_message(s, data, duration=3):
    m = await data['bot'].send_message(data['channel'], s)
    if duration > 0:
        try:
            await asyncio.sleep(duration)
            await data['bot'].delete_message(m)
        except:
            pass

async def reset_audio(data):
    try:
        data['player'].stop()
        await data['voice'].disconnect()
    except:
        pass
    # data['player'], data['voice'] = empty.EmptyAudio, empty.EmptyAudio


def est_time():
    utcn = str(datetime.datetime.utcnow())[11:-7]
    hr = int(utcn[:2])
    hr = hr - 4 if (hr - 4 >= 0) else 24 + (hr - 4)
    return str(hr) + utcn[2:]


class CommandLog(object):
    def __init__(self, user):
        self.user = user
        self.commands = []  # self.commands = [ [timestamp, command] ]
        
    def __str__(self):
        return self.user + ': \n\t' + '\n\t'.join([str(i) for i in self.commands])

class Command(ABC):
    def __init__(self, name, desc, args=[], permission=0):
        self.name = name
        self.desc = desc
        self.args = args
        self.permission = permission
        self.log = {}

    @abstractmethod
    async def on_exec(self, data, log=False):
        if log:
            try:
                self.log[str(data['author'])].commands.append([est_time(), data['msg'].content])
            except KeyError as ke:
                self.log[str(data['author'])] = CommandLog(str(data['author']))
                self.log[str(data['author'])].commands.append([est_time(), data['msg'].content])
        return data


