#! C:\Python26\
# -*- coding: utf-8 -*-
# Ch3wyB0t

# You can edit the location of your database here, or where you want it to be located
datafile = "./database/chewydb.db"

"""
Details about the bot
"""
author = "chewyb_13 @ Servers irc.chewynet.co.uk:6667 & HellRisingSun.BounceMe.Net:7202"
helpchans = "#chewybot @ Servers irc.chewynet.co.uk:6667 & HellRisingSun.BounceMe.Net:7202"
email = "chewyb13@gmail.com"
bugtracker = "http://code.google.com/p/chewybot-python/issues/list"
sourcecode = "https://chewybot-python.googlecode.com/svn/trunk/ chewybot-python-read-only"
version = "0.1.3.9"

"""
Please do not edit below this section
unless you know what you are doing
"""
import os, sys, subprocess
#import sqlite3
#import array
from collections import deque
import socket, asyncore, asynchat
import string, time, datetime, hashlib
#import optparse
#import threading
#import re
from database import Database as Database

settings = dict()
mysockets = dict()
mysocket = dict()

tempdata = dict()
loggedin = dict()

debuginfo = dict()

globtimer = dict()
lasttimer = dict()
timer = dict()
lastqueue = dict()
queue = dict()
db = Database(datafile)

""" This is the start of the code sections """
#44 is , 124 is | 126 is ~ 37 is %
#buildmsg(sock,'NORMAL',user,chan,'CHAN',output) #types are NORMAL, HELP, ERROR  mtype are PRIV, CHAN


