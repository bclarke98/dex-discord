#!/usr/bin/env python3
import sys
import check as check
if check.check_bot_on():
    print('Bot already running!')
    sys.exit()

import os
import discord
import src.bots as bots

VERSION = '1.0.2'

class DexManager:
    def __init__(self, client):
        self.details = {'client':client, 'version':VERSION}
        try:
            with open('data/logins.dat', 'r') as lr:
                self.details['btkn'], self.details['rcid'], self.details['rcs'], self.details['rpw'] = lr.read().strip().split('\n')
        except IOError as ex:
            print('"data/logins.dat" file not found. Please create one formatted as:')
            print('Discord Bot Token')
            print('Reddit Client ID')
            print('Reddit Client Secret')
            print('Reddit Password')
        self.details['pid'] = str(os.getpid())
        with open('pid.txt', 'w') as pidw:
            pidw.write(self.details['pid'])
        self.bot = bots.DiscordBot(self.details)
        

CLIENT = discord.Client()
manager = DexManager(CLIENT)

@CLIENT.event
async def on_ready():
    await manager.bot.on_ready()

@CLIENT.event
async def on_message(message):
    await manager.bot.on_message(message)

if __name__ == '__main__':
    manager.bot.start()


