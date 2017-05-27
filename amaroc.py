#!/usr/bin/env python
"""
Copyright (c) 2006 Armando Vega <synan@rilinux.hr>
All rights reserved.

This is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; version 2 of the License.

This software is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this software; if not, write to the Free Software
Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307,
USA.
"""

import curses, commands
from time import sleep
from sys import exit

############
# Functions
############
def endit():
	curses.curs_set(1); curses.nocbreak(); stdscr.keypad(0); curses.echo()
	curses.endwin()

def ak_basic(doit, return_status=0):
	dcop = 'dcop --user ' + whoami + ' amarok player ' + doit
	ret_val = commands.getoutput(dcop).split(' ')
	if ret_val[0] in ('ERROR:','call','object'):
		return 0
	elif return_status == 1:
		return ret_val
	else:
		return 1


def statuswin(message):
	global y, x, stdscr
	win = stdscr.subwin(3, len(message)+4, y/2, x/2-len(message)+4/2)
	win.clear()
	win.border()
	win.addstr(1, 2, message)
	win.refresh()
	sleep(1)
	win.erase()

def scroll_list(offset):
	global scr_y, scr_x, cur_y, songlist, scroll
	scroll.clear()
	if len(songlist) <= scr_y - 1 :
		limit = len(songlist)
	else:
		limit = offset + scr_y - 1
	num = 0
	tag = the_offset + cur_y
	current = getcurrent()
	for i in range(offset,limit):
		if i == tag:
			scroll.addstr(num, 2, songlist[i], curses.A_UNDERLINE)
		elif i == current:
			scroll.addstr(num, 2, songlist[i], curses.A_BOLD)
		else:
			scroll.addstr(num, 2, songlist[i])
		num = num + 1

def refmainwin():
	global stdscr, y, x
	y, x = stdscr.getmaxyx()
	stdscr.clear()
	stdscr.border()
	stdscr.addstr(0, x/2-3, "Amaroc",curses.A_BOLD);
	stdscr.refresh()

def refscrollwin():
	global scroll, stdscr, y, x, scr_y, scr_x
	scroll = stdscr.subwin(y-4, x-4, 1, 1)
	scr_y, scr_x = scroll.getmaxyx()	

def fixxml(dirty):
	fixed = dirty.replace('&amp;','&').replace('&lt;','<').replace('&gt;','>')
	return fixed

def refreshlist():
	global songlist
	query = 'dcop --user ' + whoami + ' amarok playlist saveCurrentPlaylist'
	dcop_query = commands.getoutput(query).split(' ')
        if dcop_query[0] in ('ERROR:','call','object'):
                return 0
        else:
		fp = open(dcop_query[0])
		songs_temp = fp.read().split('</item>')
		songs_temp.pop()
		songlist = []

		for track in songs_temp:
			song_title = track.split('<Title>')[1].split('</Title>')[0]
			song_artist = track.split('<Artist>')[1].split('</Artist>')[0]
			art = fixxml(song_artist)
			song = fixxml(song_title)
			if len(song_artist) > 30:
				art = song_artist[0:30] + '...'
			if len(song_title) > 30:
				song = song_title[0:30] + '...'
			songlist.append(art + ' - ' + song)

def getcurrent():
	query = 'dcop --user ' + whoami + ' amarok playlist getActiveIndex'
	dcop_query = commands.getoutput(query)
	dcop_check = dcop_query.split(' ')
	if dcop_check[0] in ('ERROR:','call','object'):
		return 0
	else:
		return int(dcop_query)

def playindex(index):
	global whoami
	query = 'dcop --user ' + whoami + ' amarok playlist playByIndex ' + index
	dcop_query = commands.getoutput(query).split(' ')
	if dcop_query[0] in ('ERROR:','call','object'):
		return 0
	else:
		return 1

def refbottomwin():
	global stdscr, x, y
	bottom_w = stdscr.subwin(y-3, 0)
	bottom_w.border()
	amarok_status = getstatus()
	rand_status = get_x_status('randomModeStatus')
	repeat_status = get_x_status('repeatPlaylistStatus')
	if amarok_status != '0':
		bottom_w.addstr(1, 2, amarok_status)
		if rand_status == 2:
			bottom_w.addstr(1,x-7, 'Random')
		if rand_status == 1:
			bottom_w.addstr(1,x-7, '      ')
		if repeat_status == 2:
			bottom_w.addstr(1,x-16, 'Repeat')
		if repeat_status == 1:
			bottom_w.addstr(1,x-16, '      ')
	else:
		err == 1


def getstatus():
	global whoami
	query = 'dcop --user ' + whoami + ' amarok player status'
	dcop_query = commands.getoutput(query).split(' ')
	if dcop_query[0] in ('ERROR:','call','object'):
		return '0'
	elif dcop_query[0] == '0':
		return 'Stopped'
	elif dcop_query[0] == '1':
		return 'Paused '
	elif dcop_query[0] == '2':
		return 'Playing'