# Notice types = 'CNOTE' = channel notice, 'PNOTE' = private notice
# PRIVMSG types = 'CMSG' = channel PRIVMSG, 'PMSG' = private PRIVMSGS
def commands(sock,type,user,incom,raw):
	if ((type == 'CNOTE') or (type == 'CMSG')):
		chan = rl(incom[2])
	else:
		chan = 'NULL'
	if (len(incom) >= 4):
		#debug("Enetered Private messages")
		if ((type == 'PNOTE') and (incom[0] == mysockets[sock]['connectaddress'])):
			#debug(sock,"Snotice: {0}".format(incom))
			blarg = 1
		elif ('\x01' in incom[3]):
			ctcp = incom[3:]
			stripcount = len(ctcp)
			while (stripcount):
				stripcount = stripcount - 1	
				ctcp[stripcount] = ctcp[stripcount].strip('\x01')
			if (ctcp[0].upper() == 'ACTION'):
				debug(sock,"Got a Action {0}".format(ctcp[1:]))
			elif (ctcp[0].upper() == 'VERSION'):
				if (len(ctcp) >= 2):
					debug(sock,"Got a CTCP VERSION Response {0}".format(ctcp[1:]))
				else:
					sts(sock,"NOTICE {0} :\x01VERSION Ch3wyB0t Version {1}\x01".format(user,version))
			elif (ctcp[0].upper() == 'PING'):
				if (len(ctcp) >= 2):
					sts(sock,"NOTICE {0} :\x01PING {1}\x01".format(user,ctcp[1]))
				else:
					sts(sock,"NOTICE {0} :\x01PING\x01".format(user))
			elif (ctcp[0].upper() == 'TIME'):
				if (len(ctcp) >= 2):
					debug(sock,"Got a CTCP TIME response {0}".format(ctcp[1:]))
				else:
					currenttime = datetime.datetime.now()
					sts(sock,"NOTICE {0} :\x01TIME {1}\x01".format(user,currenttime.strftime("%a %b %d %I:%M:%S%p %Y")))
			else:
				debug(sock,"Got a unknown CTCP request {0}".format(ctcp))
		elif (incom[3] == '?trigger'):
			buildmsg(sock,'NORMAL',user,chan,'PRIV',"Channel: {0}{2} Private Message: {1}{2}".format(settings['chancom'],settings['pvtcom'],settings['signal']))
		elif (((incom[3] == settings['chancom']+settings['signal']) and ((type == 'CMSG') or (type == 'CNOTE'))) or ((incom[3] == settings['pvtcom']+settings['signal']) and ((type == 'PMSG') or (type == 'PNOTE')))):
			if (len(incom) >= 5):
				if (incom[4].upper() == 'EXIT'):
					if (loggedgetaccess(sock,user,chan,'GLOBAL') >= 6):
						if (len(incom) >= 6):
							output = splitjoiner(incom[5:])
							tempsocks = mysockets.keys()
							for tempsock in tempsocks:
								mysockets[tempsock]['lastcmd'] = 'EXIT'
								sts(tempsock,"QUIT {0}".format(output))
						else:
							tempsocks = mysockets.keys()
							for tempsock in tempsocks:
								mysockets[tempsock]['lastcmd'] = 'EXIT'
								sts(tempsock,"QUIT Ch3wyB0t Version {0} Quitting".format(version))
					else:
						buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
				elif (incom[4].upper() == 'RELOAD'):
					if (loggedgetaccess(sock,user,chan,'GLOBAL') >= 6):
						tempsocks = mysockets.keys()
						debug('NULL',"Value {0} value".format(fulltemp))
						for tempsock in tempsocks:
							mysockets[tempsock]['lastcmd'] = 'RELOAD'
							sts(tempsock,"QUIT Ch3wyB0t Version {0} Reloading".format(version))
					else:
						buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
				elif (incom[4].upper() == 'RAW'):
					if (loggedgetaccess(sock,user,chan,'GLOBAL') >= 7):
						if (len(incom) >= 6):
							output = splitjoiner(raw[5:])
							sts(sock,"{0}".format(output))
							buildmsg(sock,'RAW',user,chan,'PRIV',"Sent {0} to Server".format(output))
						else:
							buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter what you want to send from the bot")
					else:
						buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
				elif (incom[4].upper() == 'RAWDB'):
					if (loggedgetaccess(sock,user,chan,'GLOBAL') >= 7):
						if (len(incom) >= 6):
							output = splitjoiner(raw[5:])
							vals = db.execute(output)
							buildmsg(sock,'RAW',user,chan,'PRIV',"Sent {0} to the database".format(output))
						else:
							buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter what you want to send to the database")
					else:
						buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
				elif (incom[4].upper() == 'QUIT'):
					if (loggedgetaccess(sock,user,chan,'SERVER') >= 6):
						if (len(incom) >= 6):
							mysockets[sock]['lastcmd'] = 'QUIT'
							sts(sock,"QUIT {0}".format(splitjoiner(incom[5:])))
						else:
							mysockets[sock]['lastcmd'] = 'QUIT'
							sts(sock,"QUIT Ch3wyB0t Version {0} Quitting".format(version))
					else:
						buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
				elif (incom[4].upper() == 'REHASH'):
					if (loggedgetaccess(sock,user,chan,'GLOBAL') >= 6):
						buildmsg(sock,'NORMAL',user,chan,'PRIV',"Rehashing...")
						rehash()
						buildmsg(sock,'NORMAL',user,chan,'PRIV',"Rehashing Complete...")
					else:
						buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
				elif (incom[4].upper() == 'SETTINGS'):
					if ((type == 'PMSG') or (type == 'PNOTE')):
						if (loggedgetaccess(sock,user,chan,'GLOBAL') >= 6):
							if (len(incom) >= 6):
								if (incom[5].upper() == 'SET'):
									if (len(incom) >= 7):
										if (len(incom) >= 8):
											sql = "UPDATE settings SET setting = '{0}', value = '{1}' WHERE setting = '{0}'".format(rl(incom[6]),incom[7])
											vals = db.execute(sql)
											settings[rl(incom[6])] = incom[7]
											buildmsg(sock,'NORMAL',user,chan,'PRIV',"You have successfully changed {0} to {1}".format(rl(incom[6]),incom[7]))
										else:
											buildmsg(sock,'ERROR',user,chan,'PRIV',"Missing Setting Value")
									else:
										buildmsg(sock,'ERROR',user,chan,'PRIV',"Missing Setting Name")
								elif (incom[5].upper() == 'LIST'):
									sql = "SELECT * FROM settings"
									records = db.select(sql)
									for record in records:
										buildmsg(sock,'NORMAL',user,chan,'PRIV',"Setting: {0} Value: {1}".format(record[1], record[2]))
								else:
									buildmsg(sock,'ERROR',user,chan,'PRIV',"Error, Use Either Set or List")
							else:
								buildmsg(sock,'ERROR',user,chan,'PRIV',"Error, Use Either Set or List")
						else:
							buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
					else:
						buildmsg(sock,'ERROR',user,chan,'PRIV',"You can not access settings via channel commands")
				elif (incom[4].upper() == 'SERVER'):
					if ((type == 'PMSG') or (type == 'PNOTE')):
						if (loggedgetaccess(sock,user,chan,'GLOBAL') >= 6):
							if (len(incom) >= 6):
								if (incom[5].upper() == 'ADD'):
									blarg = 1
								elif (incom[5].upper() == 'CHG'):
									blarg = 1
									#if (len(incom) >= 7):
										#if (len(incom) >= 8):
											#sql = "UPDATE settings SET setting = '{0}', value = '{1}' WHERE setting = '{0}'".format(rl(incom[6]),incom[7])
											#vals = db.execute(sql)
											#settings[rl(incom[6])] = incom[7]
											#buildmsg(sock,'NORMAL',user,chan,'PRIV',"You have successfully changed {0} to {1}".format(rl(incom[6]),incom[7]))
										#else:
											#buildmsg(sock,'ERROR',user,chan,'PRIV',"Missing Setting Value")
									#else:
										#buildmsg(sock,'ERROR',user,chan,'PRIV',"Missing Setting Name")
								elif (incom[5].upper() == 'LIST'):
									sql = "SELECT * FROM servers"
									records = db.select(sql)
									for record in records:
										if (record[10] == 'enabled'):
											buildmsg(sock,'NORMAL',user,chan,'PRIV',"\x033SID: {0} Server: {1} Address: {2} Port: {3} SPass: {4} Nick: {5} BNick: {6} NSPass: {7} BotOper: {8} BotOperPass: {9}\x03".format(int(record[0]),record[1],record[2],int(record[3]),record[4],record[5],record[6],record[7],record[8],record[9]))
										else:
											buildmsg(sock,'NORMAL',user,chan,'PRIV',"\x034SID: {0} Server: {1} Address: {2} Port: {3} SPass: {4} Nick: {5} BNick: {6} NSPass: {7} BotOper: {8} BotOperPass: {9}\x03".format(int(record[0]),record[1],record[2],int(record[3]),record[4],record[5],record[6],record[7],record[8],record[9]))
									buildmsg(sock,'NORMAL',user,chan,'PRIV',"Color \x033Green\x03 is enabled, Color \x034Red\x03 is disabled")
								else:
									buildmsg(sock,'ERROR',user,chan,'PRIV',"Error, Use Either List, Add, or Chg")
							else:
								buildmsg(sock,'ERROR',user,chan,'PRIV',"Error, Use Either List, Add, or Chg")
						else:
							buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
					else:
						buildmsg(sock,'ERROR',user,chan,'PRIV',"You can not access server via channel commands")
				elif (incom[4].upper() == 'CHANNEL'):
					if ((type == 'PMSG') or (type == 'PNOTE')):
						if (loggedgetaccess(sock,user,chan,'GLOBAL') >= 6):
							if (len(incom) >= 6):
								if (incom[5].upper() == 'CHG'):
									if (len(incom) >= 7):
										if (len(incom) >= 8):
											if (incom[7].upper() == 'SERVER'):
												blarg = 1
											elif (incom[7].upper() == 'CHANNEL'):
												blarg = 1
											elif (incom[7].upper() == 'CHANPASS'):
												blarg = 1
											elif (incom[7].upper() == 'CHANMODES'):
												blarg = 1
											elif (incom[7].upper() == 'CHANTOPIC'):
												blarg = 1
											elif (incom[7].upper() == 'OPTIONS'):
												blarg = 1
											elif (incom[7].upper() == 'ENABLED'):
												blarg = 1
											else:
												buildmsg(sock,'ERROR',user,chan,'PRIV',"Error, You must choose from Server, Channel, Chanpass, Chanmodes, Chantopic, Options, Enabled")
										else:
											buildmsg(sock,'ERROR',user,chan,'PRIV',"Error, You must choose from Server, Channel, Chanpass, Chanmodes, Chantopic, Options, Enabled")
									else:
										buildmsg(sock,'ERROR',user,chan,'PRIV',"Error, Missing CID number, please check channel list again")
									#if (len(incom) >= 7):
										#if (len(incom) >= 8):
											#sql = "UPDATE settings SET setting = '{0}', value = '{1}' WHERE setting = '{0}'".format(rl(incom[6]),incom[7])
											#vals = db.execute(sql)
											#settings[rl(incom[6])] = incom[7]
											#buildmsg(sock,'NORMAL',user,chan,'PRIV',"You have successfully changed {0} to {1}".format(rl(incom[6]),incom[7]))
										#else:
											#buildmsg(sock,'ERROR',user,chan,'PRIV',"Missing Setting Value")
									#else:
										#buildmsg(sock,'ERROR',user,chan,'PRIV',"Missing Setting Name")
								elif (incom[5].upper() == 'LIST'):
									sql = "SELECT * FROM channels"
									records = db.select(sql)
									for record in records:
										if (record[7] == 'enabled'):
											buildmsg(sock,'NORMAL',user,chan,'PRIV',"\x033CID: {0} Server: {1} Channel: {2} Pass: {3} Channel Modes: {4} Chan Options: {5}\x03".format(int(record[0]),record[1],record[2],record[3],record[4],record[6]))
											buildmsg(sock,'NORMAL',user,chan,'PRIV',"\x033CID: {0} Topic: {1}\x03".format(int(record[0]),record[5]))
										else:
											buildmsg(sock,'NORMAL',user,chan,'PRIV',"\x034CID: {0} Server: {1} Channel: {2} Pass: {3} Channel Modes: {4} Chan Options: {5}\x03".format(int(record[0]),record[1],record[2],record[3],record[4],record[6]))
											buildmsg(sock,'NORMAL',user,chan,'PRIV',"\x034CID: {0} Topic: {1}\x03".format(int(record[0]),record[5]))
									buildmsg(sock,'NORMAL',user,chan,'PRIV',"Color \x033Green\x03 is enabled, Color \x034Red\x03 is disabled")
								else:
									buildmsg(sock,'ERROR',user,chan,'PRIV',"Error, Use Either List, or Chg")
							else:
								buildmsg(sock,'ERROR',user,chan,'PRIV',"Error, Use Either List, or Chg")
						else:
							buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
					else:
						buildmsg(sock,'ERROR',user,chan,'PRIV',"You can not access channels via channel commands")
				elif (incom[4].upper() == 'USER'):
					if ((type == 'PMSG') or (type == 'PNOTE')):
						if (loggedgetaccess(sock,user,chan,'GLOBAL') >= 6):
							if (len(incom) >= 6):
								if (incom[5].upper() == 'ADD'):
									if (len(incom) >= 7):
										if (len(incom) >=8):
											tmpudata = pulluser(rl(incom[6]))
											if (tmpudata == 'FALSE'):
												tmppass = hashlib.md5()
												tmppass.update(incom[7])
												sql = "INSERT INTO users (username, password, global, server, channel, msgtype) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}')".format(rl(incom[6]),tmppass.hexdigest(),'NULL','NULL','NULL','msg')
												blarg = db.insert(sql)
												buildmsg(sock,'NORMAL',user,chan,'PRIV',"You have successfully created '{0}' with the password '{1}'".format(rl(incom[6]),incom[7]))
											else:
												buildmsg(sock,'ERROR',user,chan,'PRIV',"The username you entered already exists")
										else:
											buildmsg(sock,'ERROR',user,chan,'PRIV',"You only entered a username, please enter a password as well")
									else:
										buildmsg(sock,'ERROR',user,chan,'PRIV',"You are missing <username> <password>")
								elif (incom[5].upper() == 'CHG'):
									if (len(incom) >= 7):
										if (len(incom) >= 8):
											if (incom[7].upper() == 'PASS'):
												if (len(incom) >= 9):
													tmppass = hashlib.md5()
													tmppass.update(incom[8])
													sql = "UPDATE users SET password = '{0}' where username = '{1}'".format(tmppass.hexdigest(),rl(incom[6]))
													vals = db.execute(sql)
													buildmsg(sock,'NORMAL',user,chan,'PRIV',"You have successfully changed the password for '{0}'".format(rl(incom[6])))													
												else:
													buildmsg(sock,'ERROR',user,chan,'PRIV',"Error, Use format <username> PASS <newpass>")
											elif (incom[7].upper() == 'MSGTYPE'):
												if (len(incom) >= 9):
													if (incom[8].lower() == 'notice'):
														newtype = 'notice'
													else:
														newtype = 'msg'
													sql = "UPDATE users SET msgtype = '{0}' where username = '{1}'".format(newtype,rl(incom[6]))
													vals = db.execute(sql)
													if (islogged(sock,rl(incom[6])) == 'TRUE'):
														loggedin[sock][rl(incom[6])]['msgtype'] = newtype
													buildmsg(sock,'NORMAL',user,chan,'PRIV',"You have successfully changed the message type for '{0}' to '{1}'".format(rl(incom[6]),newtype))
												else:
													buildmsg(sock,'ERROR',user,chan,'PRIV',"Error, Use format <username> MSGTYPE <notice/msg>")
											else:
												buildmsg(sock,'ERROR',user,chan,'PRIV',"Error, Use Either Pass, Msgtype")
										else:
											buildmsg(sock,'ERROR',user,chan,'PRIV',"Error, Use Either Pass, Msgtype")
									else:
										buildmsg(sock,'ERROR',user,chan,'PRIV',"Missing Username")
								elif (incom[5].upper() == 'DEL'):
									#this bit of coding is only gonna be temperary for the time being due to abuse possiblities
									sql = "DELETE FROM users WHERE username = '{0}'".format(rl(incom[6]))
									db.execute(sql)
									buildmsg(sock,'NORMAL',user,chan,'PRIV',"Deleted {0} or attempted to delete from the database".format(rl(incom[6])))
								elif (incom[5].upper() == 'LIST'):
									sql = "SELECT * FROM users"
									records = db.select(sql)
									for record in records:
										buildmsg(sock,'NORMAL',user,chan,'PRIV',"UID: {0} Username: {1} Global: {2} Server: {3} Channel: {4} MsgType: {5}".format(int(record[0]),record[1],record[3],record[4],record[5],record[6]))
								else:
									buildmsg(sock,'ERROR',user,chan,'PRIV',"Error, Use Either List, Add, Del, or Chg")
							else:
								buildmsg(sock,'ERROR',user,chan,'PRIV',"Error, Use Either List, Add, Del, or Chg")
						else:
							buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
					else:
						buildmsg(sock,'ERROR',user,chan,'PRIV',"You can not access users via channel commands")
				elif (incom[4].upper() == 'ACCESS'):
					blarg = 1
				elif (incom[4].upper() == 'USERLIST'):	
					if (loggedgetaccess(sock,user,chan,'SERVER') >= 4):
						sql = "SELECT * FROM users"
						records = db.select(sql)
						buildmsg(sock,'NORMAL',user,chan,'PRIV',"Displaying user list, only showing Usernames atm, do note may be a big ammount of infomation")
						for record in records:
							buildmsg(sock,'NORMAL',user,chan,'PRIV',"Username: {0}".format(record[1]))
					else:
						buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
						
						
				elif (incom[4].upper() == 'MOWNER'):
					if (islogged(sock,user) == 'FALSE'):
						buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
					else:
						if ((type == 'PMSG') or (type == 'PNOTE')):
							if (len(incom) >= 6):
								chan = rl(incom[5])
								passthrough = 1
							else:
								passthrough = 0
								buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter a channel")
						if ((type == 'CMSG') or (type == 'CNOTE')):
							passthrough = 1
						if (passthrough == 1):
							if (getaccess(sock,loggedin[sock][user]['username'],chan,'CHANNEL') >= 5):
								massmodes(sock,user,chan,['ADD','q','ALL'])
							else:
								buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
				elif (incom[4].upper() == 'OWNER'):
					if (islogged(sock,user) == 'FALSE'):
						buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
					else:
						if ((type == 'PMSG') or (type == 'PNOTE')):
							if (len(incom) >= 6):
								chan = rl(incom[5])
								if (len(incom) >= 7):
									data = incom[6:]
									passthrough = 1
								else:
									passthrough = 0
									buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter any nicks")
							else:
								passthrough = 0
								buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter a channel")
						if ((type == 'CMSG') or (type == 'CNOTE')):
							if (len(incom) >= 6):
								data = incom[5:]
								passthrough = 1
							else:
								passthrough = 0
								buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter any nicks")
						if (passthrough == 1):
							if (getaccess(sock,loggedin[sock][user]['username'],chan,'CHANNEL') >= 5):
								massmodes(sock,user,chan,['ADD','q',data])
							else:
								buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
				elif (incom[4].upper() == 'MDEOWNER'):
					if (islogged(sock,user) == 'FALSE'):
						buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
					else:
						if ((type == 'PMSG') or (type == 'PNOTE')):
							if (len(incom) >= 6):
								chan = rl(incom[5])
								passthrough = 1
							else:
								passthrough = 0
								buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter a channel")
						if ((type == 'CMSG') or (type == 'CNOTE')):
							passthrough = 1
						if (passthrough == 1):
							if (getaccess(sock,loggedin[sock][user]['username'],chan,'CHANNEL') >= 5):
								massmodes(sock,user,chan,['REM','q','BC'])
							else:
								buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
				elif (incom[4].upper() == 'DEOWNER'):
					if (islogged(sock,user) == 'FALSE'):
						buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
					else:
						if ((type == 'PMSG') or (type == 'PNOTE')):
							if (len(incom) >= 6):
								chan = rl(incom[5])
								if (len(incom) >= 7):
									data = incom[6:]
									passthrough = 1
								else:
									passthrough = 0
									buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter any nicks")
							else:
								passthrough = 0
								buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter a channel")
						if ((type == 'CMSG') or (type == 'CNOTE')):
							if (len(incom) >= 6):
								data = incom[5:]
								passthrough = 1
							else:
								passthrough = 0
								buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter any nicks")
						if (passthrough == 1):
							if (getaccess(sock,loggedin[sock][user]['username'],chan,'CHANNEL') >= 5):
								massmodes(sock,user,chan,['REM','q',data])
							else:
								buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
				elif (incom[4].upper() == 'OWNERME'):
					if (islogged(sock,user) == 'FALSE'):
						buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
					else:
						if ((type == 'PMSG') or (type == 'PNOTE')):
							if (len(incom) >= 6):
								chan = rl(incom[5])
								passthrough = 1
							else:
								passthrough = 0
								buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter a channel")
						if ((type == 'CMSG') or (type == 'CNOTE')):
							passthrough = 1
						if (passthrough == 1):
							if (getaccess(sock,loggedin[sock][user]['username'],chan,'CHANNEL') >= 5):
								massmodes(sock,user,chan,['ADD','q',user]) #can be ADD or REM
							else:
								buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
				elif (incom[4].upper() == 'DEOWNERME'):
					if (islogged(sock,user) == 'FALSE'):
						buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
					else:
						if ((type == 'PMSG') or (type == 'PNOTE')):
							if (len(incom) >= 6):
								chan = rl(incom[5])
								passthrough = 1
							else:
								passthrough = 0
								buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter a channel")
						if ((type == 'CMSG') or (type == 'CNOTE')):
							passthrough = 1
						if (passthrough == 1):
							if (getaccess(sock,loggedin[sock][user]['username'],chan,'CHANNEL') >= 5):
								massmodes(sock,user,chan,['REM','q',user])
							else:
								buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
				elif (incom[4].upper() == 'MPROTECT'):
					if (islogged(sock,user) == 'FALSE'):
						buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
					else:
						if ((type == 'PMSG') or (type == 'PNOTE')):
							if (len(incom) >= 6):
								chan = rl(incom[5])
								passthrough = 1
							else:
								passthrough = 0
								buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter a channel")
						if ((type == 'CMSG') or (type == 'CNOTE')):
							passthrough = 1
						if (passthrough == 1):
							if (getaccess(sock,loggedin[sock][user]['username'],chan,'CHANNEL') >= 5):
								massmodes(sock,user,chan,['ADD','a','ALL'])
							else:
								buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
				elif (incom[4].upper() == 'PROTECT'):
					if (islogged(sock,user) == 'FALSE'):
						buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
					else:
						if ((type == 'PMSG') or (type == 'PNOTE')):
							if (len(incom) >= 6):
								chan = rl(incom[5])
								if (len(incom) >= 7):
									data = incom[6:]
									passthrough = 1
								else:
									passthrough = 0
									buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter any nicks")
							else:
								passthrough = 0
								buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter a channel")
						if ((type == 'CMSG') or (type == 'CNOTE')):
							if (len(incom) >= 6):
								data = incom[5:]
								passthrough = 1
							else:
								passthrough = 0
								buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter any nicks")
						if (passthrough == 1):
							if (getaccess(sock,loggedin[sock][user]['username'],chan,'CHANNEL') >= 5):
								massmodes(sock,user,chan,['ADD','a',data])
							else:
								buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
				elif (incom[4].upper() == 'MDEPROTECT'):
					if (islogged(sock,user) == 'FALSE'):
						buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
					else:
						if ((type == 'PMSG') or (type == 'PNOTE')):
							if (len(incom) >= 6):
								chan = rl(incom[5])
								passthrough = 1
							else:
								passthrough = 0
								buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter a channel")
						if ((type == 'CMSG') or (type == 'CNOTE')):
							passthrough = 1
						if (passthrough == 1):
							if (getaccess(sock,loggedin[sock][user]['username'],chan,'CHANNEL') >= 5):
								massmodes(sock,user,chan,['REM','a','BC'])
							else:
								buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
				elif (incom[4].upper() == 'DEPROTECT'):
					if (islogged(sock,user) == 'FALSE'):
						buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
					else:
						if ((type == 'PMSG') or (type == 'PNOTE')):
							if (len(incom) >= 6):
								chan = rl(incom[5])
								if (len(incom) >= 7):
									data = incom[6:]
									passthrough = 1
								else:
									passthrough = 0
									buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter any nicks")
							else:
								passthrough = 0
								buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter a channel")
						if ((type == 'CMSG') or (type == 'CNOTE')):
							if (len(incom) >= 6):
								data = incom[5:]
								passthrough = 1
							else:
								passthrough = 0
								buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter any nicks")
						if (passthrough == 1):
							if (getaccess(sock,loggedin[sock][user]['username'],chan,'CHANNEL') >= 5):
								massmodes(sock,user,chan,['REM','a',data])
							else:
								buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
				elif (incom[4].upper() == 'PROTECTME'):
					if (islogged(sock,user) == 'FALSE'):
						buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
					else:
						if ((type == 'PMSG') or (type == 'PNOTE')):
							if (len(incom) >= 6):
								chan = rl(incom[5])
								passthrough = 1
							else:
								passthrough = 0
								buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter a channel")
						if ((type == 'CMSG') or (type == 'CNOTE')):
							passthrough = 1
						if (passthrough == 1):
							if (getaccess(sock,loggedin[sock][user]['username'],chan,'CHANNEL') >= 4):
								massmodes(sock,user,chan,['ADD','a',user]) #can be ADD or REM
							else:
								buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
				elif (incom[4].upper() == 'DEPROTECTME'):
					if (islogged(sock,user) == 'FALSE'):
						buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
					else:
						if ((type == 'PMSG') or (type == 'PNOTE')):
							if (len(incom) >= 6):
								chan = rl(incom[5])
								passthrough = 1
							else:
								passthrough = 0
								buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter a channel")
						if ((type == 'CMSG') or (type == 'CNOTE')):
							passthrough = 1
						if (passthrough == 1):
							if (getaccess(sock,loggedin[sock][user]['username'],chan,'CHANNEL') >= 4):
								massmodes(sock,user,chan,['REM','a',user])
							else:
								buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
				elif (incom[4].upper() == 'MOP'):
					if (islogged(sock,user) == 'FALSE'):
						buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
					else:
						if ((type == 'PMSG') or (type == 'PNOTE')):
							if (len(incom) >= 6):
								chan = rl(incom[5])
								passthrough = 1
							else:
								passthrough = 0
								buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter a channel")
						if ((type == 'CMSG') or (type == 'CNOTE')):
							passthrough = 1
						if (passthrough == 1):
							if (getaccess(sock,loggedin[sock][user]['username'],chan,'CHANNEL') >= 3):
								massmodes(sock,user,chan,['ADD','o','ALL'])
							else:
								buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
				elif (incom[4].upper() == 'OP'):
					if (islogged(sock,user) == 'FALSE'):
						buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
					else:
						if ((type == 'PMSG') or (type == 'PNOTE')):
							if (len(incom) >= 6):
								chan = rl(incom[5])
								if (len(incom) >= 7):
									data = incom[6:]
									passthrough = 1
								else:
									passthrough = 0
									buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter any nicks")
							else:
								passthrough = 0
								buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter a channel")
						if ((type == 'CMSG') or (type == 'CNOTE')):
							if (len(incom) >= 6):
								data = incom[5:]
								passthrough = 1
							else:
								passthrough = 0
								buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter any nicks")
						if (passthrough == 1):
							if (getaccess(sock,loggedin[sock][user]['username'],chan,'CHANNEL') >= 3):
								massmodes(sock,user,chan,['ADD','o',data])
							else:
								buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
				elif (incom[4].upper() == 'MDEOP'):
					if (islogged(sock,user) == 'FALSE'):
						buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
					else:
						if ((type == 'PMSG') or (type == 'PNOTE')):
							if (len(incom) >= 6):
								chan = rl(incom[5])
								passthrough = 1
							else:
								passthrough = 0
								buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter a channel")
						if ((type == 'CMSG') or (type == 'CNOTE')):
							passthrough = 1
						if (passthrough == 1):
							if (getaccess(sock,loggedin[sock][user]['username'],chan,'CHANNEL') >= 3):
								massmodes(sock,user,chan,['REM','o','BC'])
							else:
								buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
				elif (incom[4].upper() == 'DEOP'):
					if (islogged(sock,user) == 'FALSE'):
						buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
					else:
						if ((type == 'PMSG') or (type == 'PNOTE')):
							if (len(incom) >= 6):
								chan = rl(incom[5])
								if (len(incom) >= 7):
									data = incom[6:]
									passthrough = 1
								else:
									passthrough = 0
									buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter any nicks")
							else:
								passthrough = 0
								buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter a channel")
						if ((type == 'CMSG') or (type == 'CNOTE')):
							if (len(incom) >= 6):
								data = incom[5:]
								passthrough = 1
							else:
								passthrough = 0
								buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter any nicks")
						if (passthrough == 1):
							if (getaccess(sock,loggedin[sock][user]['username'],chan,'CHANNEL') >= 3):
								massmodes(sock,user,chan,['REM','o',data])
							else:
								buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
				elif (incom[4].upper() == 'OPME'):
					if (islogged(sock,user) == 'FALSE'):
						buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
					else:
						if ((type == 'PMSG') or (type == 'PNOTE')):
							if (len(incom) >= 6):
								chan = rl(incom[5])
								passthrough = 1
							else:
								passthrough = 0
								buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter a channel")
						if ((type == 'CMSG') or (type == 'CNOTE')):
							passthrough = 1
						if (passthrough == 1):
							if (getaccess(sock,loggedin[sock][user]['username'],chan,'CHANNEL') >= 3):
								massmodes(sock,user,chan,['ADD','o',user]) #can be ADD or REM
							else:
								buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
				elif (incom[4].upper() == 'DEOPME'):
					if (islogged(sock,user) == 'FALSE'):
						buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
					else:
						if ((type == 'PMSG') or (type == 'PNOTE')):
							if (len(incom) >= 6):
								chan = rl(incom[5])
								passthrough = 1
							else:
								passthrough = 0
								buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter a channel")
						if ((type == 'CMSG') or (type == 'CNOTE')):
							passthrough = 1
						if (passthrough == 1):
							if (getaccess(sock,loggedin[sock][user]['username'],chan,'CHANNEL') >= 3):
								massmodes(sock,user,chan,['REM','o',user])
							else:
								buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
				elif (incom[4].upper() == 'MHALFOP'):
					if (islogged(sock,user) == 'FALSE'):
						buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
					else:
						if ((type == 'PMSG') or (type == 'PNOTE')):
							if (len(incom) >= 6):
								chan = rl(incom[5])
								passthrough = 1
							else:
								passthrough = 0
								buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter a channel")
						if ((type == 'CMSG') or (type == 'CNOTE')):
							passthrough = 1
						if (passthrough == 1):
							if (getaccess(sock,loggedin[sock][user]['username'],chan,'CHANNEL') >= 3):
								massmodes(sock,user,chan,['ADD','h','ALL'])
							else:
								buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
				elif (incom[4].upper() == 'HALFOP'):
					if (islogged(sock,user) == 'FALSE'):
						buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
					else:
						if ((type == 'PMSG') or (type == 'PNOTE')):
							if (len(incom) >= 6):
								chan = rl(incom[5])
								if (len(incom) >= 7):
									data = incom[6:]
									passthrough = 1
								else:
									passthrough = 0
									buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter any nicks")
							else:
								passthrough = 0
								buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter a channel")
						if ((type == 'CMSG') or (type == 'CNOTE')):
							if (len(incom) >= 6):
								data = incom[5:]
								passthrough = 1
							else:
								passthrough = 0
								buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter any nicks")
						if (passthrough == 1):
							if (getaccess(sock,loggedin[sock][user]['username'],chan,'CHANNEL') >= 3):
								massmodes(sock,user,chan,['ADD','h',data])
							else:
								buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
				elif (incom[4].upper() == 'MDEHALFOP'):
					if (islogged(sock,user) == 'FALSE'):
						buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
					else:
						if ((type == 'PMSG') or (type == 'PNOTE')):
							if (len(incom) >= 6):
								chan = rl(incom[5])
								passthrough = 1
							else:
								passthrough = 0
								buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter a channel")
						if ((type == 'CMSG') or (type == 'CNOTE')):
							passthrough = 1
						if (passthrough == 1):
							if (getaccess(sock,loggedin[sock][user]['username'],chan,'CHANNEL') >= 3):
								massmodes(sock,user,chan,['REM','h','BC'])
							else:
								buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
				elif (incom[4].upper() == 'DEHALFOP'):
					if (islogged(sock,user) == 'FALSE'):
						buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
					else:
						if ((type == 'PMSG') or (type == 'PNOTE')):
							if (len(incom) >= 6):
								chan = rl(incom[5])
								if (len(incom) >= 7):
									data = incom[6:]
									passthrough = 1
								else:
									passthrough = 0
									buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter any nicks")
							else:
								passthrough = 0
								buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter a channel")
						if ((type == 'CMSG') or (type == 'CNOTE')):
							if (len(incom) >= 6):
								data = incom[5:]
								passthrough = 1
							else:
								passthrough = 0
								buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter any nicks")
						if (passthrough == 1):
							if (getaccess(sock,loggedin[sock][user]['username'],chan,'CHANNEL') >= 3):
								massmodes(sock,user,chan,['REM','h',data])
							else:
								buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
				elif (incom[4].upper() == 'HALFOPME'):
					if (islogged(sock,user) == 'FALSE'):
						buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
					else:
						if ((type == 'PMSG') or (type == 'PNOTE')):
							if (len(incom) >= 6):
								chan = rl(incom[5])
								passthrough = 1
							else:
								passthrough = 0
								buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter a channel")
						if ((type == 'CMSG') or (type == 'CNOTE')):
							passthrough = 1
						if (passthrough == 1):
							if (getaccess(sock,loggedin[sock][user]['username'],chan,'CHANNEL') >= 2):
								massmodes(sock,user,chan,['ADD','h',user]) #can be ADD or REM
							else:
								buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
				elif (incom[4].upper() == 'DEHALFOPME'):
					if (islogged(sock,user) == 'FALSE'):
						buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
					else:
						if ((type == 'PMSG') or (type == 'PNOTE')):
							if (len(incom) >= 6):
								chan = rl(incom[5])
								passthrough = 1
							else:
								passthrough = 0
								buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter a channel")
						if ((type == 'CMSG') or (type == 'CNOTE')):
							passthrough = 1
						if (passthrough == 1):
							if (getaccess(sock,loggedin[sock][user]['username'],chan,'CHANNEL') >= 2):
								massmodes(sock,user,chan,['REM','h',user])
							else:
								buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
				elif (incom[4].upper() == 'MVOICE'):
					if (islogged(sock,user) == 'FALSE'):
						buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
					else:
						if ((type == 'PMSG') or (type == 'PNOTE')):
							if (len(incom) >= 6):
								chan = rl(incom[5])
								passthrough = 1
							else:
								passthrough = 0
								buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter a channel")
						if ((type == 'CMSG') or (type == 'CNOTE')):
							passthrough = 1
						if (passthrough == 1):
							if (getaccess(sock,loggedin[sock][user]['username'],chan,'CHANNEL') >= 2):
								massmodes(sock,user,chan,['ADD','v','ALL'])
							else:
								buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
				elif (incom[4].upper() == 'VOICE'):
					if (islogged(sock,user) == 'FALSE'):
						buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
					else:
						if ((type == 'PMSG') or (type == 'PNOTE')):
							if (len(incom) >= 6):
								chan = rl(incom[5])
								if (len(incom) >= 7):
									data = incom[6:]
									passthrough = 1
								else:
									passthrough = 0
									buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter any nicks")
							else:
								passthrough = 0
								buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter a channel")
						if ((type == 'CMSG') or (type == 'CNOTE')):
							if (len(incom) >= 6):
								data = incom[5:]
								passthrough = 1
							else:
								passthrough = 0
								buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter any nicks")
						if (passthrough == 1):
							if (getaccess(sock,loggedin[sock][user]['username'],chan,'CHANNEL') >= 2):
								massmodes(sock,user,chan,['ADD','v',data])
							else:
								buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
				elif (incom[4].upper() == 'MDEVOICE'):
					if (islogged(sock,user) == 'FALSE'):
						buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
					else:
						if ((type == 'PMSG') or (type == 'PNOTE')):
							if (len(incom) >= 6):
								chan = rl(incom[5])
								passthrough = 1
							else:
								passthrough = 0
								buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter a channel")
						if ((type == 'CMSG') or (type == 'CNOTE')):
							passthrough = 1
						if (passthrough == 1):
							if (getaccess(sock,loggedin[sock][user]['username'],chan,'CHANNEL') >= 2):
								massmodes(sock,user,chan,['REM','v','BC'])
							else:
								buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
				elif (incom[4].upper() == 'DEVOICE'):
					if (islogged(sock,user) == 'FALSE'):
						buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
					else:
						if ((type == 'PMSG') or (type == 'PNOTE')):
							if (len(incom) >= 6):
								chan = rl(incom[5])
								if (len(incom) >= 7):
									data = incom[6:]
									passthrough = 1
								else:
									passthrough = 0
									buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter any nicks")
							else:
								passthrough = 0
								buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter a channel")
						if ((type == 'CMSG') or (type == 'CNOTE')):
							if (len(incom) >= 6):
								data = incom[5:]
								passthrough = 1
							else:
								passthrough = 0
								buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter any nicks")
						if (passthrough == 1):
							if (getaccess(sock,loggedin[sock][user]['username'],chan,'CHANNEL') >= 2):
								massmodes(sock,user,chan,['REM','v',data])
							else:
								buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
				elif (incom[4].upper() == 'VOICEME'):
					if (islogged(sock,user) == 'FALSE'):
						buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
					else:
						if ((type == 'PMSG') or (type == 'PNOTE')):
							if (len(incom) >= 6):
								chan = rl(incom[5])
								passthrough = 1
							else:
								passthrough = 0
								buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter a channel")
						if ((type == 'CMSG') or (type == 'CNOTE')):
							passthrough = 1
						if (passthrough == 1):
							if (getaccess(sock,loggedin[sock][user]['username'],chan,'CHANNEL') >= 1):
								massmodes(sock,user,chan,['ADD','v',user]) #can be ADD or REM
							else:
								buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
				elif (incom[4].upper() == 'DEVOICEME'):
					if (islogged(sock,user) == 'FALSE'):
						buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
					else:
						if ((type == 'PMSG') or (type == 'PNOTE')):
							if (len(incom) >= 6):
								chan = rl(incom[5])
								passthrough = 1
							else:
								passthrough = 0
								buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter a channel")
						if ((type == 'CMSG') or (type == 'CNOTE')):
							passthrough = 1
						if (passthrough == 1):
							if (getaccess(sock,loggedin[sock][user]['username'],chan,'CHANNEL') >= 1):
								massmodes(sock,user,chan,['REM','v',user])
							else:
								buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
				elif (incom[4].upper() == 'SAY'):
					if (islogged(sock,user) == 'FALSE'):
						buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
					else:
						if ((type == 'PMSG') or (type == 'PNOTE')):
							if (len(incom) >= 6):
								chan = rl(incom[5])
								if (len(incom) >= 7):
									data = incom[6:]
									passthrough = 1
								else:
									passthrough = 0
									buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter a message")								
							else:
								passthrough = 0
								buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter a channel")
						if ((type == 'CMSG') or (type == 'CNOTE')):
							if (len(incom) >= 6):
								data = incom[5:]
								passthrough = 1
							else:
								passthrough = 0
								buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter a message")
						if (passthrough == 1):
							if (getaccess(sock,loggedin[sock][user]['username'],chan,'CHANNEL') >= 1):
								sts(sock,"PRIVMSG {0} :{1}".format(chan,splitjoiner(data)))
							else:
								buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
				elif (incom[4].upper() == 'ACT'):
					if (islogged(sock,user) == 'FALSE'):
						buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
					else:
						if ((type == 'PMSG') or (type == 'PNOTE')):
							if (len(incom) >= 6):
								chan = rl(incom[5])
								if (len(incom) >= 7):
									data = incom[6:]
									passthrough = 1
								else:
									passthrough = 0
									buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter a action")								
							else:
								passthrough = 0
								buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter a channel")
						if ((type == 'CMSG') or (type == 'CNOTE')):
							if (len(incom) >= 6):
								data = incom[5:]
								passthrough = 1
							else:
								passthrough = 0
								buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter a action")
						if (passthrough == 1):
							if (getaccess(sock,loggedin[sock][user]['username'],chan,'CHANNEL') >= 1):
								sts(sock,"PRIVMSG {0} :\x01ACTION {1}\x01".format(chan,splitjoiner(data)))
							else:
								buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
				elif (incom[4].upper() == 'ACCOUNT'):
					if ((type == 'PMSG') or (type == 'PNOTE')):
						if (islogged(sock,user) == 'TRUE'):
							if (len(incom) >= 6):
								userdetails = pulluser(loggedin[sock][user]['username'])
								if (incom[5].upper() == 'CHGPASS'):
									if (len(incom) >= 7):
										if (len(incom) >= 8):
											tmppass = hashlib.md5()
											tmppass.update(incom[6])
											if (userdata['password'] == tmppass.hexdigest()):
												tmppass2 = hashlib.md5()
												tmppass2.update(incom[7])
												sql = "UPDATE users SET password = '{0}' where id = '{1}'".format(tmppass2.hexdigest(),userdetails['id'])
												vals = db.execute(sql)
												buildmsg(sock,'NORMAL',user,chan,'PRIV',"You have successfully changed your password.")
											else:
												buildmsg(sock,'ERROR',user,chan,'PRIV',"You sure you entered your current password right")
										else:
											buildmsg(sock,'ERROR',user,chan,'PRIV',"Missing New Password")
									else:
										buildmsg(sock,'ERROR',user,chan,'PRIV',"Missing Current Password")
								if (incom[5].upper() == 'MSGTYPE'):
									if (len(incom) >= 7):
										if (incom[6].lower() == 'notice'):
											newtype = 'notice'
										else:
											newtype = 'msg'
										sql = "UPDATE users SET msgtype = '{0}' where id = '{1}'".format(newtype,userdetails['id'])
										vals = db.execute(sql)
										loggedin[sock][user]['msgtype'] = newtype
										buildmsg(sock,'NORMAL',user,chan,'PRIV',"You have successfully changed your message type to {0}".format(newtype))
									else:
										buildmsg(sock,'NORMAL',user,chan,'PRIV',"You have to enter a Message type")
							else:
								buildmsg(sock,'NORMAL',user,chan,'PRIV',"Your Account Details {0}({1})".format(user,loggedin[sock][user]['username']))
								buildmsg(sock,'NORMAL',user,chan,'PRIV',"MSGTYPE: {0}".format(loggedin[sock][user]['msgtype']))
						else:
							buildmsg(sock,'ERROR',user,chan,'PRIV','NOTLOGGED')
					else:
						buildmsg(sock,'ERROR',user,chan,'PRIV',"You can not access your account via channel commands")
				elif (incom[4].upper() == 'LOGOUT'):
					if (islogged(sock,user) == 'TRUE'):
						buildmsg(sock,'NORMAL',user,chan,'PRIV',"You have been logged out of {0}".format(loggedin[sock][user]['username']))
						del loggedin[sock][user]
					else:
						buildmsg(sock,'ERROR',user,chan,'PRIV','NOTLOGGED')
				elif (incom[4].upper() == 'LOGIN'):
					if ((type == 'PMSG') or (type == 'PNOTE')):
						if (islogged(sock,user) == 'FALSE'):
							if (len(incom) >= 6):
								if (len(incom) >= 7):
									udata = pulluser(rl(incom[5]))
									if (udata != 'FALSE'):
										tmppass = hashlib.md5()
										tmppass.update(incom[6])
										if (udata['password'] == tmppass.hexdigest()):
											loggedin[sock][user] = {'username': udata['username'], 'msgtype': udata['msgtype'], 'umask': incom[0]}
											buildmsg(sock,'NORMAL',user,chan,'PRIV',"You have successfully logged in as {0}".format(incom[5]))
										else:
											buildmsg(sock,'ERROR',user,chan,'PRIV',"You have failed to login")
									else:
										buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter a valid username")
								else:
									buildmsg(sock,'ERROR',user,chan,'PRIV',"You only entered a username, please enter a password as well")
							else:
								buildmsg(sock,'ERROR',user,chan,'PRIV',"You are missing <username> <password>")
						else:
							buildmsg(sock,'ERROR',user,chan,'PRIV',"You are already LOGGED In as {0}".format(loggedin[sock][user]['username']))
					else:
						buildmsg(sock,'ERROR',user,chan,'PRIV',"You can not log in via channel commands")						
				elif (incom[4].upper() == 'REGISTER'):
					if ((type == 'PMSG') or (type == 'PNOTE')):
						if (islogged(sock,user) == 'FALSE'):
							if (len(incom) >= 6):
								if (len(incom) >=7):
									tmpudata = pulluser(rl(incom[5]))
									if (tmpudata == 'FALSE'):
										tmppass = hashlib.md5()
										tmppass.update(incom[6])
										sql = "INSERT INTO users (username, password, global, server, channel, msgtype) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}')".format(rl(incom[5]),tmppass.hexdigest(),'NULL','NULL','NULL','msg')
										blarg = db.insert(sql)										
										loggedin[sock][user] = {'username': rl(incom[5]), 'msgtype': 'msg', 'umask': incom[0]}
										buildmsg(sock,'NORMAL',user,chan,'PRIV',"You have successfully registered as {0} and have been auto logged-in".format(incom[5]))
									else:
										buildmsg(sock,'ERROR',user,chan,'PRIV',"The username you entered already exists")
								else:
									buildmsg(sock,'ERROR',user,chan,'PRIV',"You only entered a username, please enter a password as well")
							else:
								buildmsg(sock,'ERROR',user,chan,'PRIV',"You are missing <username> <password>")
						else:
							buildmsg(sock,'ERROR',user,chan,'PRIV','LOGIN')				
					else:
						buildmsg(sock,'ERROR',user,chan,'PRIV',"You can not register via channel commands")
				elif (incom[4].upper() == 'HELP'):
					if ((type == 'PMSG') or (type == 'PNOTE')):
						if (len(incom) >= 6):
							chan = incom[5]
					helpcmd(sock,user,chan,incom)
				elif (incom[4].upper() == 'WHOIS'):
					if ((type == 'PMSG') or (type == 'PNOTE')):
						if (len(incom) >= 6):
							chan = incom[5]
							if (len(incom) >= 7):
								uwho = incom[6]
								passthrough = 1
							else:
								uwho = 'NULL'
								passthrough = 1
						else:
							buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter a channel")
					if ((type == 'CMSG') or (type == 'CNOTE')):
						if (len(incom) >= 6):
							uwho = incom[5]
							passthrough = 1
						else:
							uwho = 'NULL'
							passthrough = 1
					if (passthrough == 1):
						getwhois(sock,user,chan,'WHOIS',uwho)					
				elif (incom[4].upper() == 'WHOAMI'):
					if ((type == 'PMSG') or (type == 'PNOTE')):
						if (len(incom) >= 6):
							chan = rl(incom[5])
							passthrough = 1
						else:
							buildmsg(sock,'ERROR',user,chan,'PRIV',"You didn't enter a channel")
					if ((type == 'CMSG') or (type == 'CNOTE')):
						passthrough = 1
					if (passthrough == 1):	
						getwhois(sock,user,chan,'WHOAMI','NULL')					
				elif (incom[4].upper() == 'VERSION'):
					buildmsg(sock,'NORMAL',user,chan,'PRIV',"Ch3wyB0t Version {0}".format(version))				
				elif (incom[4].upper() == 'TESTCMD'):
					if (loggedgetaccess(sock,user,chan,'GLOBAL') >= 7):
						debug(sock,mysockets[sock])
					else:
						buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
				elif (incom[4].upper() == 'TEST'):
					if (loggedgetaccess(sock,user,chan,'GLOBAL') >= 7):

						#sts(sock,"MODE :{0}".format(mysockets[sock]['nick']))
						buildmsg(sock,'ERROR',user,chan,'PRIV',"data {0}".format('blarg'))
					else:
						buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESS')
				else:
					debug(sock,incom)
					if ((type == 'CMSG') or (type == 'CNOTE')):
						buildmsg(sock,'ERROR',user,chan,'CHAN',"The command {0} doesn't exist at the momment".format(incom[4]))
					if ((type == 'PMSG') or (type == 'PNOTE')):
						buildmsg(sock,'ERROR',user,chan,'PRIV',"The command {0} doesn't exist at the momment".format(incom[4]))
		else:
			if (type == 'PNOTE'):
				if (user == 'NickServ'):
					if (len(incom) >= 9):
						if ((incom[6] == 'registered') and (incom[8] == 'protected.')):
							if (mysockets[sock]['server']['nickservpass'] != 'NULL'):
								mysockets[sock]['nickserv'] = '1ST'
						elif ((incom[6] == 'NickServ') and (incom[7] == 'IDENTIFY')):
							if ((mysockets[sock]['server']['nickservpass'] != 'NULL') and (mysockets[sock]['nickserv'] == '1ST')):
								del mysockets[sock]['nickserv']
								sts(sock,"PRIVMSG NickServ :IDENTIFY {0}".format(mysockets[sock]['server']['nickservpass']))
								mysockets[sock]['identified'] = 'TRUE'
								autojoinchannels(sock)
				else:
					debug(sock,incom)
			else:
				#buildmsg(sock,'NORMAL',user,chan,'PRIV',output) #types are NORMAL, HELP, ERROR  mtype are PRIV, CHAN
				debug(sock,incom)
	else:
		#blarg = 'TRUE'
		#buildmsg(sock,'ERROR',user,chan,'PRIV',"The command {0} doesn't exist at the momment".format(incom[3]))
		debug(sock,incom)
	
