import socket, random, os, threading, logging, time
import numpy as np # idk, might need it
from PIL import Image, ImageDraw, ImageFont
import math

tc = 1 # thread count, 32 seems to work well but lower to like 8 if you want consistency

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

tlength = 0
size = 0

mode = input("mode: ") # selects between different operation types
if  mode == "t": # text mode - generates text at specified size
	txt = input("text: ")
	size = int(input("size: "))
	font = ImageFont.truetype('Arial.ttf', size)
	img = Image.new('RGB', (0, 0), (255, 255, 255)) # placeholder so i can use textLength because this module is horrible
	draw = ImageDraw.Draw(img)
	tlength = draw.textlength(txt, font)
	img = Image.new('RGB', (round(tlength) + 20, size * 2), (255, 255, 255)) # create actual image to draw on
	draw = ImageDraw.Draw(img)
	draw.text((10, 10), txt, fill=(0, 0, 0), font=font, align='center')
	dosmode = input("dos mode? (y/n): ")
	width, height = img.size

	for y in range(height):
		for x in range(width):
			if img.getpixel((x, y)) == (255, 255, 255, 255):
				img.putpixel((x, y), (255, 255, 255, 0))
elif mode == "w": 
	img = Image.new('RGB', ([int(elem) for elem in input("size: ").split()]), (255, 255, 254))
	dosmode = input("dos mode? (y/n): ")
elif mode == "r":
	w, h = [int(elem) for elem in input("size: ").split()]
	img = Image.fromarray(np.random.randint(0,255,(h,w,3),dtype=np.dtype('uint8')))
else: # draw image and rescale to specified size
	filename = input("file: ")
	dosmode = input("dos mode? (y/n): ")
	img = Image.open(filename)
	img = img.resize(map(int, input("size: ").split())) # I LOVE LIST COMPREHENSION!!!!

def run(rotation):
	global height
	global width
	global xoff
	global yoff
	global lines
	global tlength

	for y in range(height):
		line = ''
		for x in range(width):
			rgb = img.getpixel((x, y)) # get color of pixel

			hexcolor = f'{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'  # convert color to hex

			xp = x - width/2
			yp = y - height/2

			if (rgb[0], rgb[1], rgb[2]) != (255, 255, 255): 
				line += f'PX {int(round(xp * round(math.cos(rotation), 2) - yp * round(math.sin(rotation), 2) + xoff))} {int(round(yp * round(math.cos(rotation), 2) + xp * round(math.sin(rotation), 2) + yoff))} {hexcolor}\n'

		lines.append(line) # add command to The List


	lchunks = chunks(lines, len(lines) // tc) # divides The List into chunks (see function def for an explanation)

	# random.shuffle(lines) # shuffle line randomly for funky effect

	threads = list()
	thr = Thr() # create instance of thread class

	for i in range(tc):
		thread = threading.Thread(target=thr.sendlinesMulti, args=(i, lchunks)) # create threads to send commands
		threads.append(thread)
		thread.start()

width, height = img.size

xoff, yoff = map(int, input("offset: ").split()) # offset

lines = [] # The List

if dosmode == "y":
	# this can probably overload servers if the host doesnt have enough bandwidth
	# womp womp
	for rotation in range(0, 271, 1):
		run(math.radians(rotation))
else:	
	rotation = math.radians(float(input("rotation in degrees: ")))
	run(rotation)
