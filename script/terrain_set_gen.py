
import turtle as t
import os
from PIL import Image

BLOCK_SIZE = 32
COLORS = ['white', 'red', 'orange', 'yellow', 'green', 'blue', 'pink', 'purple']
TOTAL_KIND = len(COLORS)

screen = t.getscreen()
screen.screensize(BLOCK_SIZE * TOTAL_KIND, BLOCK_SIZE)
screen.canvwidth = BLOCK_SIZE * TOTAL_KIND
screen.canvheight = BLOCK_SIZE
t.speed(0)

origin_x, origin_y = -BLOCK_SIZE * TOTAL_KIND / 2, -BLOCK_SIZE / 2
t.hideturtle()

for i in range(TOTAL_KIND):
    t.penup()
    t.fillcolor(COLORS[i])
    t.goto(BLOCK_SIZE * i + origin_x, BLOCK_SIZE + origin_y)
    t.begin_fill()
    for edge in range(4):
        t.forward(BLOCK_SIZE)
        t.right(90)
    t.end_fill()

t.getcanvas().postscript(file="block.eps")

with open("block.eps", 'rb') as f:
    img = Image.open(f)
    img.save('block.png')
os.remove("block.eps")
t.bye()