def helpcmd(sock,user,chan,incom):
	buildmsg(sock,'HELP',user,chan,'PRIV',"{0} help system".format(settings['botname']))
	buildmsg(sock,'HELP',user,chan,'PRIV',"If you need help on a certain command go help <command>")
	buildmsg(sock,'HELP',user,chan,'PRIV',"{0}{3} = CHAN, {2}{3} = DCC, {1}{3} = MSG".format(settings['chancom'],settings['pvtcom'],settings['dcccom'],settings['signal']))
	if (len(incom) >= 6):
		if (chan == incom[5]):
			if (len(incom) >= 7):
				hcmds = incom[6:]
				processhelp = 1
			else:
				processhelp = 0
		else:
			hcmds = incom[5:]
			processhelp = 1
	else:
		processhelp = 0
	if (processhelp == 1):
		#debug(sock,len(incom))
		if (hcmds[0].upper() == 'EXIT'):
			if (loggedgetaccess(sock,user,chan,'GLOBAL') >= 6):
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(EXIT)- This Command will cause the bot to exit completely")
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(EXIT)- Command Structure: {0}{1} exit <message>".format(settings['pvtcom'],settings['signal']))
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(EXIT)- Command Structure: {0}{1} exit <message>".format(settings['chancom'],settings['signal']))
			else:
				buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESSHELP')
		elif (hcmds[0].upper() == 'RAW'):
			if (loggedgetaccess(sock,user,chan,'GLOBAL') >= 7):
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(RAW)- This Command is super dangerous as it will send whatever is entered into it")
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(RAW)- Command Structure: {0}{1} raw <data to send>".format(settings['pvtcom'],settings['signal']))
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(RAW)- Command Structure: {0}{1} raw <data to send>".format(settings['chancom'],settings['signal']))
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(RAW)- It is highly recommend you DO NOT use this command")
			else:
				buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESSHELP')
		elif (hcmds[0].upper() == 'RAWDB'):
			if (loggedgetaccess(sock,user,chan,'GLOBAL') >= 7):
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(RAWDB)- This Command is super dangerous as it will send whatever is entered into it")
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(RAWDB)- Command Structure: {0}{1} rawdb <data to send>".format(settings['pvtcom'],settings['signal']))
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(RAWDB)- Command Structure: {0}{1} rawdb <data to send>".format(settings['chancom'],settings['signal']))
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(RAWDB)- It is highly recommend you DO NOT use this command")
			else:
				buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESSHELP')				
		elif (hcmds[0].upper() == 'QUIT'):
			if (loggedgetaccess(sock,user,chan,'SERVER') >= 6):
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(QUIT)- This Command will cause the bot to quit from the current network")
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(QUIT)- Command Structure: {0}{1} quit <message>".format(settings['pvtcom'],settings['signal']))
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(QUIT)- Command Structure: {0}{1} quit <message>".format(settings['chancom'],settings['signal']))
			else:
				buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESSHELP')
		elif (hcmds[0].upper() == 'REHASH'):
			if (loggedgetaccess(sock,user,chan,'GLOBAL') >= 6):
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(REHASH)- This Command will cause the bot to reload from the database")
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(REHASH)- Command Structure: {0}{1} rehash".format(settings['pvtcom'],settings['signal']))
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(REHASH)- Command Structure: {0}{1} rehash".format(settings['chancom'],settings['signal']))
			else:
				buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESSHELP')
		elif (hcmds[0].upper() == 'SETTINGS'):
			if (loggedgetaccess(sock,user,chan,'GLOBAL') >= 6):
				if (len(hcmds) >= 2):
					if (hcmds[1].upper() == 'LIST'):
						buildmsg(sock,'HELP',user,chan,'PRIV',"-(SETTINGS)-(LIST)- This Command will list the values that are currently in the bots settings")
						buildmsg(sock,'HELP',user,chan,'PRIV',"-(SETTINGS)-(LIST)- Command Structure: {0}{1} settings list".format(settings['pvtcom'],settings['signal']))
					elif (hcmds[1].upper() == 'SET'):
						buildmsg(sock,'HELP',user,chan,'PRIV',"-(SETTINGS)-(SET)- This Command will set the value you pick and update both local and the db")
						buildmsg(sock,'HELP',user,chan,'PRIV',"-(SETTINGS)-(SET)- Command Structure: {0}{1} settings set <setting> <value>".format(settings['pvtcom'],settings['signal']))
					else:
						buildmsg(sock,'ERROR',user,chan,'PRIV',"-(SETTINGS)- The help topic account {0} is not in the database".format(hcmds[1]))
				else:
					buildmsg(sock,'HELP',user,chan,'PRIV',"-(SETTINGS)- This Command deals with the bots settings")
					buildmsg(sock,'HELP',user,chan,'PRIV',"-(SETTINGS)- Command Structure: {0}{1} settings [<list>][<set> <setting> <value>]".format(settings['pvtcom'],settings['signal']))
					buildmsg(sock,'HELP',user,chan,'PRIV',"-(SETTINGS)- Topics available: list set")
			else:
				buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESSHELP')

		#loggedgetaccess(sock,user,chan,type)
		elif (hcmds[0].upper() == 'MOWNER'):
			if (loggedgetaccess(sock,user,chan,'CHANNEL') >= 5):
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(MOWNER)- This Command will Owner everyone in <channel>")
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(MOWNER)- Command Structure: {0}{1} MOwner <channel>".format(settings['pvtcom'],settings['signal']))
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(MOWNER)- Command Structure: {0}{1} MOwner".format(settings['chancom'],settings['signal']))
			else:
				buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESSHELP')
		elif (hcmds[0].upper() == 'OWNER'):
			if (loggedgetaccess(sock,user,chan,'CHANNEL') >= 5):
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(OWNER)- This Command will Owner the <nicks> you pick on <channel>")
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(OWNER)- Command Structure: {0}{1} Owner <channel> <nick> [<nick> [<nick>]]".format(settings['pvtcom'],settings['signal']))
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(OWNER)- Command Structure: {0}{1} Owner <nick> [<nick> [<nick>]]".format(settings['chancom'],settings['signal']))
			else:
				buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESSHELP')
		elif (hcmds[0].upper() == 'MDEOWNER'):
			if (loggedgetaccess(sock,user,chan,'CHANNEL') >= 5):
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(MDEOWNER)- This Command will DeOwner everyone in <channel> but the bot and you")
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(MDEOWNER)- Command Structure: {0}{1} MDeOwner <channel>".format(settings['pvtcom'],settings['signal']))
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(MDEOWNER)- Command Structure: {0}{1} MDeOwner".format(settings['chancom'],settings['signal']))
			else:
				buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESSHELP')
		elif (hcmds[0].upper() == 'DEOWNER'):
			if (loggedgetaccess(sock,user,chan,'CHANNEL') >= 5):
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(DEOWNER)- This Command will de-Owner the <nicks> you pick on <channel>")
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(DEOWNER)- Command Structure: {0}{1} DeOwner <channel> <nick> [<nick> [<nick>]]".format(settings['pvtcom'],settings['signal']))
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(DEOWNER)- Command Structure: {0}{1} DeOwner <nick> [<nick> [<nick>]]".format(settings['chancom'],settings['signal']))
			else:
				buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESSHELP')
		elif (hcmds[0].upper() == 'OWNERME'):
			if (loggedgetaccess(sock,user,chan,'CHANNEL') >= 5):
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(OWNERME)- This Command will Owner yourself on <channel>")
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(OWNERME)- Command Structure: {0}{1} OwnerMe <channel>".format(settings['pvtcom'],settings['signal']))
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(OWNERME)- Command Structure: {0}{1} OwnerMe".format(settings['chancom'],settings['signal']))
			else:
				buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESSHELP')
		elif (hcmds[0].upper() == 'DEOWNERME'):
			if (loggedgetaccess(sock,user,chan,'CHANNEL') >= 5):
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(DEOWNERME)- This Command will de-Owner yourself on <channel>")
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(DEOWNERME)- Command Structure: {0}{1} DeOwnerMe <channel>".format(settings['pvtcom'],settings['signal']))
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(DEOWNERME)- Command Structure: {0}{1} DeOwnerMe".format(settings['chancom'],settings['signal']))
			else:
				buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESSHELP')
		elif (hcmds[0].upper() == 'MPROTECT'):
			if (loggedgetaccess(sock,user,chan,'CHANNEL') >= 5):
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(MPROTECT)- This Command will Protect everyone in <channel>")
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(MPROTECT)- Command Structure: {0}{1} MProtect <channel>".format(settings['pvtcom'],settings['signal']))
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(MPROTECT)- Command Structure: {0}{1} MProtect".format(settings['chancom'],settings['signal']))
			else:
				buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESSHELP')
		elif (hcmds[0].upper() == 'PROTECT'):
			if (loggedgetaccess(sock,user,chan,'CHANNEL') >= 5):
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(PROTECT)- This Command will Protect the <nicks> you pick on <channel>")
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(PROTECT)- Command Structure: {0}{1} Protect <channel> <nick> [<nick> [<nick>]]".format(settings['pvtcom'],settings['signal']))
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(PROTECT)- Command Structure: {0}{1} Protect <nick> [<nick> [<nick>]]".format(settings['chancom'],settings['signal']))
			else:
				buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESSHELP')
		elif (hcmds[0].upper() == 'MDEPROTECT'):
			if (loggedgetaccess(sock,user,chan,'CHANNEL') >= 5):
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(MDEPROTECT)- This Command will DeProtect everyone in <channel> but the bot and you")
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(MDEPROTECT)- Command Structure: {0}{1} MDeProtect <channel>".format(settings['pvtcom'],settings['signal']))
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(MDEPROTECT)- Command Structure: {0}{1} MDeProtect".format(settings['chancom'],settings['signal']))
			else:
				buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESSHELP')
		elif (hcmds[0].upper() == 'DEPROTECT'):
			if (loggedgetaccess(sock,user,chan,'CHANNEL') >= 5):
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(DEPROTECT)- This Command will de-Protect the <nicks> you pick on <channel>")
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(DEPROTECT)- Command Structure: {0}{1} DeProtect <channel> <nick> [<nick> [<nick>]]".format(settings['pvtcom'],settings['signal']))
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(DEPROTECT)- Command Structure: {0}{1} DeProtect <nick> [<nick> [<nick>]]".format(settings['chancom'],settings['signal']))
			else:
				buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESSHELP')
		elif (hcmds[0].upper() == 'PROTECTME'):
			if (loggedgetaccess(sock,user,chan,'CHANNEL') >= 4):
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(PROTECTME)- This Command will Protect yourself on <channel>")
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(PROTECTME)- Command Structure: {0}{1} ProtectMe <channel>".format(settings['pvtcom'],settings['signal']))
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(PROTECTME)- Command Structure: {0}{1} ProtectMe".format(settings['chancom'],settings['signal']))
			else:
				buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESSHELP')
		elif (hcmds[0].upper() == 'DEPROTECTME'):
			if (loggedgetaccess(sock,user,chan,'CHANNEL') >= 4):
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(DEPROTECTME)- This Command will de-Protect yourself on <channel>")
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(DEPROTECTME)- Command Structure: {0}{1} DeProtectMe <channel>".format(settings['pvtcom'],settings['signal']))
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(DEPROTECTME)- Command Structure: {0}{1} DeProtectMe".format(settings['chancom'],settings['signal']))
			else:
				buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESSHELP')
		elif (hcmds[0].upper() == 'MOP'):
			if (loggedgetaccess(sock,user,chan,'CHANNEL') >= 3):
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(MOP)- This Command will Op everyone in <channel>")
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(MOP)- Command Structure: {0}{1} MOp <channel>".format(settings['pvtcom'],settings['signal']))
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(MOP)- Command Structure: {0}{1} MOp".format(settings['chancom'],settings['signal']))
			else:
				buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESSHELP')
		elif (hcmds[0].upper() == 'OP'):
			if (loggedgetaccess(sock,user,chan,'CHANNEL') >= 3):
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(OP)- This Command will Op the <nicks> you pick on <channel>")
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(OP)- Command Structure: {0}{1} Op <channel> <nick> [<nick> [<nick>]]".format(settings['pvtcom'],settings['signal']))
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(OP)- Command Structure: {0}{1} Op <nick> [<nick> [<nick>]]".format(settings['chancom'],settings['signal']))
			else:
				buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESSHELP')
		elif (hcmds[0].upper() == 'MDEOP'):
			if (loggedgetaccess(sock,user,chan,'CHANNEL') >= 3):
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(MDEOP)- This Command will DeOp everyone in <channel> but the bot and you")
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(MDEOP)- Command Structure: {0}{1} MDeOp <channel>".format(settings['pvtcom'],settings['signal']))
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(MDEOP)- Command Structure: {0}{1} MDeOp".format(settings['chancom'],settings['signal']))
			else:
				buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESSHELP')
		elif (hcmds[0].upper() == 'DEOP'):
			if (loggedgetaccess(sock,user,chan,'CHANNEL') >= 3):
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(DEOP)- This Command will de-Op the <nicks> you pick on <channel>")
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(DEOP)- Command Structure: {0}{1} DeOp <channel> <nick> [<nick> [<nick>]]".format(settings['pvtcom'],settings['signal']))
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(DEOP)- Command Structure: {0}{1} DeOp <nick> [<nick> [<nick>]]".format(settings['chancom'],settings['signal']))
			else:
				buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESSHELP')
		elif (hcmds[0].upper() == 'OPME'):
			if (loggedgetaccess(sock,user,chan,'CHANNEL') >= 3):
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(OPME)- This Command will Op yourself on <channel>")
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(OPME)- Command Structure: {0}{1} OpMe <channel>".format(settings['pvtcom'],settings['signal']))
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(OPME)- Command Structure: {0}{1} OpMe".format(settings['chancom'],settings['signal']))
			else:
				buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESSHELP')
		elif (hcmds[0].upper() == 'DEOPME'):
			if (loggedgetaccess(sock,user,chan,'CHANNEL') >= 3):
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(DEOPME)- This Command will de-Op yourself on <channel>")
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(DEOPME)- Command Structure: {0}{1} DeOpMe <channel>".format(settings['pvtcom'],settings['signal']))
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(DEOPME)- Command Structure: {0}{1} DeOpMe".format(settings['chancom'],settings['signal']))
			else:
				buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESSHELP')
		elif (hcmds[0].upper() == 'MHALFOP'):
			if (loggedgetaccess(sock,user,chan,'CHANNEL') >= 3):
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(MHALFOP)- This Command will HalfOp everyone in <channel>")
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(MHALFOP)- Command Structure: {0}{1} MHalfOp <channel>".format(settings['pvtcom'],settings['signal']))
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(MHALFOP)- Command Structure: {0}{1} MHalfOp".format(settings['chancom'],settings['signal']))
			else:
				buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESSHELP')
		elif (hcmds[0].upper() == 'HALFOP'):
			if (loggedgetaccess(sock,user,chan,'CHANNEL') >= 3):
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(HALFOP)- This Command will HalfOp the <nicks> you pick on <channel>")
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(HALFOP)- Command Structure: {0}{1} HalfOp <channel> <nick> [<nick> [<nick>]]".format(settings['pvtcom'],settings['signal']))
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(HALFOP)- Command Structure: {0}{1} HalfOp <nick> [<nick> [<nick>]]".format(settings['chancom'],settings['signal']))
			else:
				buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESSHELP')
		elif (hcmds[0].upper() == 'MDEHALFOP'):
			if (loggedgetaccess(sock,user,chan,'CHANNEL') >= 3):
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(MDEHALFOP)- This Command will DeHalfOp everyone in <channel> but the bot and you")
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(MDEHALFOP)- Command Structure: {0}{1} MDeHalfOp <channel>".format(settings['pvtcom'],settings['signal']))
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(MDEHALFOP)- Command Structure: {0}{1} MDeHalfOp".format(settings['chancom'],settings['signal']))
			else:
				buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESSHELP')
		elif (hcmds[0].upper() == 'DEHALFOP'):
			if (loggedgetaccess(sock,user,chan,'CHANNEL') >= 3):
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(DEHALFOP)- This Command will de-HalfOp the <nicks> you pick on <channel>")
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(DEHALFOP)- Command Structure: {0}{1} DeHalfOp <channel> <nick> [<nick> [<nick>]]".format(settings['pvtcom'],settings['signal']))
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(DEHALFOP)- Command Structure: {0}{1} DeHalfOp <nick> [<nick> [<nick>]]".format(settings['chancom'],settings['signal']))
			else:
				buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESSHELP')
		elif (hcmds[0].upper() == 'HALFOPME'):
			if (loggedgetaccess(sock,user,chan,'CHANNEL') >= 2):
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(HALFOPME)- This Command will HalfOp yourself on <channel>")
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(HALFOPME)- Command Structure: {0}{1} HalfOpMe <channel>".format(settings['pvtcom'],settings['signal']))
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(HALFOPME)- Command Structure: {0}{1} HalfOpMe".format(settings['chancom'],settings['signal']))
			else:
				buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESSHELP')
		elif (hcmds[0].upper() == 'DEHALFOPME'):
			if (loggedgetaccess(sock,user,chan,'CHANNEL') >= 2):
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(DEHALFOPME)- This Command will de-HalfOp yourself on <channel>")
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(DEHALFOPME)- Command Structure: {0}{1} DeHalfOpMe <channel>".format(settings['pvtcom'],settings['signal']))
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(DEHALFOPME)- Command Structure: {0}{1} DeHalfOpMe".format(settings['chancom'],settings['signal']))
			else:
				buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESSHELP')
		elif (hcmds[0].upper() == 'MVOICE'):
			if (loggedgetaccess(sock,user,chan,'CHANNEL') >= 2):
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(MVOICE)- This Command will Voice everyone in <channel>")
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(MVOICE)- Command Structure: {0}{1} MVoice <channel>".format(settings['pvtcom'],settings['signal']))
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(MVOICE)- Command Structure: {0}{1} MVoice".format(settings['chancom'],settings['signal']))
			else:
				buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESSHELP')
		elif (hcmds[0].upper() == 'VOICE'):
			if (loggedgetaccess(sock,user,chan,'CHANNEL') >= 2):
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(VOICE)- This Command will voice the <nicks> you pick on <channel>")
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(VOICE)- Command Structure: {0}{1} Voice <channel> <nick> [<nick> [<nick>]]".format(settings['pvtcom'],settings['signal']))
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(VOICE)- Command Structure: {0}{1} Voice <nick> [<nick> [<nick>]]".format(settings['chancom'],settings['signal']))
			else:
				buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESSHELP')
		elif (hcmds[0].upper() == 'MDEVOICE'):
			if (loggedgetaccess(sock,user,chan,'CHANNEL') >= 2):
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(MDEVOICE)- This Command will DeVoice everyone in <channel> but the bot and you")
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(MDEVOICE)- Command Structure: {0}{1} MDeVoice <channel>".format(settings['pvtcom'],settings['signal']))
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(MDEVOICE)- Command Structure: {0}{1} MDeVoice".format(settings['chancom'],settings['signal']))
			else:
				buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESSHELP')
		elif (hcmds[0].upper() == 'DEVOICE'):
			if (loggedgetaccess(sock,user,chan,'CHANNEL') >= 2):
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(DEVOICE)- This Command will de-voice the <nicks> you pick on <channel>")
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(DEVOICE)- Command Structure: {0}{1} DeVoice <channel> <nick> [<nick> [<nick>]]".format(settings['pvtcom'],settings['signal']))
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(DEVOICE)- Command Structure: {0}{1} DeVoice <nick> [<nick> [<nick>]]".format(settings['chancom'],settings['signal']))
			else:
				buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESSHELP')
		elif (hcmds[0].upper() == 'VOICEME'):
			if (loggedgetaccess(sock,user,chan,'CHANNEL') >= 1):
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(VOICEME)- This Command will voice yourself on <channel>")
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(VOICEME)- Command Structure: {0}{1} VoiceMe <channel>".format(settings['pvtcom'],settings['signal']))
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(VOICEME)- Command Structure: {0}{1} VoiceMe".format(settings['chancom'],settings['signal']))
			else:
				buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESSHELP')
		elif (hcmds[0].upper() == 'DEVOICEME'):
			if (loggedgetaccess(sock,user,chan,'CHANNEL') >= 1):
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(DEVOICEME)- This Command will de-voice yourself on <channel>")
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(DEVOICEME)- Command Structure: {0}{1} DeVoiceMe <channel>".format(settings['pvtcom'],settings['signal']))
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(DEVOICEME)- Command Structure: {0}{1} DeVoiceMe".format(settings['chancom'],settings['signal']))
			else:
				buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESSHELP')
		elif (hcmds[0].upper() == 'SAY'):
			if (loggedgetaccess(sock,user,chan,'CHANNEL') >= 1):
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(SAY)- This command will cause the bot to say a message on a channel")
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(SAY)- Command Structure: {0}{1} say <channel> <message>".format(settings['pvtcom'],settings['signal']))
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(SAY)- Command Structure: {0}{1} say <message>".format(settings['chancom'],settings['signal']))
			else:
				buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESSHELP')		
		elif (hcmds[0].upper() == 'ACT'):
			if (loggedgetaccess(sock,user,chan,'CHANNEL') >= 1):
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(ACT)- This command will cause the bot to do a action on a channel")
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(ACT)- Command Structure: {0}{1} act <channel> <action>".format(settings['pvtcom'],settings['signal']))
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(ACT)- Command Structure: {0}{1} act <action>".format(settings['chancom'],settings['signal']))
			else:
				buildmsg(sock,'ERROR',user,chan,'PRIV','NOACCESSHELP')
		elif (hcmds[0].upper() == 'ACCOUNT'):
			if (islogged(sock,user) == 'TRUE'):
				if (len(hcmds) >= 2):
					if (hcmds[1].upper() == 'CHGPASS'):
						buildmsg(sock,'HELP',user,chan,'PRIV',"-(ACCOUNT)-(CHGPASS)- This Command will allow you to change your password")
						buildmsg(sock,'HELP',user,chan,'PRIV',"-(ACCOUNT)-(CHGPASS)- Command Structure: {0}{1} account chgpass <old pass> <new pass>".format(settings['pvtcom'],settings['signal']))
					elif (hcmds[1].upper() == 'MSGTYPE'):
						buildmsg(sock,'HELP',user,chan,'PRIV',"-(ACCOUNT)-(MSGTYPE)- This Command will allow you to change your Message Type")
						buildmsg(sock,'HELP',user,chan,'PRIV',"-(ACCOUNT)-(MSGTYPE)- Command Structure: {0}{1} account msgtype <notice/msg>".format(settings['pvtcom'],settings['signal']))
					else:
						buildmsg(sock,'ERROR',user,chan,'PRIV',"-(ACCOUNT)- The help topic account {0} is not in the database".format(hcmds[1]))
				else:
					buildmsg(sock,'HELP',user,chan,'PRIV',"-(ACCOUNT)- This Command will allow the user to do some modifications to their account")
					buildmsg(sock,'HELP',user,chan,'PRIV',"-(ACCOUNT)- Command Structure: {0}{1} account <chgpass/msgtype>".format(settings['pvtcom'],settings['signal']))
					buildmsg(sock,'HELP',user,chan,'PRIV',"-(ACCOUNT)- Topics available: chgpass msgtype")
			else:
				buildmsg(sock,'ERROR',user,chan,'PRIV','NOTLOGGED')
		elif (hcmds[0].upper() == 'LOGOUT'):
			if (islogged(sock,user) == 'TRUE'):
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(LOGOUT)- This Command will logout from the bot, this is the only command that works with users that is allowed in channel")
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(LOGOUT)- Command Structure: {0}{1} logout".format(settings['pvtcom'],settings['signal']))
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(LOGOUT)- Command Structure: {0}{1} logout".format(settings['pvtcom'],settings['signal']))
			else:
				buildmsg(sock,'ERROR',user,chan,'PRIV','NOTLOGGED')
		elif (hcmds[0].upper() == 'LOGIN'):
			if (islogged(sock,user) == 'FALSE'):
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(LOGIN)- This Command will login to the bot, should the username and password be right")
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(LOGIN)- Command Structure: {0}{1} login <username> <password>".format(settings['pvtcom'],settings['signal']))
			else:
				buildmsg(sock,'ERROR',user,chan,'PRIV','LOGGED')
		elif (hcmds[0].upper() == 'REGISTER'):
			if (islogged(sock,user) == 'FALSE'):
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(REGISTER)- This Command will register a user to the bot if that username doesn't already exists")
				buildmsg(sock,'HELP',user,chan,'PRIV',"-(REGISTER)- Command Structure: {0}{1} register <username> <password>".format(settings['pvtcom'],settings['signal']))
			else:
				buildmsg(sock,'ERROR',user,chan,'PRIV','LOGGED')		
		elif (hcmds[0].upper() == 'HELP'):
			buildmsg(sock,'HELP',user,chan,'PRIV',"-(HELP)- This Command Displays The Help System and Certain Command information")
			buildmsg(sock,'HELP',user,chan,'PRIV',"-(HELP)- Command Structure: {0}{1} help <channel> <topic>".format(settings['pvtcom'],settings['signal']))
			#buildmsg(sock,'HELP',user,chan,'PRIV',"-(HELP)- Command Structure: {0}{1} help <channel> <topic>".format(settings['dcccom'],settings['signal']))
			buildmsg(sock,'HELP',user,chan,'PRIV',"-(HELP)- Command Structure: {0}{1} help <topic>".format(settings['chancom'],settings['signal']))
		elif (hcmds[0].upper() == 'WHOIS'):
			buildmsg(sock,'HELP',user,chan,'PRIV',"-(WHOIS)- This Command will send you a whois on the <nick> you choose")
			buildmsg(sock,'HELP',user,chan,'PRIV',"-(WHOIS)- Command Structure: {0}{1} whois <channel> <nick>".format(settings['pvtcom'],settings['signal']))
			#buildmsg(sock,'HELP',user,chan,'PRIV',"-(WHOIS)- Command Structure: {0}{1} whois <channel> <nick>".format(settings['dcccom'],settings['signal']))
			buildmsg(sock,'HELP',user,chan,'PRIV',"-(WHOIS)- Command Structure: {0}{1} whois <nick>".format(settings['chancom'],settings['signal']))
		elif (hcmds[0].upper() == 'WHOAMI'):
			buildmsg(sock,'HELP',user,chan,'PRIV',"-(WHOAMI)- This Command will send you a whois on your current logged in user account")
			buildmsg(sock,'HELP',user,chan,'PRIV',"-(WHOAMI)- Command Structure: {0}{1} whoami <channel>".format(settings['pvtcom'],settings['signal']))
			#buildmsg(sock,'HELP',user,chan,'PRIV',"-(WHOAMI)- Command Structure: {0}{1} whoami <channel>".format(settings['dcccom'],settings['signal']))
			buildmsg(sock,'HELP',user,chan,'PRIV',"-(WHOAMI)- Command Structure: {0}{1} whoami".format(settings['chancom'],settings['signal']))		
		else:
			buildmsg(sock,'ERROR',user,chan,'PRIV',"The help topic {0} is not in the database".format(hcmds[0]))
	else:
		buildmsg(sock,'HELP',user,chan,'PRIV',"The bot has the following Commands Available")
		if (islogged(sock,user) == 'TRUE'):
			if (loggedgetaccess(sock,user,chan,'GLOBAL') >= 7):
				buildmsg(sock,'HELP',user,chan,'PRIV',"Creator Level Access (7) Only (Due to dangerous level to bot and system):")
				buildmsg(sock,'HELP',user,chan,'PRIV',"Raw Rawdb")
			if (loggedgetaccess(sock,user,chan,'CHANNEL') >= 6):
				#Master & Creator Commands 6/7 Global, 6 Server, 6 Channel
				buildmsg(sock,'HELP',user,chan,'PRIV',"Master Level Access (6):")
				if (loggedgetaccess(sock,user,chan,'GLOBAL') >= 6):
					buildmsg(sock,'HELP',user,chan,'PRIV',"Exit Rehash Settings") #Server User
				if (loggedgetaccess(sock,user,chan,'SERVER') >= 6):
					buildmsg(sock,'HELP',user,chan,'PRIV',"Quit") #Channel
				if (loggedgetaccess(sock,user,chan,'CHANNEL') >= 6):
					blarg = 1 #don't think there is gonna be any of these
			if (loggedgetaccess(sock,user,chan,'CHANNEL') >= 5):
				#Owner Commands - 5 Global, 6 Server, 5 Channel
				buildmsg(sock,'HELP',user,chan,'PRIV',"Owner Level Access (5):")
				if (loggedgetaccess(sock,user,chan,'GLOBAL') >= 5):
					blarg = 1
				if (loggedgetaccess(sock,user,chan,'SERVER') >= 5):
					blarg = 1
				if (loggedgetaccess(sock,user,chan,'CHANNEL') >= 5):
					buildmsg(sock,'HELP',user,chan,'PRIV',"MOwner Owner MDeOwner DeOwner Ownerme DeOwnerme")
					buildmsg(sock,'HELP',user,chan,'PRIV',"MProtect Protect MDeProtect DeProtect")
			if (loggedgetaccess(sock,user,chan,'CHANNEL') >= 4):
				#Protected Commands - 4 Global, 4 Server, 4 Channel
				buildmsg(sock,'HELP',user,chan,'PRIV',"Protected Level Access (4):")
				if (loggedgetaccess(sock,user,chan,'GLOBAL') >= 4):
					blarg = 1
				if (loggedgetaccess(sock,user,chan,'SERVER') >= 4):
					blarg = 1
				if (loggedgetaccess(sock,user,chan,'CHANNEL') >= 4):
					buildmsg(sock,'HELP',user,chan,'PRIV',"Protectme DeProtectme")
					#Access Protectme DeProtectme
			if (loggedgetaccess(sock,user,chan,'CHANNEL') >= 3):
				#Op Commands - 3 Global, 3 Server, 3 Channel
				buildmsg(sock,'HELP',user,chan,'PRIV',"Op Level Access (3):")
				buildmsg(sock,'HELP',user,chan,'PRIV',"MOp Op MDeOp DeOp Opme DeOpme")
				buildmsg(sock,'HELP',user,chan,'PRIV',"MHalfop Halfop MDeHalfop DeHalfop")
			if (loggedgetaccess(sock,user,chan,'CHANNEL') >= 2):
				#Half-Op Commands - 2 Global, 2 Server, 2 Channel
				buildmsg(sock,'HELP',user,chan,'PRIV',"Half-Op Level Access (2):")
				buildmsg(sock,'HELP',user,chan,'PRIV',"Halfopme DeHalfopme MVoice Voice MDeVoice DeVoice")
				#channel Kick Ban
			if (loggedgetaccess(sock,user,chan,'CHANNEL') >= 1):
				#Voice Commands - 1 Global, 1 Server, 1 Channel
				buildmsg(sock,'HELP',user,chan,'PRIV',"Voice Level Access (1):")
				buildmsg(sock,'HELP',user,chan,'PRIV',"Voiceme DeVoiceme Say Act")		
			#Logged in with - 0 Global, 0 Server, 0 Channel
			buildmsg(sock,'HELP',user,chan,'PRIV',"Logged In Access (0):")
			buildmsg(sock,'HELP',user,chan,'PRIV',"Account Logout")
		else :
			#Logged out with - 0 Global, 0 Server, 0 Channel
			buildmsg(sock,'HELP',user,chan,'PRIV',"Logged out Access (0):")
			buildmsg(sock,'HELP',user,chan,'PRIV',"Login Register")
		#Anyone Commands - 0 global, 0 server, 0 channel
		buildmsg(sock,'HELP',user,chan,'PRIV',"Anyone Can Access (0):")
		buildmsg(sock,'HELP',user,chan,'PRIV',"Help Whoami Whois")
		buildmsg(sock,'HELP',user,chan,'PRIV',"Pvt Command: {0}{2} help <channel> <topic>, Channel Command: {1}{2} help <topic>".format(settings['pvtcom'],settings['chancom'],settings['signal']))
	buildmsg(sock,'HELP',user,chan,'PRIV',"End Of {0} help system".format(settings['botname']))
		
