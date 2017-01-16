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

def read_data(filepath, byte_count):
	text = read_file(filepath)

	data = [ ord(c) for c in text ]
	data = [ join_bytes(data[n:n+byte_count], byte_count) for n in range(0, len(data), byte_count) ]
	return data

def write_data(filepath, data, byte_count):
	data = sum([ split_bytes(n, byte_count) for n in data ], [])
	write_file(filepath, ''.join([ chr(c) for c in data ]))



def join_bytes(data, byte_count):
	result = 0
	for i in range(0, byte_count):
		result = (result << 8) | data[i]
	return result

def split_bytes(data, byte_count):
	return [ (data >> i * 8) & 0xff for i in range(byte_count - 1, -1, -1) ]


def rep_data(data, byte_count):
	return ('%0' + str(byte_count * 2) + 'X') % data



def display_byte(scr, data, index, byte_count, width):
	index_y = index / width
	index_x = index % width
	scr.addstr(index_y, index_x * (byte_count * 2 + 1), rep_data(data[index], byte_count) + ' ')

def display_bytes(scr, data, byte_count, width):
	line = 0
	for i in range(0, len(data)):
		display_byte(scr, data, i, byte_count, width)



def place_cursor(scr, cursor_index, byte_count, width):
	cursor_y = cursor_index / (byte_count * 2) / width
	cursor_x = cursor_index / (byte_count * 2) % width
	cursor_offset = cursor_index % (byte_count * 2)
	scr.addstr(cursor_y, cursor_x * (byte_count * 2 + 1) + cursor_offset, '')

def edit_byte(data, cursor_index, key, byte_count, scr):
	shift = (byte_count * 2) - 1 - cursor_index % (byte_count * 2)
	data_index = cursor_index / (byte_count * 2)
	scr.addstr(44, 0, 'debug: %d %d' % (shift, data_index))
	data[data_index] = (int(key, 16) << shift * 4) | (data[data_index] ^ (data[data_index] & (0xf << shift * 4)))
	#if cursor_index % 2 == 0:
		#data[cursor_index / 2] = (int(key, 16) << 4) | (data[cursor_index / 2] & 0xf)
	#else:
		#data[cursor_index / 2] = int(key, 16) | (data[cursor_index / 2] & 0xf0)

def bedit_main(scr):
	cursor_index = 0
	byte_count = 2
	width = 16
	scr.clear()

	if len(sys.argv) > 1:
		filepath = sys.argv[1]
		data = read_data(filepath, byte_count)
		scr.addstr(50, 1, 'read file: '+filepath)


	display_bytes(scr, data, byte_count, width)
	place_cursor(scr, cursor_index, byte_count, width)
	
	scr.refresh()
	k = scr.getkey()
	while k != 'q':
		if k == 'KEY_LEFT':
			if cursor_index > 0:
				cursor_index -= 1
		elif k == 'KEY_RIGHT':
			if cursor_index <= len(data) * byte_count * 2:
				cursor_index += 1
		elif k == 'KEY_UP':
			cursor_index -= width * byte_count * 2
			if cursor_index < 0:
				cursor_index = 0
		elif k == 'KEY_DOWN':
			cursor_index += width * byte_count * 2
			if cursor_index > len(data) * byte_count * 2:
				cursor_index = len(data) * byte_count * 2

		elif len(k) == 1 and ((k >= '0' and k <= '9') or (k >= 'a' and k <= 'f')):
			edit_byte(data, cursor_index, k, byte_count, scr)
			display_byte(scr, data, cursor_index / (byte_count * 2), byte_count, width)
			cursor_index += 1

		elif k == 'w':
			write_data(filepath, data, byte_count)
			scr.addstr(50, 1, 'wrote file: '+filepath)

		place_cursor(scr, cursor_index, byte_count, width)
		#scr.addstr(0, 0, '')

		scr.refresh()
		k = scr.getkey()

curses.wrapper(bedit_main)


