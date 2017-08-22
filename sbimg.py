#!/usr/bin/env python3
import sys
import random
import string
import textwrap
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

def spongebob(s):
    return ''.join([s[i].lower() if i % 2 == 0 else s[i].upper() for i in range(len(s))])

def spongebob_sentence(s):
    r, i = '', 0
    for c in s:
        r, i = r + c.lower() if i % 2 == 0 else r + c.upper(), i if c == ' ' else i + 1
    return r
        

img = Image.open('sb.png')
draw = ImageDraw.Draw(img)
f = ImageFont.truetype('/usr/share/fonts/truetype/ubuntu-font-family/Ubuntu-B.ttf', 72, encoding='unic')

def draw_text(s, x, y, fill, stroke=2):
    for line in textwrap.wrap(s, width=32)[::-1]:
        coords = [(x+stroke,y+stroke), (x-stroke,y+stroke), (x+stroke,y-stroke),(x-stroke,y-stroke), (x,y)]
        for i in range(len(coords)):
            p = coords[i]
            draw.text((p[0] - f.getsize(line)[0] / 2, p[1]), line, font=f, fill=fill if i + 1 == len(coords) else '#000000')
        y -= f.getsize(line)[1]


text = spongebob_sentence(' '.join(sys.argv[1:]))
draw_text(text, 768, 1430, '#ffffff', 4)

loc = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6)) + '.png'
img.save('/var/www/html/spongebob/' + loc)
print('home.d3x.me/spongebob/' + loc)