def rawp(sock,extra):
	#buildmsg(sock,'NORMAL',user,chan,'PRIV',output) #types are NORMAL, HELP, ERROR  mtype are PRIV, CHAN
	debug(sock,"this is temp")
	
def parse_data(sock,data):
	screenoutput(sock,'in',data)
	incom = data
	incom = incom.split(' ')
	raw = data
	raw = raw.split(' ')
	stripcount = len(incom)
	while (stripcount):
		stripcount = stripcount - 1	
		incom[stripcount] = incom[stripcount].strip(':')
		incom[stripcount] = incom[stripcount].strip('\r')
		incom[stripcount] = incom[stripcount].strip('\n')
	stripcount = len(raw)
	while (stripcount):
		stripcount = stripcount - 1	
		raw[stripcount] = raw[stripcount].strip('\r')
		raw[stripcount] = raw[stripcount].strip('\n')
	sender = incom[0].split('!')
	sender = sender[0]
	if (incom[0] == 'PING'):
		sts(sock,"PONG :{0}".format(incom[1]))
		mysockets[sock]['lastping'] = time.time()
	elif (incom[0] == 'ERROR'):
		if ((mysockets[sock]['lastcmd'] == 'QUIT') or (mysockets[sock]['lastcmd'] == 'EXIT') or (mysockets[sock]['lastcmd'] == 'RELOAD')):
			mysocket[sock].close()
			del mysocket[sock]
			del mysockets[sock]
		else:
			mysocket[sock].close()
			doconnection(sock)
			mysockets[sock]['lastping'] = time.time()
	elif (len(incom) >= 2):
		#start the numerics
		if (incom[1] == '001'):
			#debug(sock,"Numeric 001 - Welcome to server")
			mysockets[sock]['networkname'] = incom[6]
			mysockets[sock]['connectumask'] = incom[9]
			sts(sock,"MODE {0} +B".format(mysockets[sock]['nick']))
			operupcheck(sock)
			if (mysockets[sock]['identified'] == 'TRUE'):
				autojoinchannels(sock)
		elif (incom[1] == '002'):
			#debug(sock,"Numeric 002 - host is server and version")
			blarg = 1
		elif (incom[1] == '003'):
			#debug(sock,"Numeric 003 - created")
			blarg = 1
		elif (incom[1] == '004'):
			#debug(sock,"Numeric 004 - server var usermode charmode")
			mysockets[sock]['connectaddress'] = incom[3]
			mysockets[sock]['sversion'] = incom[4]
			mysockets[sock]['connectumodes'] = incom[5]
			mysockets[sock]['connectcmodes'] = incom[6]
			modeprocessor_user(sock,'umode',incom[5])
		elif (incom[1] == '005'):
			#debug(sock,"Numeric 005 - map")
			i = 0
			while (i < len(incom)):
				tmpdata = incom[i].split('=')
				#if (tmpdata[0] == 'UHNAMES'):
				if (tmpdata[0] == 'MAXCHANNELS'): mysockets[sock]['maxchannels'] = int(tmpdata[1])
				elif (tmpdata[0] == 'CHANLIMIT'): mysockets[sock]['chanlimit'] = tmpdata[1]
				elif (tmpdata[0] == 'MAXLIST'): mysockets[sock]['maxlist'] = tmpdata[1]
				elif (tmpdata[0] == 'NICKLEN'): mysockets[sock]['nicklen'] = int(tmpdata[1])
				elif (tmpdata[0] == 'CHANNELLEN'): mysockets[sock]['channellen'] = int(tmpdata[1])
				elif (tmpdata[0] == 'TOPICLEN'): mysockets[sock]['topiclen'] = int(tmpdata[1])
				elif (tmpdata[0] == 'KICKLEN'): mysockets[sock]['kicklen'] = int(tmpdata[1])
				elif (tmpdata[0] == 'AWAYLEN'): mysockets[sock]['awaylen'] = int(tmpdata[1])
				elif (tmpdata[0] == 'MAXTARGETS'): mysockets[sock]['maxtargets'] = int(tmpdata[1])
				elif (tmpdata[0] == 'MODES'): mysockets[sock]['modespl'] = int(tmpdata[1])
				elif (tmpdata[0] == 'CHANTYPES'): mysockets[sock]['chantypes'] = tmpdata[1]
				elif (tmpdata[0] == 'PREFIX'): mysockets[sock]['prefix'] = tmpdata[1]
				elif (tmpdata[0] == 'CHANMODES'): mysockets[sock]['chanmodes'] = tmpdata[1]
				elif (tmpdata[0] == 'EXTBAN'): mysockets[sock]['extban'] = tmpdata[1]
				else: blarg = 1
				i = i + 1
				
		elif (incom[1] == '007'):
			debug(sock,"Numeric 007 - end of map")
		elif (incom[1] == '008'):
			#debug(sock,"Numeric 008 - num - server notice mask")
			if (incom[2] == mysockets[sock]['nick']):
				modeprocessor_user(sock,'smask',incom[6])
		
		elif (incom[1] == '010'):
			#debug(sock,"Numeric 010 - JumpServer")
			mysockets[sock]['connection']['address'] = incom[3]
			mysockets[sock]['connection']['serverport'] = int(incom[4])

		elif (incom[1] == '211'):
			debug(sock,"Numeric 211 - connection sendq sentmsg sentbyte recdmsg recdbyte :open")
		elif (incom[1] == '212'):
			debug(sock,"Numeric 212 - command uses bytes")
		elif (incom[1] == '213'):
			debug(sock,"Numeric 213 - C address * server port class")
		elif (incom[1] == '214'):
			debug(sock,"Numeric 214 - N address * server port class")
		elif (incom[1] == '215'):
			debug(sock,"Numeric 215 - I ipmask * hostmask port class")
		elif (incom[1] == '216'):
			debug(sock,"Numeric 216 - k address * username details")
		elif (incom[1] == '217'):
			debug(sock,"Numeric 217 - P port ?? ??")
		elif (incom[1] == '218'):
			debug(sock,"Numeric 218 - Y class ping freq maxconnect sendq")
		elif (incom[1] == '219'):
			#debug(sock,"Numeric 219 - End of /stats report")
			blarg = 1
		
		elif (incom[1] == '221'):
			if (incom[2] == mysockets[sock]['nick']):
				modeprocessor_user(sock,'umode',incom[3])
		elif (incom[1] == '222'):
			debug(sock,"Numeric 222 - mask :comment")
		elif (incom[1] == '223'):
			debug(sock,"Numeric 223 - E hostmask * username ?? ??")
		elif (incom[1] == '224'):
			debug(sock,"Numeric 224 - D ipmask * username ?? ??")
		
		elif (incom[1] == '241'):
			debug(sock,"Numeric 241 - L address * server ?? ??")
		elif (incom[1] == '242'):
			debug(sock,"Numeric 242 - :Server Up num days, time")
		elif (incom[1] == '243'):
			if (incom[6] == mysockets[sock]['server']['botoper']):
				modeprocessor_user(sock,'oflags','+'+incom[7])
		elif (incom[1] == '244'):
			debug(sock,"Numeric 244 - H address * server ?? ??")
		
		elif (incom[1] == '247'):
			debug(sock,"Numeric 247 - G address timestamp :reason")
		elif (incom[1] == '248'):
			debug(sock,"Numeric 248 - U host * ?? ?? ??")
		elif (incom[1] == '249'):
			debug(sock,"Numeric 249 - :info")
		elif (incom[1] == '250'):
			#debug(sock,"Numeric 250 - highest connection count")
			blarg = 1
		elif (incom[1] == '251'):
			#debug(sock,"Numeric 251 - there are x users online")
			blarg = 1
		elif (incom[1] == '252'):
			#debug(sock,"Numeric 252 - number of operators")
			blarg = 1
		elif (incom[1] == '253'):
			#debug(sock,"Numeric 253 - number of unknown connections")
			blarg = 1
		elif (incom[1] == '254'):
			#debug(sock,"Numeric 254 - number of channels")
			blarg = 1
		elif (incom[1] == '255'):
			#debug(sock,"Numeric 255 - have x clients and x servers")
			blarg = 1
		elif (incom[1] == '256'):
			debug(sock,"Numeric 256 - :Administrative info about server")
		elif (incom[1] == '257'):
			debug(sock,"Numeric 257 - :info")
		elif (incom[1] == '258'):
			debug(sock,"Numeric 258 - :info")
		elif (incom[1] == '259'):
			debug(sock,"Numeric 259 - :info")
		
		elif (incom[1] == '263'):
			debug(sock,"Numeric 263 - :Server load is temporarily too heavy. Please wait a while and try again.")
	
		elif (incom[1] == '265'):
			#debug(sock,"Numeric 265 - :Current local users: curr Max: max")
			blarg = 1
		elif (incom[1] == '266'):
			#debug(sock,"Numeric 266 - :Current global users: curr Max: max")
			blarg = 1
		
		elif (incom[1] == '271'):
			debug(sock,"Numeric 271 - nick mask")
		elif (incom[1] == '272'):
			debug(sock,"Numeric 272 - nick :End of Silence List")
		
		elif (incom[1] == '280'):
			debug(sock,"Numeric 280 - address timestamp reason")
		elif (incom[1] == '281'):
			debug(sock,"Numeric 281 - :End of G-line List")
		
		elif (incom[1] == '290'):
			debug(sock,"Numeric 290 - :num ***** topic *****")
		elif (incom[1] == '291'):
			debug(sock,"Numeric 291 - :text")
		elif (incom[1] == '292'):
			debug(sock,"Numeric 292 - : ***** Go to #dalnethelp if you have any further questions *****")
		elif (incom[1] == '293'):
			debug(sock,"Numeric 293 - :text")
		elif (incom[1] == '294'):
			debug(sock,"Numeric 294 - :Your help-request has been forwarded to Help Operators")
		
		elif (incom[1] == '298'):
			debug(sock,"Numeric 298 - nick :Nickname conflict has been resolved")
			
		elif (incom[1] == '301'):
			debug(sock,"Numeric 301 - nick :away")
		elif (incom[1] == '302'):
			debug(sock,"Numeric 302 - :userhosts")
		elif (incom[1] == '303'):
			debug(sock,"Numeric 303 - :nicknames")
		elif (incom[1] == '304'):
			debug(sock,"Numeric 304 - Unknown Raw Code")			
		elif (incom[1] == '305'):
			debug(sock,"Numeric 305 - :You are no longer marked as being away")
		elif (incom[1] == '306'):
			debug(sock,"Numeric 306 - :You have been marked as being away")
		elif (incom[1] == '307'):
			debug(sock,"Numeric 307 - :userips")
		
		elif (incom[1] == '310'):
			debug(sock,"Numeric 310 - nick :looks very helpful")
		elif (incom[1] == '311'):
			debug(sock,"Numeric 311 - nick username address * :info")
		elif (incom[1] == '312'):
			debug(sock,"Numeric 312 - nick server :info")
		elif (incom[1] == '313'):
			debug(sock,"Numeric 313 - nick :is an IRC Operator")
		elif (incom[1] == '314'):
			debug(sock,"Numeric 314 - nick username address * :info")
		elif (incom[1] == '315'):
			debug(sock,"Numeric 315 - request :End of /WHO list.")
		
		elif (incom[1] == '317'):
			debug(sock,"Numeric 317 - nick seconds signon :info")
		elif (incom[1] == '318'):
			debug(sock,"Numeric 318 - request :End of /WHOIS list.")
		elif (incom[1] == '319'):
			debug(sock,"Numeric 319 - nick :channels")
		
		elif (incom[1] == '321'):
			debug(sock,"Numeric 321 - Channel :Users Name")
		elif (incom[1] == '322'):
			debug(sock,"Numeric 322 - channel users :topic")
		elif (incom[1] == '323'):
			debug(sock,"Numeric 323 - :End of /LIST")
		elif (incom[1] == '324'):
			modeprocessor_chan(sock,sender,rl(incom[3]),incom[4:])
			if (chanmodes(sock,rl(incom[3])) != 'NULL'):
				sts(sock,"MODE {0} {1}".format(incom[3],chanmodes(sock,rl(incom[3]))))

		elif (incom[1] == '328'):
			debug(sock,"Numeric 328 - channel :url")
		elif (incom[1] == '329'):
			#debug(sock,"Numeric 329 - Channel Creation time")
			#-1-> :chewy.chewynet.co.uk 329 ^chewy_god^ #home 1280495592
			#DEBUG: ChewyNet ['chewy.chewynet.co.uk', '329', '^chewy_god^', '#home', '1280495592']
			blarg = 1

		elif (incom[1] == '331'):
			debug(sock,"Numeric 331 - No topic is set")
		elif (incom[1] == '332'):
			debug(sock,"Numeric 332 - Topic")
		elif (incom[1] == '333'):
			debug(sock,"Numeric 333 - Nickname time")

		elif (incom[1] == '340'):
			debug(sock,"Numeric 340 - nick :nickname=+user@IP.address")
		elif (incom[1] == '341'):
			debug(sock,"Numeric 341 - nick channel")
	
		elif (incom[1] == '346'):
			#DEBUG: ChewyNet ['chewy.chewynet.co.uk', '346', '^chewy_god^', '#home', 'doe!*@*', 'chewyb_13', '1280533501']
			#debug(sock,"Numeric 346 - Channel Invex list
			try: mysockets[sock]['channels'][rl(incom[3])]['INVEX']
			except: mysockets[sock]['channels'][rl(incom[3])]['INVEX'] = dict()
			mysockets[sock]['channels'][rl(incom[3])]['INVEX'][incom[4]] = 'TRUE'
		elif (incom[1] == '347'):
			#debug(sock,"Numeric 347 - End of Channel Invite List")		
			blarg = 1		
		elif (incom[1] == '348'):
			#DEBUG: ChewyNet ['chewy.chewynet.co.uk', '348', '^chewy_god^', '#home', 'blond!*@*', 'chewyb_13', '1280533501']
			#debug(sock,"Numeric 348 - Channel Exception list
			try: mysockets[sock]['channels'][rl(incom[3])]['EXCEPT']
			except: mysockets[sock]['channels'][rl(incom[3])]['EXCEPT'] = dict()
			mysockets[sock]['channels'][rl(incom[3])]['EXCEPT'][incom[4]] = 'TRUE'		
		elif (incom[1] == '349'):
			#debug(sock,"Numeric 349 - End of Channel Exception List")
			blarg = 1

		elif (incom[1] == '351'):
			debug(sock,"Numeric 351 - version.debug server :info")
		elif (incom[1] == '352'):
			debug(sock,"Numeric 352 - channel username address server nick flags :hops info")
		elif (incom[1] == '353'):
			#debug(sock,"Numeric 353 - Names")
			try: mysockets[sock]['channels'][rl(incom[4])]
			except: mysockets[sock]['channels'][rl(incom[4])] = dict()
			tmpdata = incom[5:]
			#debug(sock,tmpdata)
			i = 0
			while (i < len(tmpdata)):
				if (tmpdata[i] == ''): break
				try: mysockets[sock]['channels'][rl(incom[4])]['users']
				except:	mysockets[sock]['channels'][rl(incom[4])]['users'] = dict()
				if (tmpdata[i][0] == '~'):
					tmpuser = tmpdata[i][1:]
					tmpmode = 'FOP'
				elif (tmpdata[i][0] == '&'):
					tmpuser = tmpdata[i][1:]
					tmpmode = 'SOP'
				elif (tmpdata[i][0] == '@'):
					tmpuser = tmpdata[i][1:]
					tmpmode = 'OP'
				elif (tmpdata[i][0] == '%'):
					tmpuser = tmpdata[i][1:]
					tmpmode = 'HOP'
				elif (tmpdata[i][0] == '+'):
					tmpuser = tmpdata[i][1:]
					tmpmode = 'VOICE'
				else:
					tmpuser = tmpdata[i]
					tmpmode = 'REGULAR'
				try: mysockets[sock]['channels'][rl(incom[4])]['users'][tmpuser]
				except: mysockets[sock]['channels'][rl(incom[4])]['users'][tmpuser] = dict()
				mysockets[sock]['channels'][rl(incom[4])]['users'][tmpuser]['inchan'] = 'TRUE'
				mysockets[sock]['channels'][rl(incom[4])]['users'][tmpuser][tmpmode] = 'TRUE'
				i = i + 1

		elif (incom[1] == '364'):
			debug(sock,"Numeric 364 - server hub :hops info")
		elif (incom[1] == '365'):
			debug(sock,"Numeric 365 - mask :End of /LINKS list.")
		elif (incom[1] == '366'):
			#debug(sock,"Numeric 366 - End of Names")
			blarg = 1		
		elif (incom[1] == '367'):
			#DEBUG: ChewyNet ['chewy.chewynet.co.uk', '367', '^chewy_god^', '#home', 'blarg!*@*', 'chewyb_13', '1280533501']
			#debug(sock,"Numeric 367 - Channel Ban list
			try: mysockets[sock]['channels'][rl(incom[3])]['BAN']
			except: mysockets[sock]['channels'][rl(incom[3])]['BAN'] = dict()
			mysockets[sock]['channels'][rl(incom[3])]['BAN'][incom[4]] = 'TRUE'
		elif (incom[1] == '368'):
			#debug(sock,"Numeric 368 - End of Channel Ban List")
			blarg = 1
		elif (incom[1] == '369'):
			debug(sock,"Numeric 369 - request :End of WHOWAS")
		
		elif (incom[1] == '371'):
			debug(sock,"Numeric 371 - :info")
		elif (incom[1] == '372'):
			#debug(sock,"Numeric 372 - MOTD info")
			blarg = 1

		elif (incom[1] == '374'):
			debug(sock,"Numeric 374 - :End of /INFO list.")
		elif (incom[1] == '375'):
			#debug(sock,"Numeric 375 - server motd")
			blarg = 1
		elif (incom[1] == '376'):
			#debug(sock,"Numeric 376 - end of motd")
			blarg = 1
		elif (incom[1] == '377'):
			debug(sock,"Numeric 377 - info")
		elif (incom[1] == '378'):
			debug(sock,"Numeric 378 - info")
		
		elif (incom[1] == '381'):
			if (mysockets[sock]['isoper'] == 'ATTEMPTING'):
				mysockets[sock]['isoper'] = 'TRUE'
				sts(sock,"STATS O")
		elif (incom[1] == '382'):
			debug(sock,"Numeric 382 - file :Rehashing")
		
		elif (incom[1] == '391'):
			debug(sock,"Numeric 391 - server :time")
				
		elif (incom[1] == '401'):
			debug(sock,"Numeric 401 - No such nick")
		elif (incom[1] == '402'):
			debug(sock,"Numeric 402 - server :No such server")
		elif (incom[1] == '403'):
			debug(sock,"Numeric 403 - No such channel")
		elif (incom[1] == '404'):
			debug(sock,"Numeric 404 - channel :Cannot send to channel")
		elif (incom[1] == '405'):
			debug(sock,"Numeric 405 - channel :You have joined too many channels")
		elif (incom[1] == '406'):
			debug(sock,"Numeric 406 - nickname :There was no such nickname")
		elif (incom[1] == '407'):
			debug(sock,"Numeric 407 - target :Duplicate recipients. No message delivered")
		elif (incom[1] == '408'):
			debug(sock,"Numeric 408 - nickname #channel :You cannot use colors on this channel. Not sent: text")
		elif (incom[1] == '409'):
			debug(sock,"Numeric 409 - :No origin specified")
		
		elif (incom[1] == '411'):
			debug(sock,"Numeric 411 - :No recipient given (command)")
		elif (incom[1] == '412'):
			debug(sock,"Numeric 412 - :No text to send")
		elif (incom[1] == '413'):
			debug(sock,"Numeric 413 - mask :No toplevel domain specified")
		elif (incom[1] == '414'):
			debug(sock,"Numeric 414 - mask :Wildcard in toplevel Domain")
		
		elif (incom[1] == '416'):
			debug(sock,"Numeric 416 - command :Too many lines in the output, restrict your query")
		
		elif (incom[1] == '421'):
			debug(sock,"Numeric 421 - command :Unknown command")
		elif (incom[1] == '422'):
			#debug(sock,"Numeric 422 - MOTD missing")
			blarg = 1
		elif (incom[1] == '423'):
			debug(sock,"Numeric 423 - server :No administrative info available")
		
		elif (incom[1] == '431'):
			debug(sock,"Numeric 431 - :No nickname given")
		elif (incom[1] == '432'):
			debug(sock,"Numeric 432 - nickname :Erroneus Nickname")			
		elif (incom[1] == '433'):
			if (incom[3] == mysockets[sock]['nick']):
				if (mysockets[sock]['nick'] == mysockets[sock]['server']['nick']):
					sts(sock,"NICK {0}".format(mysockets[sock]['server']['bnick']))
					mysockets[sock]['nick'] = mysockets[sock]['server']['bnick']
				if (mysockets[sock]['nick'] == mysockets[sock]['server']['bnick']):
					sts(sock,"NICK {0}".format(mysockets[sock]['server']['nick']))
					mysockets[sock]['nick'] = mysockets[sock]['server']['nick']

		elif (incom[1] == '436'):
			debug(sock,"Numeric 436 - nickname :Nickname collision KILL")
		elif (incom[1] == '437'):
			debug(sock,"Numeric 437 - channel :Cannot change nickname while banned on channel")
		elif (incom[1] == '438'):
			debug(sock,"Numeric 438 - nick :Nick change too fast. Please wait sec seconds.")
		elif (incom[1] == '439'):
			debug(sock,"Numeric 439 - target :Target change too fast. Please wait sec seconds.")
			
		elif (incom[1] == '441'):
			debug(sock,"Numeric 441 - nickname channel :They aren't on that channel")
		elif (incom[1] == '442'):
			debug(sock,"Numeric 442 - You are not on that channel")
		elif (incom[1] == '443'):
			debug(sock,"Numeric 443 - nickname channel :is already on channel")
		
		elif (incom[1] == '445'):
			debug(sock,"Numeric 445 - :SUMMON has been disabled")
		elif (incom[1] == '446'):
			debug(sock,"Numeric 446 - :USERS has been disabled")
		
		elif (incom[1] == '451'):
			debug(sock,"Numeric 451 - command :Register first.")
		
		elif (incom[1] == '455'):
			debug(sock,"Numeric 455 - :Your username ident contained the invalid character(s) chars and has been changed to new. Please use only the characters 0-9 a-z A-Z _ - or . in your username. Your username is the part before the @ in your email address.")
		
		elif (incom[1] == '461'):
			debug(sock,"Numeric 461 - command :Not enough parameters")
		elif (incom[1] == '462'):
			debug(sock,"Numeric 462 - :You may not reregister")
		
		elif (incom[1] == '467'):
			debug(sock,"Numeric 467 - channel :Channel key already set")
		elif (incom[1] == '468'):
			debug(sock,"Numeric 468 - channel :Only servers can change that mode")
			
		elif (incom[1] == '471'):
			#debug(sock,"Numeric 471 - channel :Cannot join channel (+l)")
			if (mysockets[sock]['identified'] == 'TRUE'):
				sts(sock,"PRIVMSG ChanServ :INVITE {0}".format(incom[3]))
				joinchan(sock,rl(incom[3]))
			elif (mysockets[sock]['isoper'] == 'TRUE'):
				sts(sock,"SAJOIN {0} {1}".format(mysockets[sock]['nick'],incom[3]))
			else:
				blarg = 1
		elif (incom[1] == '472'):
			debug(sock,"Numeric 472 - char :is unknown mode char to me")
		elif (incom[1] == '473'):
			#debug(sock,"Numeric 474 - channel :Cannot join channel (+i)")
			if (mysockets[sock]['identified'] == 'TRUE'):
				sts(sock,"PRIVMSG ChanServ :INVITE {0}".format(incom[3]))
				joinchan(sock,rl(incom[3]))
		elif (incom[1] == '474'):
			#debug(sock,"Numeric 474 - channel :Cannot join channel (+b)")
			if (mysockets[sock]['identified'] == 'TRUE'):
				sts(sock,"PRIVMSG ChanServ :UNBAN {0}".format(incom[3]))
				joinchan(sock,rl(incom[3]))
			elif (mysockets[sock]['isoper'] == 'TRUE'):
				sts(sock,"SAJOIN {0} {1}".format(mysockets[sock]['nick'],incom[3]))
			else:
				blarg = 1	
		elif (incom[1] == '475'):
			#debug(sock,"Numeric 475 - channel :Cannot join channel (+k)")
			if (mysockets[sock]['identified'] == 'TRUE'):
				sts(sock,"PRIVMSG ChanServ :INVITE {0}".format(incom[3]))
				joinchan(sock,rl(incom[3]))
			elif (mysockets[sock]['isoper'] == 'TRUE'):
				sts(sock,"SAJOIN {0} {1}".format(mysockets[sock]['nick'],incom[3]))
			else:
				blarg = 1
		
		elif (incom[1] == '477'):
			debug(sock,"Numeric 477 - channel :You need a registered nick to join that channel.")
		elif (incom[1] == '478'):
			debug(sock,"Numeric 478 - channel ban :Channel ban/ignore list is full")
		
		elif (incom[1] == '481'):
			debug(sock,"Numeric 481 - :Permission Denied- You're not an IRC operator")					
		elif (incom[1] == '482'):
			debug(sock,"Numeric 482 - channel :You're not channel operator")
		elif (incom[1] == '483'):
			debug(sock,"Numeric 483 - :You cant kill a server!")
		elif (incom[1] == '484'):
			debug(sock,"Numeric 484 - nick channel :Cannot kill, kick or deop channel service")
		elif (incom[1] == '485'):
			debug(sock,"Numeric 485 - channel :Cannot join channel (reason)")
			
		elif (incom[1] == '491'):
			debug(sock,"Numeric 491 - :No O-lines for your host")

		elif (incom[1] == '499'):
			#debug(sock,"Numeric 499 - Not owner of the channel")
			blarg = 1
			
		elif (incom[1] == '501'):
			debug(sock,"Numeric 501 - :Unknown MODE flag")
		elif (incom[1] == '502'):
			debug(sock,"Numeric 502 - :Cant change mode for other users")
		
		elif (incom[1] == '510'):
			debug(sock,"Numeric 510 - :You must resolve the nickname conflict before you can proceed")
		elif (incom[1] == '511'):
			debug(sock,"Numeric 511 - mask :Your silence list is full")
		elif (incom[1] == '512'):
			debug(sock,"Numeric 512 - address :No such gline")
		elif (incom[1] == '513'):
			debug(sock,"Numeric 513 - If you can't connect, type /QUOTE PONG code or /PONG code")
		
		elif (incom[1] == '600'):
			debug(sock,"Numeric 600 - nick userid host time :logged offline")
		elif (incom[1] == '601'):
			debug(sock,"Numeric 601 - nick userid host time :logged online")
		elif (incom[1] == '602'):
			debug(sock,"Numeric 602 - nick userid host time :stopped watching")
		elif (incom[1] == '603'):
			debug(sock,"Numeric 603 - :You have mine and are on other WATCH entries")
		elif (incom[1] == '604'):
			debug(sock,"Numeric 604 - nick userid host time :is online")
		elif (incom[1] == '605'):
			debug(sock,"Numeric 605 - nick userid host time :is offline")
		elif (incom[1] == '606'):
			debug(sock,"Numeric 606 - :nicklist")
		
		elif (incom[1] == '972'):
			#debug(sock,"Numeric 972 - Can't kick user due to +q")
			blarg = 1
		
		#start normal
		elif (incom[1].upper() == 'JOIN'):
			try: mysockets[sock]['channels'][rl(incom[2])]
			except: mysockets[sock]['channels'][rl(incom[2])] = dict()
			try: mysockets[sock]['channels'][rl(incom[2])]['users']
			except: mysockets[sock]['channels'][rl(incom[2])]['users'] = dict()
			try: mysockets[sock]['channels'][rl(incom[2])]['users'][sender]
			except: mysockets[sock]['channels'][rl(incom[2])]['users'][sender] = dict()
			mysockets[sock]['channels'][rl(incom[2])]['users'][sender]['inchan'] = 'TRUE'
			if (sender == mysockets[sock]['nick']):
				if (checkchan(sock,rl(incom[2])) == 'FALSE'):
					sts(sock,"PART {0} :Not supposed to be in here".format(incom[2]))
				else:
					sts(sock,"MODE {0}".format(incom[2]))
					sts(sock,"MODE {0} +b".format(incom[2]))
					sts(sock,"MODE {0} +e".format(incom[2]))
					sts(sock,"MODE {0} +I".format(incom[2]))
			else:
				#debug(sock,"{0} joined channel {1}".format(sender,incom[2]))
				if (islogged(sock,sender) == 'TRUE'):
					if (len(tempdata[sock]) > 0):
						if (tempdata[sock][sender] == 'UHCHANGE'):
							loggedin[sock][sender]['umask'] = incom[0]
						del tempdata[sock][sender]
		elif (incom[1].upper() == 'PART'):
			del mysockets[sock]['channels'][rl(incom[2])]['users'][sender]['inchan']
			if (sender == mysockets[sock]['nick']):
				if (checkchan(sock,rl(incom[2])) == 'TRUE'):
					joinchan(sock,rl(incom[2]))
				else:
					del mysockets[sock]['channels'][rl(incom[2])]
				#debug(sock,"I parted channel {0}".format(incom[2]))
			else:
				#debug(sock,"{0} parted channel {1}".format(sender,incom[2]))
				if (islogged(sock,sender) == 'TRUE'):
					if (len(incom) >= 8):
						if ((incom[3] == 'Rejoining') and (incom[4] == 'because') and (incom[5] == 'of') and (incom[6] == 'user@host') and (incom[7] == 'change')):
							tempdata[sock][sender] = 'UHCHANGE'
		elif (incom[1].upper() == 'QUIT'):
			if (sender == mysockets[sock]['nick']):
				debug(sock,"I quit")
			else:
				#Still gotta make the netsplit detection coding for here *.*.*.* iswm $1 $2
				if (islogged(sock,sender) == 'TRUE'):
					botlog(sock,sender,'COMMON',"Auto-Logout for {0}({1})".format(sender,loggedin[sock][sender]['username']))
					del loggedin[sock][sender]
			if (len(mysockets[sock]['channels']) > 0):
				tmpckeys = mysockets[sock]['channels'].keys()
				for tmpckey in tmpckeys:
					if (len(mysockets[sock]['channels'][tmpckey]['users']) > 0):
						tmpuukeys = mysockets[sock]['channels'][tmpckey]['users'].keys()
						for tmpuukey in tmpuukeys:
							if (tmpuukey == sender):
								del mysockets[sock]['channels'][tmpckey]['users'][sender]
		elif (incom[1].upper() == 'KICK'):
			if (incom[3] == mysockets[sock]['nick']):
				if (checkchan(sock,rl(incom[2])) == 'TRUE'):
					joinchan(sock,rl(incom[2]))
			else:
				debug(sock,"Another user KICKed")
			del mysockets[sock]['channels'][rl(incom[2])]['users'][incom[3]]
		elif (incom[1].upper() == 'NICK'):
			if (sender == mysockets[sock]['nick']):
				debug(sock,"My nick changed --- AHHHHHHH")
			else:
				if (islogged(sock,sender) == 'TRUE'):
					tmpmask = incom[0].split('!')
					output = incom[2]+"!"
					output = output+tmpmask[1]
					loggedin[sock][incom[2]] = {'username': loggedin[sock][sender]['username'], 'msgtype': loggedin[sock][sender]['msgtype'], 'umask': output}
					del loggedin[sock][sender]
			tmpmodes = ['FOP', 'SOP', 'OP', 'HOP', 'VOICE', 'inchan']
			if (len(mysockets[sock]['channels']) > 0):
				tmpckeys = mysockets[sock]['channels'].keys()
				for tmpckey in tmpckeys:
					if (len(mysockets[sock]['channels'][tmpckey]['users']) > 0):
						tmpuukeys = mysockets[sock]['channels'][tmpckey]['users'].keys()
						for tmpuukey in tmpuukeys:
							if (tmpuukey == sender):
								if (len(mysockets[sock]['channels'][tmpckey]['users'][sender]) > 0):
									tmpukeys = mysockets[sock]['channels'][tmpckey]['users'][sender].keys()
									try: mysockets[sock]['channels'][tmpckey]['users'][incom[2]]
									except: mysockets[sock]['channels'][tmpckey]['users'][incom[2]] = dict()
									for tmpukey in tmpukeys:
										for tmpmode in tmpmodes:
											if (tmpukey == tmpmode):
												mysockets[sock]['channels'][tmpckey]['users'][incom[2]][tmpmode] = mysockets[sock]['channels'][tmpckey]['users'][sender][tmpmode]
								del mysockets[sock]['channels'][tmpckey]['users'][sender]
		elif (incom[1].upper() == 'MODE'):
			if (incom[2] == mysockets[sock]['nick']): modeprocessor_user(sock,'umode',incom[3])
			else: 
				modeprocessor_chan(sock,sender,rl(incom[2]),incom[3:])
				if (chanmodes(sock,rl(incom[2])) != 'NULL'):
					sts(sock,"MODE {0} {1}".format(incom[2],chanmodes(sock,rl(incom[2]))))
		elif (incom[1].upper() == 'TOPIC'):
			debug(sock,"TOPIC")
		elif (incom[1].upper() == 'WALLOPS'):
			debug(sock,"WALLOPS")
		elif (incom[1].upper() == 'INVITE'):
			debug(sock,"INVITE")
		elif (incom[1].upper() == 'NOTICE'):
			if (incom[2] == mysockets[sock]['nick']): commands(sock,'PNOTE',sender,incom,raw)
			else: commands(sock,'CNOTE',sender,incom,raw)
		elif (incom[1].upper() == 'PRIVMSG'):
			if (incom[2] == mysockets[sock]['nick']): commands(sock,'PMSG',sender,incom,raw)
			else: commands(sock,'CMSG',sender,incom,raw)
		else:
			debug(sock,incom)
			debug(sock,"Unknown feature at this momment")
	else:
		debug(sock,"Unknown Lenght {0}".format(incom))

