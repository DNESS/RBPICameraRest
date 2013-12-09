#!/usr/bin/env python

#  Copyright (C) 2013
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see http://www.gnu.org/licenses/.
#
#  Authors : Roberto Calvo <rocapal at gmail dot com>


from subprocess import call
import StringIO
from json import JSONEncoder
from django.utils import simplejson
import socket
import threading
import commands
import time
from time import strftime
import os

IMAGE_FILE_PATH = "/tmp/image.jpg"
IMAGE_DATETIME_FILE_PATH = "/tmp/image-datetime.jpg"
RBPI_PHOTO_COMMAND = "raspistill"
RBPI_VIDEO_COMMAND = "raspivid"

VLC_STREAMING_COMMAND = " | cvlc -vvv stream:///dev/stdin --sout '#standard{access=http,mux=ts,dst=:8090}' :demux=h264"
VLC_STREAMING_URL = "http://%s:8090/"

control_streaming_th = None 

disable_args = ['none','false', 'off']



def parse_args (args_list, timeout = 0):

	args = ""

	if "timeout" is not args_list:
		args = args + "--timeout " + str(timeout) + " "


	for arg in args_list:
		if (arg["argument"] == "true"):
			args = args + "--" + arg["name"] + " "
			continue
		if (arg["argument"] in disable_args):
			continue
                        
		args = args + "--" + arg["name"] + " " + arg["argument"] + " "

	return args

def snap_photo (args_list):

	args = "--output " + IMAGE_FILE_PATH + " "  + parse_args(args_list, 300)

	command = RBPI_PHOTO_COMMAND + " " + args

	return_code = call(command, shell=True);

	if (return_code == 0):
		datetime = strftime("%Y-%m-%d %H:%M:%S", time.localtime())
		command = "convert " + IMAGE_FILE_PATH + " -pointsize 12 -fill black -undercolor white -annotate +10+20 '" + datetime + "' " + IMAGE_DATETIME_FILE_PATH
		call(command, shell=True);
		os.remove(IMAGE_FILE_PATH)	
		return IMAGE_DATETIME_FILE_PATH
	else:
		return None


def launch_cmd (command):
	code = call (command, shell=True)

def start_streaming (args_list, ip):

	global control_streaming_th 
	res = {}
	args = " -o - " + parse_args(args_list, 9999999)
	command = RBPI_VIDEO_COMMAND + " " + args + " " + VLC_STREAMING_COMMAND

	print command 

	try:
		if (control_streaming_th == None):
			control_streaming_th = 1
			streaming_th  = threading.Thread(target = launch_cmd, args=[command])
			streaming_th.setDaemon(True)
			streaming_th.start()

		res["code"] = 200
		res["streaming_url"] = VLC_STREAMING_URL % (ip)
		
	except:		
		res["code"] = 500
		res["msg"] = "Error while streaming was initialized!"
		res["streaming_url"] = ""
		

	return res

def stop_streaming():

	global control_streaming_th 

	cmds = {'vlc',RBPI_VIDEO_COMMAND}

	for cmd in cmds:
		print "killing " + cmd
		kill_command = "ps aux | grep " + cmd + " | grep -v grep | tr -s ' ' | cut -d' ' -f2 | tr -s '\n' ' ' | sed -e s/^/kill\ -9\ /g | bash"
		call (kill_command, shell=True)

	control_streaming_th = None



def get_ip ():
	intf = 'eth0'
	intf_ip = commands.getoutput("ip address show dev " + intf).split()
	intf_ip = intf_ip[intf_ip.index('inet') + 1].split('/')[0]

	return intf_ip
