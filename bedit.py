#!/usr/bin/env python

import sys
import curses

def read_file(filepath):
	text = None
	with open(filepath, 'rb') as f:
		text = bytes(f.read())
	return text

def rep_data(data):
	return "%02X" % data

def display_bytes(scr, data, width=8):
	line = 0
	print 'debug:', data
	while line < len(data) / width and line < 40:
		for i in range(0, width):
			if line * width + i < len(data):
				print data[line * width + i]
				scr.addstr(line, i * 3, rep_data(data[line * width + i]) + ' ')
		line += 1




def bedit_main(scr):
	scr.clear()

	if len(sys.argv) > 1:
		data = read_file(sys.argv[1])
		scr.addstr(5, 0, 'read file: '+sys.argv[1])
	
	data = [ ord(c) for c in data ]

	#scr.addstr(0, 0, str(data))

	display_bytes(scr, data, 16)
	
	scr.refresh()
	k = scr.getkey()
	while k != 'q':
		#scr.addstr(0, 0, k)
		

		scr.addstr(0, 0, '')


		scr.refresh()
		k = scr.getkey()

curses.wrapper(bedit_main)