def massmodes(sock,user,chan,modes):
	modespl = mysockets[sock]['modespl']
	tmpusers = deque()
	if (len(mysockets[sock]['channels'][chan]['users']) > 0):
		tmplogged = 'FALSE'
		tmpkeys = mysockets[sock]['channels'][chan]['users'].keys()
		for tmpkey in tmpkeys:
			if (modes[2] == 'ALL'):
				tmpusers.append(tmpkey)
			elif (modes[2] == 'BC'):
				if (modes[0] == 'ADD'):	tmpusers.append(tmpkey)
				else:
					if (tmpkey == user): tmplogged = 'TRUE'
					elif (tmpkey == mysockets[sock]['nick']): tmplogged = 'TRUE'
					else: tmpusers.append(tmpkey)
			else:
				for tmpmode in modes[2]:
					if (tmpkey == tmpmode): tmpusers.append(tmpkey)
			
	i = 0
	outputmode = ''
	while (i != modespl):
		outputmode = outputmode+modes[1]
		i = i + 1
	outputmode = outputmode.rstrip()
	if (modes[0] == 'ADD'): omode = '+'
	else: omode = '-'
	i = l = 0
	output = ''
	length = len(tmpusers)
	while (i != length):
		output = output+tmpusers.popleft()+" "
		l = l + 1
		if (l == modespl):
			output = output.rstrip()
			sts(sock,"MODE {0} {1}{2} {3}".format(chan,omode,outputmode,output))
			output = ''
			l = 0
		i = i + 1
	output = output.rstrip()
	sts(sock,"MODE {0} {1}{2} {3}".format(chan,omode,outputmode,output))		
		
