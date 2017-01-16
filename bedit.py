#!/usr/bin/env python

import sys
import curses

def read_file(filepath):
	text = None
	with open(filepath, 'rb') as f:
		text = bytes(f.read())
	return text

def write_file(filepath, text):
	with open(filepath, 'wb') as f:
		f.write(text)




def rep_data(data):
	return "%02X" % data

def display_byte(scr, data, index, width=8):
	index_y = index / width
	index_x = index % width
	scr.addstr(index_y, index_x * 3, rep_data(data[index]) + ' ')

def display_bytes(scr, data, width=8):
	line = 0
	for i in range(0, len(data)):
		display_byte(scr, data, i, width)



def place_cursor(scr, cursor_index, width=8):
	cursor_y = cursor_index / 2 / width
	cursor_x = cursor_index / 2 % width
	cursor_offset = cursor_index % 2
	scr.addstr(cursor_y, cursor_x * 3 + cursor_offset, '')

def edit_byte(data, cursor_index, key):
	if cursor_index % 2 == 0:
		data[cursor_index / 2] = (int(key, 16) << 4) | (data[cursor_index / 2] & 0xf)
	else:
		data[cursor_index / 2] = int(key, 16) | (data[cursor_index / 2] & 0xf0)

def bedit_main(scr):
	cursor_index = 0
	width = 16
	scr.clear()

	if len(sys.argv) > 1:
		filepath = sys.argv[1]
		data = read_file(filepath)
		scr.addstr(50, 1, 'read file: '+filepath)
	
	data = [ ord(c) for c in data ]

	#scr.addstr(0, 0, str(data))

	display_bytes(scr, data, width)
	place_cursor(scr, cursor_index, width)
	
	scr.refresh()
	k = scr.getkey()
	while k != 'q':
		if k == 'KEY_LEFT':
			if cursor_index > 0:
				cursor_index -= 1
		elif k == 'KEY_RIGHT':
			if cursor_index <= len(data) * 2:
				cursor_index += 1
		elif k == 'KEY_UP':
			cursor_index -= width * 2
			if cursor_index < 0:
				cursor_index = 0
		elif k == 'KEY_DOWN':
			cursor_index += width * 2
			if cursor_index > len(data) * 2:
				cursor_index = len(data) * 2

		elif len(k) == 1 and ((k >= '0' and k <= '9') or (k >= 'a' and k <= 'f')):
			edit_byte(data, cursor_index, k)
			display_byte(scr, data, cursor_index / 2, width)
			cursor_index += 1

		elif k == 'w':
			write_file(filepath, ''.join([ chr(c) for c in data ]))
			scr.addstr(50, 1, 'wrote file: '+filepath)

		place_cursor(scr, cursor_index, width)
		#scr.addstr(0, 0, '')

		scr.refresh()
		k = scr.getkey()

curses.wrapper(bedit_main)


