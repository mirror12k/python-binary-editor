# bedit binary editor
A very basic binary editor written in python with curses to be as minimalistic as possible.
Launch with ```./bedit.py <filepath>``` which will open the file for editing in hexidecimal format.

Permits in-place editting of bytes or inserting/deleting bytes in insert mode.

## controls
 - arrow keys - movement
 - pageup/pagedown - move entire pages
 - [0123456789abcdef] - edit the current byte
 - shift + q - quit
 - shift + w - save file to disk
 - [ ] - increase/decrease word size
 - { } - decrease/increase display width
 - p - toggle little endian
 - i - toggle insert mode
 - l - toggle guide lines
 - backspace - delete previous byte/word

## why?
Because pulling out ghex/bless all the time is becoming a pain.