def modeprocessor_chan(sock,user,chan,data):
	try: mysockets[sock]['channels'][chan]['modes']
	except: mysockets[sock]['channels'][chan]['modes'] = dict()
	i = 0
	pos = 1
	mode = 'SUB'
	while (i < len(data[0])):
		if ((data[0][i] == '+') or (data[0][i] == '-') or (data[0][i] == '(') or (data[0][i] == ')')):
			if (data[0][i] == '+'): mode = 'ADD'
			else: mode = 'SUB'
		else:
			if (data[0][i] == 'q'): tmpmode = 'FOP'
			elif (data[0][i] == 'a'): tmpmode = 'SOP'
			elif (data[0][i] == 'o'): tmpmode = 'OP'
			elif (data[0][i] == 'h'): tmpmode = 'HOP'
			elif (data[0][i] == 'v'): tmpmode = 'VOICE'
			elif (data[0][i] == 'e'): tmpmode = 'EXCEPT'
			elif (data[0][i] == 'I'): tmpmode = 'INVEX'
			elif (data[0][i] == 'b'): tmpmode = 'BAN'
			elif (data[0][i] == 'l'): tmpmode = 'LIMIT'
			elif (data[0][i] == 'k'): tmpmode = 'CHANPASS'
			elif (data[0][i] == 'f'): tmpmode = 'FLOOD'
			elif (data[0][i] == 'j'): tmpmode = 'JOIN'
			elif (data[0][i] == 'L'): tmpmode = 'LINK'
			elif (data[0][i] == 'B'): tmpmode = 'BANLINK'	
			else: tmpmode = data[0][i]
			if (mode == 'ADD'):
				if ((tmpmode == 'FOP') or (tmpmode == 'SOP') or (tmpmode == 'OP') or (tmpmode == 'HOP') or (tmpmode == 'VOICE') or (tmpmode == 'EXCEPT') or (tmpmode == 'INVEX') or (tmpmode == 'BAN') or (tmpmode == 'LIMIT') or (tmpmode == 'LINK') or (tmpmode == 'BANLINK') or (tmpmode == 'CHANPASS') or (tmpmode == 'FLOOD') or (tmpmode == 'JOIN')):
					if ((tmpmode == 'FOP') or (tmpmode == 'SOP') or (tmpmode == 'OP') or (tmpmode == 'HOP') or (tmpmode == 'VOICE')):
						try: mysockets[sock]['channels'][chan]['users'][data[pos]]
						except:	mysockets[sock]['channels'][chan]['users'][data[pos]] = dict()
						mysockets[sock]['channels'][chan]['users'][data[pos]][tmpmode] = 'TRUE'
					else:
						try: mysockets[sock]['channels'][chan][tmpmode]
						except:	mysockets[sock]['channels'][chan][tmpmode] = dict()
						if ((tmpmode == 'BAN') or (tmpmode == 'EXCEPT') or (tmpmode == 'INVEX')): mysockets[sock]['channels'][chan][tmpmode][data[pos]] = 'TRUE'
						else: mysockets[sock]['channels'][chan][tmpmode] = data[pos]
					pos = pos + 1
				else:
					try: mysockets[sock]['channels'][chan]['modes']
					except:	mysockets[sock]['channels'][chan]['modes'] = dict()
					mysockets[sock]['channels'][chan]['modes'][tmpmode] = 'TRUE'
			if (mode == 'SUB'):
				if ((tmpmode == 'FOP') or (tmpmode == 'SOP') or (tmpmode == 'OP') or (tmpmode == 'HOP') or (tmpmode == 'VOICE') or (tmpmode == 'EXCEPT') or (tmpmode == 'INVEX') or (tmpmode == 'BAN') or (tmpmode == 'LIMIT') or (tmpmode == 'LINK') or (tmpmode == 'BANLINK') or (tmpmode == 'CHANPASS') or (tmpmode == 'FLOOD') or (tmpmode == 'JOIN')):
					if ((tmpmode == 'FOP') or (tmpmode == 'SOP') or (tmpmode == 'OP') or (tmpmode == 'HOP') or (tmpmode == 'VOICE')):
						try: mysockets[sock]['channels'][chan]['users'][data[pos]]
						except:	mysockets[sock]['channels'][chan]['users'][data[pos]] = dict()
						mysockets[sock]['channels'][chan]['users'][data[pos]][tmpmode] = 'FALSE'
					else:
						try: mysockets[sock]['channels'][chan][tmpmode]
						except:	mysockets[sock]['channels'][chan][tmpmode] = dict()
						if ((tmpmode == 'BAN') or (tmpmode == 'EXCEPT') or (tmpmode == 'INVEX')): del mysockets[sock]['channels'][chan][tmpmode][data[pos]] 
						else: del mysockets[sock]['channels'][chan][tmpmode]
					pos = pos + 1
				else:
					try: mysockets[sock]['channels'][chan]['modes']
					except: mysockets[sock]['channels'][chan]['modes'] = dict()
					mysockets[sock]['channels'][chan]['modes'][tmpmode] = 'FALSE'
		i = i + 1	
		
