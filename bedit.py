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

def read_data(filepath):
	text = read_file(filepath)

	data = [ ord(c) for c in text ]
	#data = [ join_bytes(data[n:n+byte_count], byte_count, little_endian) for n in range(0, len(data), byte_count) ]
	return data

def write_data(filepath, data):
	#data = sum([ split_bytes(n, byte_count, little_endian) for n in data ], [])
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
		self.byte_count = 1
		self.max_byte_count = 32
		self.width = 32
		self.little_endian = False
		self.show_guide_lines = True

		self.byte_colors = [ 0 for i in range(256) ]
		for c in range(0x20, 0x7f):
			self.byte_colors[c] = 1
		for c in range(0x80, 0x100):
			self.byte_colors[c] = 3
		self.byte_color_mods = [ 0 for i in range(256) ]
		for c in range(0x20, 0x7f):
			self.byte_color_mods[c] = curses.A_BOLD
		#self.byte_color_ranges = [ 0 for _ in range(0, 0x20) ] + [ 1 for _ in range(0x20, 0x7f) ] + [ 0 for _ in range(0x7f, 0x100) ]

	def display_byte(self, index):
		index_y = index / self.width - self.window_y_offset
		index_x = index % self.width
		
		offset_x = index_x / self.byte_count * (self.byte_count * 2 + 1)
		if self.little_endian:
			offset_x += (self.byte_count - index_x % self.byte_count - 1) * 2
		else:
			offset_x += index_x % self.byte_count * 2
		self.screen.addstr(index_y, offset_x + 10, '%02X' % self.data[index], self.byte_color_mods[self.data[index]] | curses.color_pair(self.byte_colors[self.data[index]]))

	def display_bytes(self):
		offset = self.window_y_offset * self.width
		for i in range(offset, min(len(self.data), offset + (self.max_y - 1) * self.width)):
			self.display_byte(i)

	def display_guide_lines(self):
		for y in range(0, min(self.max_y - 1, len(self.data) / self.width - self.window_y_offset + 1)):
			for byte_offset in range(0, self.width, 4 * self.byte_count):
				offset_x = byte_offset / self.byte_count * (self.byte_count * 2 + 1)
				offset_x += byte_offset % self.byte_count * 2
				self.screen.addstr(y, offset_x + 9, '|')

	def display_address(self, address, index_y):
		if address % 0x100 == 0:	
			self.screen.addstr(index_y, 0, '%08X:' % address, curses.color_pair(4))
		else:
			self.screen.addstr(index_y, 0, '%08X:' % address)

	def display_addresses(self):
		for i in range(self.window_y_offset, min(len(self.data) / self.width + 1, self.window_y_offset + self.max_y - 1)):
			self.display_address(i * self.width, i - self.window_y_offset)

	def display_cursor(self):
		cursor_y = self.cursor_index / 2 / self.width
		cursor_y -= self.window_y_offset
		cursor_x = self.cursor_index / 2 % self.width
		cursor_x = cursor_x * 2 + cursor_x / self.byte_count
		cursor_offset = self.cursor_index % 2
		self.screen.addstr(cursor_y, cursor_x + cursor_offset + 10, '')

	def rep_text_byte(self, c):
		if c >= 0x20 and c < 0x7e:
			return chr(c)
		else:
			return '.'

	def display_text_line(self, index):
		index_y = index / self.width - self.window_y_offset
		offset_x = self.width * 2 + self.width / self.byte_count + 10

		text = ''.join([ self.rep_text_byte(self.data[i]) for i in range(index, min(index + self.width, len(self.data))) ])
		self.screen.addstr(index_y, offset_x, text)

	def display_text(self):
		offset = self.window_y_offset * self.width
		for i in range(offset, min(len(self.data), offset + (self.max_y - 1) * self.width), self.width):
			self.display_text_line(i)

	def edit_byte_piece(self, index, key):
		shift = (1 - index % 2) * 4
		data_index = index / 2
		if self.little_endian:
			offset = self.byte_count - data_index % self.byte_count - 1
			data_index = offset + data_index / self.byte_count * self.byte_count
		self.data[data_index] = (int(key, 16) << shift) | (self.data[data_index] ^ (self.data[data_index] & (0xf << shift)))

	def print_info(self, msg):
		self.screen.addstr(self.max_y - 1, 1, ' ' * 40)
		self.screen.addstr(self.max_y - 1, 1, msg)


	def redraw(self):
		self.screen.clear()
		self.display_addresses()
		if self.show_guide_lines:
			self.display_guide_lines()
		self.display_bytes()
		self.display_text()
		#self.display_cursor()

	def store_data(self, filepath):
		write_data(filepath, self.data)
	
	def load_data(self, filepath):
		self.data = read_data(filepath)

	def main(self, screen):
		self.screen = screen
		self.max_y, self.max_x = self.screen.getmaxyx()
		self.screen.clear()
		curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
		curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
		curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_RED)
		curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_WHITE)

		if len(sys.argv) > 1:
			self.filepath = sys.argv[1]
			self.load_data(self.filepath)
			self.print_info('read file: '+self.filepath)


		self.redraw()
		#self.display_bytes()
		self.display_cursor()
		
		self.screen.refresh()
		k = self.screen.getkey()
		while k != 'q':
			if k == 'KEY_LEFT':
				self.cursor_index -= 1
				self.print_info('offset %X/%X' % (self.cursor_index / 2, len(self.data)))
			elif k == 'KEY_RIGHT':
				self.cursor_index += 1
				self.print_info('offset %X/%X' % (self.cursor_index / 2, len(self.data)))
			elif k == 'KEY_UP':
				self.cursor_index -= self.width * 2
				self.print_info('offset %X/%X' % (self.cursor_index / 2, len(self.data)))
			elif k == 'KEY_DOWN':
				self.cursor_index += self.width * 2
				self.print_info('offset %X/%X' % (self.cursor_index / 2, len(self.data)))
			elif k == 'KEY_PPAGE':
				self.cursor_index -= (self.max_y - 1) * self.width * 2
				if self.cursor_index < 0:
					self.window_y_offset = 0
				else:
					self.window_y_offset -= self.max_y - 1
				self.redraw()
				self.print_info('offset %X/%X' % (self.cursor_index / 2, len(self.data)))
			elif k == 'KEY_NPAGE':
				self.cursor_index += (self.max_y - 1) * self.width * 2
				self.window_y_offset += self.max_y - 1
				self.redraw()
				self.print_info('offset %X/%X' % (self.cursor_index / 2, len(self.data)))
			elif k == ']':
				if self.byte_count > 1:
					self.byte_count /= 2
					self.redraw()
				self.print_info('byte_count = %d' % self.byte_count)
			elif k == '[':
				if self.byte_count < self.max_byte_count:
					self.byte_count *= 2
					self.redraw()
				self.print_info('byte_count = %d' % self.byte_count)

			elif k == 'p':
				self.little_endian = not self.little_endian
				self.redraw()
				self.print_info('little_endian = {}'.format(self.little_endian))
			
			elif k == 'l':
				self.show_guide_lines = not self.show_guide_lines
				self.redraw()
				self.print_info('show_guide_lines = {}'.format(self.show_guide_lines))

			elif len(k) == 1 and ((k >= '0' and k <= '9') or (k >= 'a' and k <= 'f')):
				self.edit_byte_piece(self.cursor_index, k)
				byte_index = self.cursor_index / 2
				if self.little_endian:
					offset = self.byte_count - byte_index % self.byte_count - 1
					byte_index = byte_index / self.byte_count * self.byte_count + offset
				self.display_byte(byte_index)
				self.display_text_line(byte_index / self.width * self.width)
				self.cursor_index += 1

			elif k == 'w':
				self.store_data(self.filepath)
				self.print_info('wrote file: '+self.filepath)
			else:
				self.print_info('unknown command "{}"'.format(k))

			if self.cursor_index < 0:
				self.cursor_index = 0
				self.print_info('offset %X/%X' % (self.cursor_index / 2, len(self.data)))
			if self.cursor_index > len(self.data) * 2:
				self.cursor_index = len(self.data) * 2
				self.print_info('offset %X/%X' % (self.cursor_index / 2, len(self.data)))
			
			cursor_y = self.cursor_index / 2 / self.width
			if cursor_y - self.window_y_offset < 0:
				self.window_y_offset += cursor_y - self.window_y_offset
				self.redraw()
				self.print_info('offset %X/%X' % (self.cursor_index / 2, len(self.data)))
			if cursor_y - self.window_y_offset >= self.max_y - 1:
				self.window_y_offset += cursor_y - self.window_y_offset - (self.max_y - 2)
				self.redraw()
				self.print_info('offset %X/%X' % (self.cursor_index / 2, len(self.data)))
			
			self.display_cursor()

			self.screen.refresh()
			k = self.screen.getkey()


bedit = bin_editor()
curses.wrapper(bedit.main)


