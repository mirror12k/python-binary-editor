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
	while len(data) < byte_count:
		data.append(0)
	result = 0
	for i in range(0, byte_count):
		result = (result << 8) | data[i]
	return result

def split_bytes(data, byte_count):
	return [ (data >> i * 8) & 0xff for i in range(byte_count - 1, -1, -1) ]


def rep_data(data, byte_count):
	return ('%0' + str(byte_count * 2) + 'X') % data


class bin_editor(object):
	def __init__(self):
		self.cursor_index = 0
		self.window_y_offset = 0
		self.byte_count = 4
		self.width = 8
	def display_byte(self, index):
		index_y = index / self.width - self.window_y_offset
		index_x = index % self.width
		self.screen.addstr(index_y, index_x * (self.byte_count * 2 + 1), rep_data(self.data[index], self.byte_count) + ' ')

	def display_bytes(self):
		offset = self.window_y_offset * self.width
		for i in range(offset, min(len(self.data), offset + self.max_y * self.width)):
			self.display_byte(i)

	def display_cursor(self):
		cursor_y = self.cursor_index / (self.byte_count * 2) / self.width
		cursor_y -= self.window_y_offset
		cursor_x = self.cursor_index / (self.byte_count * 2) % self.width
		cursor_offset = self.cursor_index % (self.byte_count * 2)
		self.screen.addstr(cursor_y, cursor_x * (self.byte_count * 2 + 1) + cursor_offset, '')



	def edit_byte_piece(self, index, key):
		shift = (self.byte_count * 2) - 1 - index % (self.byte_count * 2)
		data_index = index / (self.byte_count * 2)
		self.data[data_index] = (int(key, 16) << shift * 4) | (self.data[data_index] ^ (self.data[data_index] & (0xf << shift * 4)))

	def print_info(self, msg):
		self.screen.addstr(50, 1, ' ' * 40)
		self.screen.addstr(50, 1, msg)


	def redraw(self):
		self.screen.clear()
		self.display_bytes()
		#self.display_cursor()

	def main(self, screen):
		self.screen = screen
		self.max_y, self.max_x = self.screen.getmaxyx()
		self.screen.clear()

		if len(sys.argv) > 1:
			filepath = sys.argv[1]
			self.data = read_data(filepath, self.byte_count)
			self.print_info('read file: '+filepath)


		self.display_bytes()
		self.display_cursor()
		
		self.screen.refresh()
		k = self.screen.getkey()
		while k != 'q':
			if k == 'KEY_LEFT':
				if self.cursor_index > 0:
					self.cursor_index -= 1
			elif k == 'KEY_RIGHT':
				if self.cursor_index < len(self.data) * self.byte_count * 2:
					self.cursor_index += 1
			elif k == 'KEY_UP':
				self.cursor_index -= self.width * self.byte_count * 2
				if self.cursor_index < 0:
					self.cursor_index = 0
			elif k == 'KEY_DOWN':
				self.cursor_index += self.width * self.byte_count * 2
				if self.cursor_index > len(self.data) * self.byte_count * 2:
					self.cursor_index = len(self.data) * self.byte_count * 2

			elif len(k) == 1 and ((k >= '0' and k <= '9') or (k >= 'a' and k <= 'f')):
				self.edit_byte_piece(self.cursor_index, k)
				self.display_byte(self.cursor_index / (self.byte_count * 2))
				self.cursor_index += 1

			elif k == 'w':
				write_data(filepath, self.data, self.byte_count)
				self.print_info('wrote file: '+filepath)


			cursor_y = self.cursor_index / (self.byte_count * 2) / self.width
			if cursor_y - self.window_y_offset < 0:
				self.window_y_offset -= 1
				self.redraw()
			if cursor_y - self.window_y_offset >= self.max_y:
				self.window_y_offset += 1
				self.redraw()
			
			self.display_cursor()

			self.screen.refresh()
			k = self.screen.getkey()


bedit = bin_editor()
curses.wrapper(bedit.main)