def modeprocessor_user(sock,type,data):
	i = 0
	mode = 'SUB'
	while (i < len(data)):
		#debug(sock,incom[3][i])
		if ((data[i] == '+') or (data[i] == '-') or (data[i] == '(') or (data[i] == ')')):
			if (data[i] == '+'): mode = 'ADD'
			else: mode = 'SUB'
		else:
			if (mode == 'ADD'):
				try: mysockets[sock][type]
				except:	mysockets[sock][type] = dict()
				mysockets[sock][type][data[i]] = 'TRUE'
			if (mode == 'SUB'):
				try: mysockets[sock][type]
				except:	mysockets[sock][type] = dict()
				mysockets[sock][type][data[i]] = 'FALSE'
		i = i + 1		
		
def pulluser(user):
	sql = "SELECT * FROM users WHERE username = '{0}'".format(user)
	records = db.select(sql)
	if (len(records) == 0):	return 'FALSE'
	for record in records:
		#debug("NULL","{0} , {1} , {2} , {3} , {4} , {5} , {6}".format(record[0],record[1],record[2],record[3],record[4],record[5],record[6]))
		udata = {'id': int(record[0]),'username': record[1],'password': record[2],'global': record[3],'server': record[4],'channel': record[5],'msgtype': record[6]}
	return udata

def getwhois(sock,user,chan,mode,otheruser):
	if (otheruser == 'NULL'):
		if (islogged(sock,user) == 'TRUE'): userdata = pulluser(loggedin[sock][user]['username'])
		else: userdata = pulluser(user)
		tmpuinfo = user
	else:
		if (islogged(sock,otheruser) == 'TRUE'): userdata = pulluser(loggedin[sock][otheruser]['username'])
		else: userdata = pulluser(otheruser)
		tmpuinfo = otheruser
	if (userdata == 'FALSE'): 
		tmpusername = "GUEST"
		tmpglobaccess = 0
		tmpservaccess = 0
		tmpchanaccess = 0
		tmpmsgtype = "msg"
	else:
		tmpusername = userdata['username']
		tmpglobaccess = getglobaccess(userdata)
		tmpservaccess = getservaccess(sock,userdata)
		tmpchanaccess = getchanaccess(sock,chan,userdata)
		tmpmsgtype = userdata['msgtype']
	if (mode == 'WHOIS'):
		buildmsg(sock,'NORMAL',user,chan,'PRIV',"Your Bot Whois on {0}".format(tmpuinfo))
		buildmsg(sock,'NORMAL',user,chan,'PRIV',"Nick(Username): {0} ({1})".format(tmpuinfo,tmpusername))
		buildmsg(sock,'NORMAL',user,chan,'PRIV',"Global: {0} Server: {1} Channel: {2}".format(wordaccess(tmpglobaccess),wordaccess(tmpservaccess),wordaccess(tmpchanaccess)))
		buildmsg(sock,'NORMAL',user,chan,'PRIV',"End of Your Bot Whois on {0}".format(tmpuinfo))
	if (mode == 'WHOAMI'):
		buildmsg(sock,'NORMAL',user,chan,'PRIV',"Your Bot Whois")
		buildmsg(sock,'NORMAL',user,chan,'PRIV',"Nick(Username): {0} ({1})".format(tmpuinfo,tmpusername))
		buildmsg(sock,'NORMAL',user,chan,'PRIV',"Your Global Access: {0}".format(wordaccess(tmpglobaccess)))
		buildmsg(sock,'NORMAL',user,chan,'PRIV',"Your Server Access: {0}".format(wordaccess(tmpservaccess)))
		buildmsg(sock,'NORMAL',user,chan,'PRIV',"Your Channel Access: {0}".format(wordaccess(tmpchanaccess)))
		buildmsg(sock,'NORMAL',user,chan,'PRIV',"Your Current MsgType: {0}".format(tmpmsgtype))
		buildmsg(sock,'NORMAL',user,chan,'PRIV',"End of Your Bot Whois")	
	
def islogged(sock,user):
	tmplogged = 'FALSE'
	if (len(loggedin[sock]) > 0):
		tmpkeys = loggedin[sock].keys()
		for tmpkey in tmpkeys:
			if (tmpkey == user): tmplogged = 'TRUE'
			else: 
				if (tmplogged != 'TRUE'): tmplogged = 'FALSE'
	return tmplogged
	
def getglobaccess(data):
	#Global Straight access numbers
	if (data['global'] != 'NULL'): tmpglobaccess = data['global']
	else: tmpglobaccess = 0
	return tmpglobaccess
	
def getservaccess(sock,data):
	#Server ServerName~Access%ServerName~Access
	if (data['server'] != 'NULL'):
		tmpdata = data['server']
		tmpdata = tmpdata.split(chr(37))
		for tmpdata2 in tmpdata:
			tmpdata2 = tmpdata2.split(chr(126))
			if (tmpdata2[0] == mysockets[sock]['server']['servername']): tmpservaccess = tmpdata2[1]
	else: tmpservaccess = 0
	return tmpservaccess

def getchanaccess(sock,chan,data):
	#Channel ServerName|ChannelName~Access|ChannelName~Access%ServerName|ChannelName~Access|ChannelName~Access
	if (data['channel'] != 'NULL'):
		tmpdata = data['channel']
		tmpdata = tmpdata.split(chr(37))
		for tmpdata2 in tmpdata:
			tmpdata2 = tmpdata2.split(chr(124))
			if (tmpdata2[0] == mysockets[sock]['server']['servername']):
				tmpdata3 = tmpdata2[1:]
				for tmpdata4 in tmpdata3:
					tmpdata4 = tmpdata4.split(chr(126))
					if (tmpdata4[0] == chan): tmpchanaccess = tmpdata4[1]
	else: tmpchanaccess = 0
	return tmpchanaccess

def getaccess(sock,user,chan,type):
	userdata = pulluser(user)
	if (userdata == 'FALSE'): return 0
	else:
		tmpglobaccess = getglobaccess(userdata)
		tmpservaccess = getservaccess(sock,userdata)
		tmpchanaccess = getchanaccess(sock,chan,userdata)
		if (type == 'GLOBAL'): tmpaccess = tmpglobaccess
		if (type == 'SERVER'):
			tmpaccess = tmpglobaccess
			if (tmpaccess < tmpservaccess):	tmpaccess = tmpservaccess
		if (type == 'CHANNEL'):
			tmpaccess = tmpglobaccess
			if (tmpaccess < tmpservaccess):	tmpaccess = tmpservaccess
			if (tmpaccess < tmpchanaccess):	tmpaccess = tmpchanaccess
		return tmpaccess

def loggedgetaccess(sock,user,chan,type):
	if (islogged(sock,user) == 'TRUE'):
		return getaccess(sock,loggedin[sock][user]['username'],chan,type)
	else:
		return 0
		
def botlog(sock,user,chan,text):
	print "BOTLOG: {0} {1} {2} {3}".format(mysockets[sock]['server']['servername'],user,chan,text)
		
def debug(sock,text):
	if (sock == 'NULL'):
		print "DEBUG: {0}".format(text)
	else:
		print "DEBUG: {0} {1}".format(mysockets[sock]['server']['servername'],text)
	
