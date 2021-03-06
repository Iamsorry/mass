#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import os.path
import time
import urllib, urllib2, cookielib
import json
import MultipartPostHandler

cookie_jar = None
session_opener = None
get_api_url = lambda x: 'http://www.plurk.com/API%s' % x
encode = urllib.urlencode
api_key = ''
accounts = {
	'account1': 'password1',
	'account2': 'password2',
	'account3': 'password3',
}

robots = {
	18757: 'plurkbuddy',
	4634727: '小籤籤',
	3436759: 'PlurkBuzz',
	4708688: '淺草籤',
	5993803: '掰噗',
	3212350: 'Citytalk城市通',
	4299622: '邦尼妹妹',
	4708232: '小歌手',
	6433462: 'Plurk分析工具',
	7753029: '卡馬警衛',
	4799740: '女僕小C',
	4952912: '執事Jin Cendrars',
	5410409: '轉噗機',
	5211437: '預報美眉',
	4579330: '肥肥夫人',
	4009327: '布魯斯推推',
}

timezone_offset = 60 * 60 * 8   # CST = GMT +8 hours

def ctime2iso(ctime):
	tm = time.strptime(ctime, '%a, %d %b %Y %H:%M:%S %Z')
	return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(int(time.mktime(tm)) + timezone_offset))

def json2obj(jsonstr):
	return json.loads(jsonstr
		.replace('\\u', '#UNI_ESC#')
		.replace('\\', '\\\\')
		.replace('#UNI_ESC#', '\\u')
		.decode('unicode-escape')
		.replace(r'\/', '/').replace('\n', ''))

def getPlurks(time_offset):
	fp = session_opener.open(get_api_url('/Timeline/getPlurks'),
		encode({'api_key': api_key,
		'limit': '100',
		'offset': time_offset,
		}))
	return json2obj(fp.read())

def getUserPlurks(time_offset, target_user):
	fp = session_opener.open(get_api_url('/Timeline/getPlurks'),
		encode({'api_key': api_key,
		'user_id': target_user,
		'limit': '100',
		'offset': time_offset,
		}))
	return json2obj(fp.read())

def getResponse(plurk_id):
	fp = session_opener.open(get_api_url('/Responses/get'),
		encode({'api_key': api_key,
		'plurk_id': plurk_id,
		}))
	return json2obj(fp.read())

def getPublicProfile(user_id):
	fp = session_opener.open(get_api_url('/Profile/getPublicProfile'),
		encode({'api_key': api_key,
		'user_id': user_id,
		}))
	return json2obj(fp.read())

def getOwnProfile():
	args = {'api_key': api_key}
	fp = session_opener.open(get_api_url('/Profile/getOwnProfile'),
		encode(args))
	return json2obj(fp.read())

def plurkAdd(qualifier, content):
	args = {'qualifier': qualifier,
		'content': content,
		'lang': 'tr_ch',
		'api_key': api_key}
	fp = session_opener.open(get_api_url('/Timeline/plurkAdd'),
		encode(args))
	return json2obj(fp.read())

def responseAdd(plurk_id, qualifier, content):
	args = {'plurk_id': plurk_id,
		'qualifier': qualifier,
		'content': content,
		'api_key': api_key}
	fp = session_opener.open(get_api_url('/Responses/responseAdd'),
		encode(args))
	return json2obj(fp.read())

def getFriendsByOffset(user_id, offset, limit):
	args = {'user_id': user_id,
		'offset': offset,
		'limit': limit,
		'api_key': api_key}
	fp = session_opener.open(get_api_url('/FriendsFans/getFriendsByOffset'),
		encode(args))
	return json2obj(fp.read())

def uploadPicture(imgp):
	uploader = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie_jar), MultipartPostHandler.MultipartPostHandler)
	args = {'api_key': api_key,
		'image': imgp}
	try:
		fp = uploader.open(get_api_url("/Timeline/uploadPicture"), args)
		obj = json2obj(fp.read())
	except urllib2.HTTPError, error:
		print 'Upload failed: %d - %s' % (error.code, error.read())
		exit()
	return obj

def login(username):
	if not accounts.has_key(username):
		print 'User not defined in plurklib'
		return None

	global cookie_jar
	global session_opener

	cookie_jar = cookielib.LWPCookieJar()
	cookie_file = 'plurk_session.' + username + '.txt'
	if os.path.isfile(cookie_file):
		cookie_jar.load(cookie_file)

	session_opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie_jar))
	#urllib2.install_opener(session_opener)

	obj = None
	try:
		obj = getOwnProfile()
	except urllib2.HTTPError, error:
		print 'Cookie auth failed: %d - %s' % (error.code, error.read())
		try:
			fp = session_opener.open(get_api_url('/Users/login'),
				encode({'api_key': api_key,
				'username': username,
				'password': accounts[username],
				#'no_data': '1',
				}))
			obj = json2obj(fp.read())
		except urllib2.HTTPError, error:
			print 'Password auth failed: %d - %s' % (error.code, error.read())
			exit()
		else:
			cookie_jar.save(cookie_file)

	return obj
