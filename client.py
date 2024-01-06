import socket, random, os, threading, logging, time
import numpy as np # idk, might need it
from PIL import Image, ImageDraw, ImageFont
import math

tc = 16 # thread count, 32 seems to work well but lower to like 8 if you want consistency

class Thr: # thread class with initializer and function
    def __init__(self):
         self._lock = threading.Lock() # im scared to take this out even though i dont need it anymore

    def sendlinesMulti(self, name, list):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # creates a socket for every thread TODO: dont do that
        # (if i dont do this, it becomes a race condition)
        s.connect(('pixelflut.uwu.industries', 1234))
        for line in list[name]:
            s.send(line.encode())
            # time.sleep(0.1) # time.sleep to simulate latency when testing on local server, remove before using

def chunks(lst, n): # this is like the only thing in this program that is written well
    output = list() # this creates a list where we will put the other lists
    for i in range(0, len(lst), n): # creates a range of numbers with step size equal to the length of The List divided by the number of threads
        output.append(lst[i:i + n]) # puts the chunks in the output list
    return output

mode = input("mode: ") # selects between different operation types
if  mode == "t": # text mode - generates text at specified size
    txt = input("text: ")
    size = int(input("size: "))
    font = ImageFont.truetype('C:\\Windows\\Fonts\\arial.ttf', size)
    img = Image.new('RGB', (0, 0), (255, 255, 255)) # placeholder so i can use textLength because this module is horrible
    draw = ImageDraw.Draw(img)
    tlength = draw.textlength(txt, font)
    img = Image.new('RGB', (round(tlength) + 20, size * 2), (255, 255, 255)) # create actual image to draw on
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), txt, fill=(0, 0, 0), font=font, align='center')
elif mode == "w": # wipe screen with black with specified size
    img = Image.new('RGB', ([int(elem) for elem in input("size: ").split()]), (0, 0, 0))
elif mode == "r":
    w, h = [int(elem) for elem in input("size: ").split()]
    img = Image.fromarray(np.random.randint(0,255,(h,w,3),dtype=np.dtype('uint8')))
else: # draw image and rescale to specified size
    filename = input("file: ")
    img = Image.open(filename)
    img = img.resize(map(int, input("size: ").split())) # I LOVE LIST COMPREHENSION!!!!

width, height = img.size

# s.send('SIZE\n'.encode()) 
# size = s.recv(10).decode()[5:].split()
# print(size)

xoff, yoff = map(int, input("offset: ").split()) # offset

lines = [] # The List

rotation = math.radians(float(input("rotation in degrees: ")))

for y in range(height):
    line = ''
    for x in range(width):
        rgb = img.getpixel((x, y)) # get color of pixel
        hexcolor = '%02x%02x%02x' % (rgb) # convert color to hex

        xp = x 
        yp = y 

            
        line += 'PX %d %d %s\n' % (int(round(x * round(math.cos(rotation), 1) - y * round(math.sin(rotation), 1) + xoff - tlength/2)), int(round(y * round(math.cos(rotation), 1) + x * round(math.sin(rotation), 1) + yoff - size*3/4)), hexcolor)

    lines.append(line) # add command to The List


lchunks = chunks(lines, len(lines) // tc) # divides The List into chunks (see function def for an explanation)

# random.shuffle(lines) # shuffle line randomly for funky effect

threads = list()
thr = Thr() # create instance of thread class

for i in range(tc):
    thread = threading.Thread(target=thr.sendlinesMulti, args=(i, lchunks)) # create threads to send commands
    threads.append(thread)
    thread.start()

# this can probably overload servers if the host doesnt have enough bandwidth
# womp womp