def screenoutput(sock,mode,text):
	if (mode == 'in'):
		print "-{0}-> {1}".format(sock,text)
	if (mode == 'out'):
		print "<-{0}- {1}".format(sock,text)

def splitjoiner(data):
	outcounti = 0
	output = ''
	while (outcounti != len(data)):
		output = output+data[outcounti]+" "
		outcounti = outcounti + 1
	output = output.rstrip()
	return output
		
def buildmsg(sock,type,user,chan,uctype,message):
	#sock = server($1) type = messagetype($4) uctype = priv/chan($2) user/chan = sendto($3) message = message($5-)
	if (uctype == 'PRIV'): 
		sendto = user
		if (islogged(sock,user) == 'TRUE'):
			userdata = pulluser(loggedin[sock][user]['username'])
			msgtype = userdata['msgtype']
		else: msgtype = "msg"
	else: 
		sendto = chan
		msgtype = "msg"
	if (msgtype == "msg"): msgoutput = "PRIVMSG"
	if (msgtype == "notice"): msgoutput = "NOTICE"
	if (type == 'RAW'): mtoutput = "-(RAW)-"
	elif (type == 'BLOG'): mtoutput = "-(CBOT)-(LOG)-"
	elif (type == 'ELOG'): mtoutput = "-(CBOT)-(ERROR-LOG)-"
	elif (type == 'RELAY'): mtoutput = "*"
	elif (type == 'NORMAL'): mtoutput = "-(CBOT)-"
	elif (type == 'HELP'): mtoutput = "-(CBOT)-(HELP)-"
	elif (type == 'ERROR'): 
		mtoutput = "-(CBOT)-(ERROR)-"
		if (message == 'LOGIN'): message = "You are already Logged in."
		elif (message == 'PASSPROB'): message = "There was a problem with changing your password"
		elif (message == 'LOGGED'):	message = "You are Logged in."
		elif (message == 'NOTLOGGED'): message = "You are not Logged in."
		elif (message == 'NOACCESS'): message = "You either have no access to this command or you are not Logged in."
		elif (message == 'NOACCESSHELP'): message = "You do not have access to read help on this command."
		else: message = message
	else: mtoutput = "-(CBOT)-"
	sts(sock,"{0} {1} :{2}4,1{3}{2} {4}".format(msgoutput,sendto,chr(3),mtoutput,message))	
	
def sts(sock,data):
	#mysocket[sock].send("{0}\n\r".format(data))
	#screenoutput(sock,'out',data)
	queue[sock].append("{0}\n\r".format(data))

def run_timer(sock):
	lasttimer[sock] = time.time()

def run_globtimer():
	globtimer['lastcheck'] = time.time()
	
def run_queue(sock):
	now = time.time()
	i = 0
	queuelimit = int(settings['msgqueue'])
	msginterval = int(settings['msginterval'])
	if ((lastqueue[sock] + msginterval) < now):
		#debug(sock,now)
		#debug(sock,lastqueue[sock])
		while (i != queuelimit):
			#debug(sock,"Queue Loop {0} and Queue Lenght is {1}, Queue Loop Max should be {2}".format(i,len(queue[sock]),queuelimit))
			if (len(queue[sock]) != 0):
				data = queue[sock].popleft()
				mysocket[sock].send(data)
				screenoutput(sock,'out',data.strip('\n\r'))
				i = i + 1
			else:
				i = queuelimit
			lastqueue[sock] = time.time()

def rl(item):
	return item.lower()
			
def checkchan(sock,chan):
	channels = mysockets[sock]['chans'].keys()
	for channel in channels:
		if (channel == chan):
			if (mysockets[sock]['chans'][channel]['enabled'] == 'enabled'):
				return 'TRUE'
			else:
				return 'FALSE'
	return 'FALSE'

def chanmodes(sock,chan):
	channels = mysockets[sock]['chans'].keys()
	foutput = ''
	for channel in channels:
		if (channel == chan):
			if (mysockets[sock]['chans'][chan]['chanmodes'] != 'NULL'):
				tmpmodes = mysockets[sock]['channels'][chan]['modes'].keys()
				tmpimodes = mysockets[sock]['chans'][chan]['chanmodes']
				mydata = mysockets[sock]['channels'][chan]['users'][mysockets[sock]['nick']]
				isop = 'FALSE'
				try:
					if (mydata['FOP'] == 'TRUE'):
						isop = 'TRUE'
				except:
					isop = 'FALSE'
				try:
					if (mydata['SOP'] == 'TRUE'):
						isop = 'TRUE'
				except:
					isop = 'FALSE'
				try:
					if (mydata['OP'] == 'TRUE'):
						isop = 'TRUE'
				except:
					isop = 'FALSE'
				try:
					if (mysockets[sock]['isoper'] == 'TRUE'):
						isop = 'TRUE'
				except:
					isop = 'FALSE'
				if (isop == 'TRUE'):
					data = tmpimodes.split(' ')
					i = 0
					pos = 1
					output = ''
					output2 = ''
					mode = 'SUB'
					while (i < len(data[0])):
						if ((data[0][i] == '+') or (data[0][i] == '-') or (data[0][i] == '(') or (data[0][i] == ')')):
							if (data[0][i] == '+'): mode = 'ADD'
							else: mode = 'SUB'
							if ((data[0][i] == '+') or (data[0][i] == '-')):
								output = output+data[0][i]
						else:
							if (data[0][i] == 'l'): tmpmode = 'LIMIT'
							elif (data[0][i] == 'k'): tmpmode = 'CHANPASS'
							elif (data[0][i] == 'f'): tmpmode = 'FLOOD'
							elif (data[0][i] == 'j'): tmpmode = 'JOIN'
							elif (data[0][i] == 'L'): tmpmode = 'LINK'
							elif (data[0][i] == 'B'): tmpmode = 'BANLINK'	
							else: tmpmode = data[0][i]
							if (mode == 'ADD'):
								if ((tmpmode == 'LIMIT') or (tmpmode == 'LINK') or (tmpmode == 'BANLINK') or (tmpmode == 'CHANPASS') or (tmpmode == 'FLOOD') or (tmpmode == 'JOIN')):
									output = output+data[0][i]
									output2 = output2+data[pos]+' '
									pos = pos + 1
								else:
									output = output+tmpmode
							if (mode == 'SUB'):
								if ((tmpmode == 'LIMIT') or (tmpmode == 'LINK') or (tmpmode == 'BANLINK') or (tmpmode == 'CHANPASS') or (tmpmode == 'FLOOD') or (tmpmode == 'JOIN')):
									output = output+data[0][i]
									output2 = output2+data[pos]+' '
									pos = pos + 1
								else:
									output = output+tmpmode
						i = i + 1
					output = output.strip(' ')
					if (len(output) >= 2):
						output2 = output2.rstrip()
						foutput = output+' '+output2
						foutput = foutput.rstrip()
						return foutput
					else:
						return 'NULL'
				else:
					return 'NULL'
			else:
				return 'NULL'
	return 'NULL'
	
def joinchan(sock,chan):
	channels = mysockets[sock]['chans'].keys()
	for channel in channels:
		if (channel == chan):
			if (mysockets[sock]['chans'][channel]['chanpass'] == 'NULL'):
				sts(sock,"JOIN :{0}".format(channel))
			else:
				sts(sock,"JOIN :{0} {1}".format(channel,mysockets[sock]['chans'][channel]['chanpass']))
	
def autojoinchannels(sock):
	channels = mysockets[sock]['chans'].keys()
	for channel in channels:
		if (checkchan(sock,channel) == 'TRUE'):
			joinchan(sock,channel)
	
def operupcheck(sock):
	if (mysockets[sock]['server']['botoper'] != 'NULL'):
		sts(sock,"OPER {0} {1}".format(mysockets[sock]['server']['botoper'],mysockets[sock]['server']['botoperpass']))
		mysockets[sock]['isoper'] = 'ATTEMPTING'
		
def wordaccess(access):
	if (access == '7'): wordaccess = "Creator(7)"
	elif (access == '6'): wordaccess = "Master(6)"
	elif (access == '5'): wordaccess = "Owner(5)"
	elif (access == '4'): wordaccess = "Protected(4)"
	elif (access == '3'): wordaccess = "OP(3)"
	elif (access == '2'): wordaccess = "Half-Op(2)"
	elif (access == '1'): wordaccess = "Voice(1)"
	else: wordaccess = "No Access(0)"
	return wordaccess
		
def rehash():
	sql = "SELECT * FROM settings"
	records = db.select(sql)
	for record in records:
		#debug("NULL","{0} = {1} ".format(record[1],record[2]))
		settings[record[1]] = record[2]

	sql = "SELECT * FROM servers"
	records = db.select(sql)
	sockcount = 1
	for record in records:
		try: mysockets[sockcount]
		except: mysockets[sockcount] = dict()
		try: mysockets[sockcount]['server']
		except: mysockets[sockcount]['server'] = dict()	
		try: mysockets[sockcount]['connection']
		except: mysockets[sockcount]['connection'] = dict()
		#debug("NULL","{0} , {1} , {2} , {3} , {4} , {5} , {6} , {7} , {8} , {9} , {10} ".format(record[0],record[1],record[2],record[3],record[4],record[5],record[6],record[7],record[8],record[9],record[10]))
		#servers[record[0]] = {'id': int(record[0]), 'servername': record[1], 'address': record[2], 'serverport': int(record[3]), 'serverpass': record[4], 'nick': record[5], 'bnick': record[6], 'nickservpass': record[7], 'botoper': record[8], 'botoperpass': record[9], 'enabled': record[10]}
		mysockets[sockcount]['server']['id'] = int(record[0])
		mysockets[sockcount]['server']['servername'] = record[1]
		mysockets[sockcount]['server']['address'] = record[2]
		mysockets[sockcount]['server']['serverport'] = int(record[3])
		mysockets[sockcount]['server']['serverpass'] = record[4]
		mysockets[sockcount]['server']['nick'] = record[5]
		mysockets[sockcount]['server']['bnick'] = record[6]
		mysockets[sockcount]['server']['nickservpass'] = record[7]
		mysockets[sockcount]['server']['botoper'] = record[8]
		mysockets[sockcount]['server']['botoperpass'] = record[9]
		mysockets[sockcount]['server']['enabled'] = record[10]
		mysockets[sockcount]['connection']['address'] = mysockets[sockcount]['server']['address']
		mysockets[sockcount]['connection']['serverport'] = mysockets[sockcount]['server']['serverport']	
		sockcount = sockcount + 1

	sql = "SELECT * FROM channels"
	records = db.select(sql)
	for record in records:
		#debug("NULL","{0} , {1} , {2}, {3}, {4}, {5}, {6}".format(record[0],record[1],record[2],record[3],record[4],record[5],record[6]))
		#channels[record[0]] = {'id': int(record[0]), 'server': record[1], 'channel': record[2], 'chanpass': record[3], 'chanmodes': record[4], 'chantopic': record[5], 'options': record[6], 'enabled': record[7]}
		try: mysockets[int(record[1])]['chans']
		except: mysockets[int(record[1])]['chans'] = dict()
		try: mysockets[int(record[1])]['chans'][record[2]]
		except: mysockets[int(record[1])]['chans'][record[2]] = dict()
		mysockets[int(record[1])]['chans'][record[2]]['chanpass'] = record[3]
		mysockets[int(record[1])]['chans'][record[2]]['chanmodes'] = record[4]
		mysockets[int(record[1])]['chans'][record[2]]['chantopic'] = record[5]
		mysockets[int(record[1])]['chans'][record[2]]['options'] = record[6]
		mysockets[int(record[1])]['chans'][record[2]]['enabled'] = record[7]

	tempsocks = mysockets.keys()
	for tempsock in tempsocks:
		if (mysockets[tempsock]['server']['enabled'] != 'enabled'):
			del mysockets[tempsock]

def loaddata():
	sql = "SELECT * FROM settings"
	records = db.select(sql)
	for record in records:
		#debug("NULL","{0} = {1} ".format(record[1],record[2]))
		settings[record[1]] = record[2]

	sql = "SELECT * FROM servers"
	records = db.select(sql)
	sockcount = 1
	for record in records:
		try: mysockets[sockcount]
		except: mysockets[sockcount] = dict()
		try: mysockets[sockcount]['server']
		except: mysockets[sockcount]['server'] = dict()	
		try: mysockets[sockcount]['connection']
		except: mysockets[sockcount]['connection'] = dict()
		#debug("NULL","{0} , {1} , {2} , {3} , {4} , {5} , {6} , {7} , {8} , {9} , {10} ".format(record[0],record[1],record[2],record[3],record[4],record[5],record[6],record[7],record[8],record[9],record[10]))
		#servers[record[0]] = {'id': int(record[0]), 'servername': record[1], 'address': record[2], 'serverport': int(record[3]), 'serverpass': record[4], 'nick': record[5], 'bnick': record[6], 'nickservpass': record[7], 'botoper': record[8], 'botoperpass': record[9], 'enabled': record[10]}
		mysockets[sockcount]['server']['id'] = int(record[0])
		mysockets[sockcount]['server']['servername'] = record[1]
		mysockets[sockcount]['server']['address'] = record[2]
		mysockets[sockcount]['server']['serverport'] = int(record[3])
		mysockets[sockcount]['server']['serverpass'] = record[4]
		mysockets[sockcount]['server']['nick'] = record[5]
		mysockets[sockcount]['server']['bnick'] = record[6]
		mysockets[sockcount]['server']['nickservpass'] = record[7]
		mysockets[sockcount]['server']['botoper'] = record[8]
		mysockets[sockcount]['server']['botoperpass'] = record[9]
		mysockets[sockcount]['server']['enabled'] = record[10]
		mysockets[sockcount]['connection']['address'] = mysockets[sockcount]['server']['address']
		mysockets[sockcount]['connection']['serverport'] = mysockets[sockcount]['server']['serverport']		
		sockcount = sockcount + 1

	sql = "SELECT * FROM channels"
	records = db.select(sql)
	for record in records:
		#debug("NULL","{0} , {1} , {2}, {3}, {4}, {5}, {6}".format(record[0],record[1],record[2],record[3],record[4],record[5],record[6]))
		#channels[record[0]] = {'id': int(record[0]), 'server': record[1], 'channel': record[2], 'chanpass': record[3], 'chanmodes': record[4], 'chantopic': record[5], 'options': record[6], 'enabled': record[7]}
		try: mysockets[int(record[1])]['chans']
		except: mysockets[int(record[1])]['chans'] = dict()
		try: mysockets[int(record[1])]['chans'][record[2]]
		except: mysockets[int(record[1])]['chans'][record[2]] = dict()
		mysockets[int(record[1])]['chans'][record[2]]['chanpass'] = record[3]
		mysockets[int(record[1])]['chans'][record[2]]['chanmodes'] = record[4]
		mysockets[int(record[1])]['chans'][record[2]]['chantopic'] = record[5]
		mysockets[int(record[1])]['chans'][record[2]]['options'] = record[6]
		mysockets[int(record[1])]['chans'][record[2]]['enabled'] = record[7]

	tempsocks = mysockets.keys()
	for tempsock in tempsocks:
		if (mysockets[tempsock]['server']['enabled'] != 'enabled'):
			del mysockets[tempsock]

def doconnection(sock):
	mysockets[sock]['lastcmd'] = ''
	if (mysockets[sock]['server']['nickservpass'] != 'NULL'):
			mysockets[sock]['identified'] = 'FALSE'
	else:
		mysockets[sock]['identified'] = 'TRUE'
	mysockets[sock]['isoper'] = ''
	mysockets[sock]['lastping'] = time.time()
	mysocket[sock] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		mysocket[sock].connect((mysockets[sock]['connection']['address'], mysockets[sock]['connection']['serverport']))
		mysocket[sock].settimeout(0)
		if (mysockets[sock]['server']['serverpass'] != 'NULL'):
			sts(sock,"PASS {0}".format(mysockets[sock]['server']['serverpass']))
		sts(sock,"NICK {0}".format(mysockets[sock]['nick']))
		sts(sock,"USER {0} 0 {2} :Ch3wyB0t Version {1}".format(settings['botname'],version,mysockets[sock]['server']['address']))
	except:
		#del mysocket[sock]
		#del mysockets[sock]
		blarg = 1
	
def main ():
	if hasattr(os, 'fork'): 
		attemptfork()
	tempsocks = mysockets.keys()
	globtimer['data'] = dict()
	globtimer['lastcheck'] = time.time() - 10
	for tempsock in tempsocks:
		mysockets[tempsock]['channels'] = dict()
		queue[tempsock] = deque()
		timer[tempsock] = dict()
		lastqueue[tempsock] = time.time() - 10 
		lasttimer[tempsock] = time.time() - 10
		loggedin[tempsock] = dict()
		tempdata[tempsock] = dict()
		mysockets[tempsock]['lastcmd'] = ''
		if (mysockets[tempsock]['server']['nickservpass'] != 'NULL'):
			mysockets[tempsock]['identified'] = 'FALSE'
		else:
			mysockets[tempsock]['identified'] = 'TRUE'
		mysockets[tempsock]['lastping'] = time.time()
		mysockets[tempsock]['nick'] = mysockets[tempsock]['server']['nick']
		doconnection(tempsock)
		run_queue(tempsock)
	
	while True:
		if (len(globtimer['data']) != 0): run_globtimer()
		tempsocks = mysockets.keys()
		sockcount = len(tempsocks)
		if (sockcount == 0):
			break
		for tempsock in tempsocks:
			now = time.time()
			if ((mysockets[tempsock]['lastping'] + 600) < now):
				mysocket[tempsock].close()
				doconnection(tempsock)
			if (len(queue[tempsock]) != 0):	run_queue(tempsock)
			if (len(timer[tempsock]) != 0): run_timer(tempsock)
			try:
				data = mysocket[tempsock].recv(10240)
				process = 1
			except socket.timeout:
				#debug(tempsock,socket.timeout)
				process = 0
			except socket.error:
				#debug(tempsock,socket.error)
				process = 0
			if (process == 1):
				tmpdata = data.strip('\r')
				tmpdata = tmpdata.split('\n')
				while (tmpdata):
					if (tmpdata[0] != ''):
						parse_data(tempsock,tmpdata[0])
					del tmpdata[0]
		time.sleep(0.5)

# attemptfork is thanks to phenny irc bot (http://inamidst.com/phenny/)
def attemptfork(): 
	try: 
		pid = os.fork()
		if pid > 0:
			sys.exit(0)
	except OSError, e: 
		raise OSError('Could not daemonize process: {0} ({1})'.format(e.errno, e.strerror))
	os.setsid()
	os.umask(0)
	try: 
		pid = os.fork()
		if pid > 0: 
			sys.exit(0)
	except OSError, e: 
		raise OSError('Could not daemonize process: {0} ({1})'.format(e.errno, e.strerror))
			
if __name__ == '__main__':
	loaddata()
	#debug("NULL","Time to start coding, hehe")
	try:
		main()
	except KeyboardInterrupt:
		print "Bot Exited due to KeyboardInterrupt"