def get_x_status(ofwhat):
	global whoami
	query = 'dcop --user ' + whoami + ' amarok player ' + ofwhat
	dcop_query = commands.getoutput(query).split(' ')
	if dcop_query[0] in ('ERROR:','call','object'):
		return 0
	elif dcop_query[0] == 'false':
		rand = 1
	elif dcop_query[0] == 'true':
		rand = 2
	return rand


def toggle(what):
	global whoami
	if what == 'enableRandomMode':
		of_what = 'randomModeStatus'
	elif what == 'enableRepeatPlaylist':
		of_what = 'repeatPlaylistStatus'
	status = get_x_status(of_what)
	if status == 0:
		return 0
	elif status == 1:
		toggle = '1'
	elif status == 2:
		toggle = '0'
	query = 'dcop --user ' + whoami + ' amarok player ' + what + ' ' + toggle
	dcop_query = commands.getoutput(query).split(' ')
	if dcop_query[0] in ('ERROR:','call','object'):
		return 0
	else:
		return 1

def displayhelp():
	global stdscr
	win = stdscr.subwin(8, 42, 1, 2)
	win.clear()
	win.border()
	win.addstr(1, 2, 'up   -> up          |  a     -> prev  ')
	win.addstr(2, 2, 'down -> down        |  d     -> next  ')
	win.addstr(3, 2, 'left -> vol down    |  right -> vol up')
	win.addstr(4, 2, 'w    -> play/pause  |  s     -> stop  ')
	win.addstr(5, 2, 'q    -> random      |  e     -> repeat')
	win.addstr(6, 2, 'spc  -> play this   |  x     -> exit  ')
	win.refresh()
	win.getch()
	win.erase()


def volumeDisplay():
	global stdscr, y, x
	dcop = 'dcop --user ' + whoami + ' amarok player getVolume'
	ret_val = commands.getoutput(dcop).split(' ')
	if ret_val[0] in ('ERROR:','call','object'):
		return 0
	else:
		win = stdscr.subwin(3, 13, y/2-1, x/2-6)
		win.clear()
		win.border()
		volume = 'Volume: ' + ret_val[0]
		win.addstr(1, 1, volume)
		win.refresh()
		sleep(0.5)
		win.erase()


############
# Main part
############

stdscr = curses.initscr()
curses.noecho()
curses.cbreak()
stdscr.keypad(1)
curses.curs_set(0)
whoami = commands.getoutput('whoami')

y, x = stdscr.getmaxyx()

if x < 70:
	endit()
	print 'Need atleast 70x9'
	exit()
elif y < 9:
	endit()
	print 'Need atleast 70x9'
	exit()

ver = ak_basic('version', 1)
if ver == 0:
	statuswin('Amarok not running?')
	endit()
	exit()
else:
	version = 'Amarok ' + ver[0]
	statuswin(version)


# playlist
refreshlist()

# the while loop
the_offset = 0
cur_y = 0
refmainwin()
refbottomwin()
refscrollwin()

while(1):
	check_y,check_x = stdscr.getmaxyx()
	if check_y != y:
		err = 2
		break
	elif check_x != x:
		err = 2
		break

	refscrollwin()
	refbottomwin()
	scroll_list(the_offset)
	scroll.move(cur_y, 1)
	c = stdscr.getch()
	if c == ord('x'): err=0; break
	elif c == ord('h'):
		displayhelp()
	elif c == ord('d'): 
		ret = ak_basic('next')
		if ret == 0:
			err = 1
			break
		statuswin('Next track')
	elif c == ord('a'):
		ret = ak_basic('prev')
		if ret == 0:
			err = 1
			break
		statuswin('Previous track')
	elif c == ord(' '):
		ret = playindex(str(the_offset+cur_y))
		if ret == 0:
			err =  1
			break
	elif c == ord('w'):
		ret = ak_basic('playPause')
		if ret == 0:
			err = 1
			break
	elif c == ord('s'):
		ret = ak_basic('stop')
		if ret == 0:
			err = 1
			break
	elif c == ord('q'):
		ret = toggle('enableRandomMode')
		if ret == 0:
			err = 1
			break
	elif c == ord('e'):
		ret = toggle('enableRepeatPlaylist')
		if ret == 0:
			err = 1
			break
	elif c == curses.KEY_RIGHT:
		ret = ak_basic('volumeUp')
		if ret == 0:
			err = 1
			break
		else:
			volumeDisplay()
	elif c == curses.KEY_LEFT:
		ret = ak_basic('volumeDown')
		if ret == 0:
			err = 1
			break
		else:
			volumeDisplay()
	elif c == curses.KEY_UP:
		cur_y, cur_x = scroll.getyx()
		if cur_y == 0:
			if the_offset == 0:
				curses.beep()
			else:
				the_offset = the_offset - 1
		else:
			cur_y = cur_y - 1
	elif c == curses.KEY_DOWN:
		cur_y, cur_x = scroll.getyx()
		if cur_y == scr_y - 2:
			if the_offset + scr_y - 1 == len(songlist):
				curses.beep()
			else:
				the_offset = the_offset + 1
		else:
			if cur_y < len(songlist)-1:
				cur_y = cur_y + 1
	else: continue



endit()
if err == 1:
	print "Amarok not running"
elif err == 2:
	print "No support for resizing"
else:
	print "Exiting.."