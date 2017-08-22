from src.commands.basecmd import *

import sys
import random
import string
import textwrap

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

def spongebob(s):
    r, i = '', 0
    for c in s:
        r, i = r + c.lower() if i % 2 == 0 else r + c.upper(), i if c == ' ' else i + 1
    return r


class CommandSpongebob(Command):
    def __init__(self):
        super().__init__('sponge', 'tHiS cOmMaNd iS sElF eXpLaNiToRy', permission=0)

    async def on_exec(self, data):
        img = Image.open('res/sb.png')
        draw = ImageDraw.Draw(img)
        f = ImageFont.truetype('/usr/share/fonts/truetype/ubuntu-font-family/Ubuntu-B.ttf', 72, encoding='unic')
        x, y, fill, stroke = 768, 1430, '#ffffff', 4
        for line in textwrap.wrap(spongebob(' '.join(data['args'])), width=32)[::-1]:
            coords = [(x+stroke,y+stroke), (x-stroke,y+stroke), (x+stroke,y-stroke),(x-stroke,y-stroke), (x,y)]
            for i in range(len(coords)):
                p = coords[i]
                draw.text((p[0] - f.getsize(line)[0] / 2, p[1]), line, font=f, fill=fill if i + 1 == len(coords) else '#000000')
            y -= f.getsize(line)[1]
        loc = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6)) + '.png'
        img.save('/var/www/html/spongebob/' + loc)
        await send_message('http://home.d3x.me/spongebob/%s' % loc, data, -1)
        return await super().on_exec(data)


