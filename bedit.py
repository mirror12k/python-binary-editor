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

def read_data(filepath, byte_count, little_endian=True):
	text = read_file(filepath)

	data = [ ord(c) for c in text ]
	data = [ join_bytes(data[n:n+byte_count], byte_count, little_endian) for n in range(0, len(data), byte_count) ]
	return data

def write_data(filepath, data, byte_count, little_endian=True):
	data = sum([ split_bytes(n, byte_count, little_endian) for n in data ], [])
	write_file(filepath, ''.join([ chr(c) for c in data ]))



def join_bytes(data, byte_count, little_endian=True):
	while len(data) < byte_count:
		data.append(0)
	if little_endian:
		return sum([ data[i] << 8 * i for i in range(0, byte_count) ])
	else:
		result = 0
		for i in range(0, byte_count):
			result = (result << 8) | data[i]
		return result

def split_bytes(data, byte_count, little_endian=True):
	if little_endian:
		return [ (data >> i * 8) & 0xff for i in range(0, byte_count) ]
	else:
		return [ (data >> i * 8) & 0xff for i in range(byte_count - 1, -1, -1) ]


def rep_data(data, byte_count):
	return ('%0' + str(byte_count * 2) + 'X') % data


class bin_editor(object):
	def __init__(self):
		self.cursor_index = 0
		self.window_y_offset = 0
		self.byte_count = 4
		self.width = 8
		self.little_endian = False
	def display_byte(self, index):
		index_y = index / self.width - self.window_y_offset
		index_x = index % self.width
		self.screen.addstr(index_y, index_x * (self.byte_count * 2 + 1), rep_data(self.data[index], self.byte_count) + ' ')

	def display_bytes(self):
		offset = self.window_y_offset * self.width
		for i in range(offset, min(len(self.data), offset + (self.max_y - 1) * self.width)):
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
		self.screen.addstr(self.max_y - 1, 1, ' ' * 40)
		self.screen.addstr(self.max_y - 1, 1, msg)


	def redraw(self):
		self.screen.clear()
		self.display_bytes()
		#self.display_cursor()

	def store_data(self, filepath):
		write_data(filepath, self.data, self.byte_count, self.little_endian)
	
	def load_data(self, filepath):
		self.data = read_data(filepath, self.byte_count, self.little_endian)

	def main(self, screen):
		self.screen = screen
		self.max_y, self.max_x = self.screen.getmaxyx()
		self.screen.clear()

		if len(sys.argv) > 1:
			self.filepath = sys.argv[1]
			self.load_data(self.filepath)
			self.print_info('read file: '+self.filepath)


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
			elif k == '[':
				if self.byte_count > 1:
					self.store_data('.BEDIT_TEMP_FILE')
					self.byte_count /= 2
					self.load_data('.BEDIT_TEMP_FILE')
					self.redraw()
					self.print_info('byte_count = %d' % self.byte_count)
				else:
					self.print_info('already at minimum byte count!')
			elif k == ']':
				if self.byte_count < 8:
					self.store_data('.BEDIT_TEMP_FILE')
					self.byte_count *= 2
					self.load_data('.BEDIT_TEMP_FILE')
					self.redraw()
					self.print_info('byte_count = %d' % self.byte_count)
				else:
					self.print_info('nope')

			elif k == 'p':
				self.store_data('.BEDIT_TEMP_FILE')
				self.little_endian = not self.little_endian
				self.load_data('.BEDIT_TEMP_FILE')
				self.redraw()
				self.print_info('little_endian = {}'.format(self.little_endian))

			elif len(k) == 1 and ((k >= '0' and k <= '9') or (k >= 'a' and k <= 'f')):
				self.edit_byte_piece(self.cursor_index, k)
				self.display_byte(self.cursor_index / (self.byte_count * 2))
				self.cursor_index += 1

			elif k == 'w':
				self.store_data(self.filepath)
				self.print_info('wrote file: '+self.filepath)


			cursor_y = self.cursor_index / (self.byte_count * 2) / self.width
			if cursor_y - self.window_y_offset < 0:
				self.window_y_offset -= 1
				self.redraw()
			if cursor_y - self.window_y_offset >= self.max_y - 1:
				self.window_y_offset += 1
				self.redraw()
			
			self.display_cursor()

			self.screen.refresh()
			k = self.screen.getkey()


bedit = bin_editor()
curses.wrapper(bedit.main)


