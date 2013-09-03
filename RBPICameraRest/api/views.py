# -*- coding: utf-8 -*- 
import os
import sys
import datetime
import collections
from django.http import HttpResponse, HttpResponseServerError
from django.utils import simplejson
from parser import *
import jsonpickle
from operator import itemgetter

from django.core.servers.basehttp import FileWrapper
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

from RBPiControl import *

JSON_MIMETYPE="application/json"


def version(request):

	data = {'name': 'RBPICameraRest',
		'version' : '0.1'}


	return HttpResponse(simplejson.dumps(data), JSON_MIMETYPE)


def get_photo_params (request):
	
	commands = parse(PHOTO_COMMAND)

	l = commands.values()
	l.sort(key=lambda x: x.cid)

	return HttpResponse(jsonpickle.encode(l), JSON_MIMETYPE)


def get_video_params (request):

	commands = parse(VIDEO_COMMAND)
	l = commands.values()
	l.sort(key=lambda x: x.cid)

	return HttpResponse(jsonpickle.encode(l), JSON_MIMETYPE)


@csrf_exempt
def video_streaming (request):

	if request.method == 'POST':
		json_data = simplejson.loads(request.raw_post_data)

		ip = request.META['HTTP_HOST'].split(":")[0]
		url_streaming = start_streaming(json_data, ip)

		return HttpResponse(simplejson.dumps(url_streaming), JSON_MIMETYPE)


	else:
		data = { 'msg' : 'Just allowed POST petition' }
		return HttpResponse(simplejson.dumps(data), JSON_MIMETYPE)


def video_streaming_stop (request):

	stop_streaming()

	data = {'code': 200,
		'msg' : 'Streaming stopped correctly!' }
	return HttpResponse(simplejson.dumps(data), JSON_MIMETYPE)

		
@csrf_exempt  
def photo_shot (request):

	if request.method == 'POST':
		json_data = simplejson.loads(request.raw_post_data)

		image_path = snap_photo (json_data)

		if (image_path == None):
			return HttpResponseServerError()


		image_file = open (image_path)

		response = HttpResponse(FileWrapper(image_file), content_type='image/jpeg')
		response['Content-Disposition'] = 'attachment; filename=image.jpg'

		return response

	else:
		data = { 'msg' : 'Just allowed POST petition' }
		return HttpResponse(simplejson.dumps(data), JSON_MIMETYPE)
