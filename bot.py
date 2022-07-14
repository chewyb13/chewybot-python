#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
ChewyBot coded by chewyb_13
"""
# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# Disabling these just to cut down on some stuff to possibly make it quicker
# pylint: disable=too-many-nested-blocks
# pylint: disable=too-many-branches
# pylint: disable=too-many-arguments
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals
# pylint: enable=useless-suppression

# Don't mess with the imports

import os
import sys
import logging
import logging.handlers
#import subprocess
#import sqlite3
#import array
from collections import deque
#from collections import UserDict
import socket
#import asyncore
#import asynchat
#import string
import time
import datetime
import hashlib
#import optparse
#import threading
#import re
from database import Database

# You can Start Editing Settings Here

# You can edit the location of your database here, or where you want it to be located
DATAFILE: str = "./database/chewydb.db"

# Please do not edit below this section
# unless you know what you are doing

# Details about the bot
__author__: str = "chewyb_13"
__servers__: str = "irc.chewynet.co.uk & HellRisingSun.BounceMe.Net:7202"
__helpchans__: str = "#chewybot"
__email__: str = "chewyb13@gmail.com"
__bugtracker__: str = "https://github.com/chewyb13/chewybot-python/issues"
__sourcecode__: str = "https://github.com/chewyb13/chewybot-python.git"
__version__: str = "0.1.3.11"

# bot global values

# Logging setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger_handle = logging.FileHandler(filename="log.log",mode="a")
#logger_handle = logging.handlers.TimedRotatingFileHandler(filename="log.log", when='midnight', interval=1, backupCount=0, encoding="utf-8")
logger_handle.setLevel(logging.DEBUG)
logger_chandle = logging.StreamHandler()
logger_chandle.setLevel(logging.DEBUG)
logger_format = logging.Formatter("{asctime}:{name}:{levelname}:{message}", style="{")
logger_handle.setFormatter(logger_format)
logger_chandle.setFormatter(logger_format)
logger.addHandler(logger_handle)
logger.addHandler(logger_chandle)

settings:dict = {}
mysockets:dict = {}
mysocket:dict = {}

tempdata:dict = {}
loggedin:dict = {}

debuginfo:dict = {}

globtimer:dict = {}
lasttimer:dict = {}
timer:dict = {}
lastqueue:dict = {}
queue:dict = {}
db = Database(db_file=DATAFILE)

""" This is the start of the code sections """
#44 is , 124 is | 126 is ~ 37 is %
#buildmsg(sock,'NORMAL',user,chan,'CHAN',output)
#imsgtypes are NORMAL, HELP, ERROR  mtype are PRIV, CHAN


# Notice imsgtypes = 'CNOTE' = channel notice, 'PNOTE' = private notice
# PRIVMSG imsgtypes = 'CMSG' = channel PRIVMSG, 'PMSG' = private PRIVMSGS
def mycommands(sock: int,imsgtype: str,myuser: str,incom,raw):
    """Command Structure.

    Args:
        sock (int): The socket information for the current connection.

        imsgtype (str): Incoming msgtype: CNOTE, PNOTE, CMSG, PMSG

        myuser (str): The user that called the command

        incom (_type_): Incoming data

        raw (_type_): Incoming raw data
    """
    if imsgtype in ('CNOTE', 'CMSG'):
        chan:str = rtnlower(incom[2])
    else:
        chan:str = 'NULL'
    if len(incom) >= 4:
        #debug("Enetered Private messages")
        if ((imsgtype == 'PNOTE') and (incom[0] == mysockets[sock]['connectaddress'])):
            logger.debug("Snotice: %s", incom)
        elif '\x01' in incom[3]:
            ctcp = incom[3:]
            stripcount = len(ctcp)
            while stripcount:
                stripcount = stripcount - 1
                ctcp[stripcount] = ctcp[stripcount].strip('\x01')
            if ctcp[0].upper() == 'ACTION':
                debug(sock,f"Got a Action {ctcp[1:]}")
            elif ctcp[0].upper() == 'VERSION':
                if len(ctcp) >= 2:
                    debug(sock,f"Got a CTCP VERSION Response {ctcp[1:]}")
                else:
                    sts(sock,f"NOTICE {myuser} :\x01VERSION Ch3wyB0t Version {__version__}\x01")
            elif ctcp[0].upper() == 'PING':
                if len(ctcp) >= 2:
                    sts(sock,f"NOTICE {myuser} :\x01PING {ctcp[1]}\x01")
                else:
                    sts(sock,f"NOTICE {myuser} :\x01PING\x01")
            elif ctcp[0].upper() == 'TIME':
                if len(ctcp) >= 2:
                    debug(sock,f"Got a CTCP TIME response {ctcp[1:]}")
                else:
                    currenttime = datetime.datetime.now()
                    sts(sock,f"NOTICE {myuser} :\x01TIME {currenttime.strftime('%a %b %d %I:%M:%S%p %Y')}\x01")
            else:
                debug(sock,f"Got a unknown CTCP request {ctcp}")
        elif incom[3] == '?trigger':
            buildmsg(sock,'NORMAL',myuser,chan,'PRIV',f"Channel: {settings['chancom']}{settings['signal']} Private Message: {settings['pvtcom']}{settings['signal']}")
        elif ((incom[3] == settings['chancom']+settings['signal']) and (imsgtype in ('CMSG', 'CNOTE'))) or ((incom[3] == settings['pvtcom']+settings['signal']) and (imsgtype in ('PMSG', 'PNOTE'))):
            if len(incom) >= 5:
                if incom[4].upper() == 'EXIT':
                    if loggedgetaccess(sock,myuser,chan,'GLOBAL') >= 6:
                        if len(incom) >= 6:
                            output = splitjoiner(incom[5:])
                            tempsocks = mysockets.keys()
                            for tempsock in tempsocks:
                                mysockets[tempsock]['lastcmd'] = 'EXIT'
                                sts(tempsock,f"QUIT {output}")
                        else:
                            tempsocks = mysockets.keys()
                            for tempsock in tempsocks:
                                mysockets[tempsock]['lastcmd'] = 'EXIT'
                                sts(tempsock,f"QUIT Ch3wyB0t Version {__version__} Quitting")
                    else:
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                elif incom[4].upper() == 'RELOAD':
                    if loggedgetaccess(sock,myuser,chan,'GLOBAL') >= 6:
                        tempsocks = mysockets.keys()
                        debug('NULL',f"Value {tempsocks} value")
                        for tempsock in tempsocks:
                            mysockets[tempsock]['lastcmd'] = 'RELOAD'
                            sts(tempsock,f"QUIT Ch3wyB0t Version {__version__} Reloading")
                    else:
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                elif incom[4].upper() == 'RAW':
                    if loggedgetaccess(sock,myuser,chan,'GLOBAL') >= 7:
                        if len(incom) >= 6:
                            output = splitjoiner(raw[5:])
                            sts(sock,f"{output}")
                            buildmsg(sock,'RAW',myuser,chan,'PRIV',f"Sent {output} to Server")
                        else:
                            buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter what you want to send from the bot")
                    else:
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                elif incom[4].upper() == 'RAWDB':
                    if loggedgetaccess(sock,myuser,chan,'GLOBAL') >= 7:
                        if len(incom) >= 6:
                            output = splitjoiner(raw[5:])
                            db.execute(output)
                            buildmsg(sock,'RAW',myuser,chan,'PRIV',f"Sent {output} to the database")
                        else:
                            buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter what you want to send to the database")
                    else:
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                elif incom[4].upper() == 'QUIT':
                    if loggedgetaccess(sock,myuser,chan,'SERVER') >= 6:
                        if len(incom) >= 6:
                            mysockets[sock]['lastcmd'] = 'QUIT'
                            sts(sock,f"QUIT {splitjoiner(incom[5:])}")
                        else:
                            mysockets[sock]['lastcmd'] = 'QUIT'
                            sts(sock,f"QUIT Ch3wyB0t Version {__version__} Quitting")
                    else:
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                elif incom[4].upper() == 'REHASH':
                    if loggedgetaccess(sock,myuser,chan,'GLOBAL') >= 6:
                        buildmsg(sock,'NORMAL',myuser,chan,'PRIV',"Rehashing...")
                        rehash()
                        buildmsg(sock,'NORMAL',myuser,chan,'PRIV',"Rehashing Complete...")
                    else:
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                elif incom[4].upper() == 'SETTINGS':
                    if imsgtype in ('PMSG', 'PNOTE'):
                        if loggedgetaccess(sock,myuser,chan,'GLOBAL') >= 6:
                            if len(incom) >= 6:
                                if incom[5].upper() == 'SET':
                                    if len(incom) >= 7:
                                        if len(incom) >= 8:
                                            sql = f"UPDATE settings SET setting = '{rtnlower(incom[6])}', value = '{incom[7]}' WHERE setting = '{rtnlower(incom[6])}'"
                                            db.execute(sql)
                                            settings[rtnlower(incom[6])] = incom[7]
                                            buildmsg(sock,'NORMAL',myuser,chan,'PRIV',f"You have successfully changed {rtnlower(incom[6])} to {incom[7]}")
                                        else:
                                            buildmsg(sock,'ERROR',myuser,chan,'PRIV',"Missing Setting Value")
                                    else:
                                        buildmsg(sock,'ERROR',myuser,chan,'PRIV',"Missing Setting Name")
                                elif incom[5].upper() == 'LIST':
                                    sql = "SELECT * FROM settings"
                                    records = db.select(sql)
                                    for record in records:
                                        buildmsg(sock,'NORMAL',myuser,chan,'PRIV',f"Setting: {record[1]} Value: {record[2]}")
                                else:
                                    buildmsg(sock,'ERROR',myuser,chan,'PRIV',"Error, Use Either Set or List")
                            else:
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"Error, Use Either Set or List")
                        else:
                            buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                    else:
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You can not access settings via channel commands")
                elif incom[4].upper() == 'SERVER':
                    if imsgtype in ('PMSG', 'PNOTE'):
                        if loggedgetaccess(sock,myuser,chan,'GLOBAL') >= 6:
                            if len(incom) >= 6:
                                if incom[5].upper() == 'ADD':
                                    logger.debug("Server Add Section called")
                                elif incom[5].upper() == 'CHG':
                                    logger.debug("Server CHG called")
                                    #if (len(incom) >= 7):
                                        #if (len(incom) >= 8):
                                            #sql = "UPDATE settings SET setting = '{0}', value = '{1}' WHERE setting = '{0}'".format(rtnlower(incom[6]),incom[7])
                                            #vals = db.execute(sql)
                                            #settings[rtnlower(incom[6])] = incom[7]
                                            #buildmsg(sock,'NORMAL',myuser,chan,'PRIV',"You have successfully changed {0} to {1}".format(rtnlower(incom[6]),incom[7]))
                                        #else:
                                            #buildmsg(sock,'ERROR',myuser,chan,'PRIV',"Missing Setting Value")
                                    #else:
                                        #buildmsg(sock,'ERROR',myuser,chan,'PRIV',"Missing Setting Name")
                                elif incom[5].upper() == 'LIST':
                                    sql = "SELECT * FROM servers"
                                    records = db.select(sql)
                                    for record in records:
                                        if record[10] == 'enabled':
                                            buildmsg(sock,'NORMAL',myuser,chan,'PRIV',f"\x033SID: {int(record[0])} Server: {record[1]} Address: {record[2]} Port: {int(record[3])} SPass: {record[4]} Nick: {record[5]} BNick: {record[6]} NSPass: {record[7]} BotOper: {record[8]} BotOperPass: {record[9]}\x03")
                                        else:
                                            buildmsg(sock,'NORMAL',myuser,chan,'PRIV',f"\x034SID: {int(record[0])} Server: {record[1]} Address: {record[2]} Port: {int(record[3])} SPass: {record[4]} Nick: {record[5]} BNick: {record[6]} NSPass: {record[7]} BotOper: {record[8]} BotOperPass: {record[9]}\x03")
                                    buildmsg(sock,'NORMAL',myuser,chan,'PRIV',"Color \x033Green\x03 is enabled, Color \x034Red\x03 is disabled")
                                else:
                                    buildmsg(sock,'ERROR',myuser,chan,'PRIV',"Error, Use Either List, Add, or Chg")
                            else:
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"Error, Use Either List, Add, or Chg")
                        else:
                            buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                    else:
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You can not access server via channel commands")
                elif incom[4].upper() == 'CHANNEL':
                    if imsgtype in ('PMSG', 'PNOTE'):
                        if loggedgetaccess(sock,myuser,chan,'GLOBAL') >= 6:
                            if len(incom) >= 6:
                                if incom[5].upper() == 'CHG':
                                    if len(incom) >= 7:
                                        if len(incom) >= 8:
                                            if incom[7].upper() == 'SERVER':
                                                if len(incom) >= 9:
                                                    buildmsg(sock,'NORMAL',myuser,chan,'PRIV', f"You have successfully changed CID {incom[6]} server value to {incom[8]}")
                                                else:
                                                    buildmsg(sock,'ERROR',myuser,chan,'PRIV', "Missing server value to change to")
                                            elif incom[7].upper() == 'CHANNEL':
                                                logger.debug("Channel CHG Channel called")
                                            elif incom[7].upper() == 'CHANPASS':
                                                logger.debug("Channel CHG ChanPass called")
                                            elif incom[7].upper() == 'CHANMODES':
                                                logger.debug("Channel CHG ChanModes called")
                                            elif incom[7].upper() == 'CHANTOPIC':
                                                logger.debug("Channel CHG ChanTopic called")
                                            elif incom[7].upper() == 'OPTIONS':
                                                logger.debug("Channel CHG Options called")
                                            elif incom[7].upper() == 'ENABLED':
                                                logger.debug("Channel CHG Enabled called")
                                            else:
                                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"Error, You must choose from Server, Channel, Chanpass, Chanmodes, Chantopic, Options, Enabled")
                                        else:
                                            buildmsg(sock,'ERROR',myuser,chan,'PRIV',"Error, You must choose from Server, Channel, Chanpass, Chanmodes, Chantopic, Options, Enabled")
                                    else:
                                        buildmsg(sock,'ERROR',myuser,chan,'PRIV',"Error, Missing CID number, please check channel list again")
                                    #if len(incom) >= 7:
                                        #if len(incom) >= 8:
                                            #sql = "UPDATE settings SET setting = '{0}', value = '{1}' WHERE setting = '{0}'".format(rtnlower(incom[6]),incom[7])
                                            #vals = db.execute(sql)
                                            #settings[rtnlower(incom[6])] = incom[7]
                                            #buildmsg(sock,'NORMAL',myuser,chan,'PRIV',"You have successfully changed {0} to {1}".format(rtnlower(incom[6]),incom[7]))
                                        #else:
                                            #buildmsg(sock,'ERROR',myuser,chan,'PRIV',"Missing Setting Value")
                                    #else:
                                        #buildmsg(sock,'ERROR',myuser,chan,'PRIV',"Missing Setting Name")
                                elif incom[5].upper() == 'LIST':
                                    sql = "SELECT * FROM channels"
                                    records = db.select(sql)
                                    for record in records:
                                        if record[7] == 'enabled':
                                            buildmsg(sock,'NORMAL',myuser,chan,'PRIV',f"\x033CID: {int(record[0])} Server: {record[1]} Channel: {record[2]} Pass: {record[3]} Channel Modes: {record[4]} Chan Options: {record[6]}\x03")
                                            buildmsg(sock,'NORMAL',myuser,chan,'PRIV',f"\x033CID: {int(record[0])} Topic: {record[5]}\x03")
                                        else:
                                            buildmsg(sock,'NORMAL',myuser,chan,'PRIV',f"\x034CID: {int(record[0])} Server: {record[1]} Channel: {record[2]} Pass: {record[3]} Channel Modes: {record[4]} Chan Options: {record[6]}\x03")
                                            buildmsg(sock,'NORMAL',myuser,chan,'PRIV',f"\x034CID: {int(record[0])} Topic: {record[5]}\x03")
                                    buildmsg(sock,'NORMAL',myuser,chan,'PRIV',"Color \x033Green\x03 is enabled, Color \x034Red\x03 is disabled")
                                else:
                                    buildmsg(sock,'ERROR',myuser,chan,'PRIV',"Error, Use Either List, or Chg")
                            else:
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"Error, Use Either List, or Chg")
                        else:
                            buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                    else:
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You can not access channels via channel commands")
                elif incom[4].upper() == 'USER':
                    if imsgtype in ('PMSG', 'PNOTE'):
                        if loggedgetaccess(sock,myuser,chan,'GLOBAL') >= 6:
                            if len(incom) >= 6:
                                if incom[5].upper() == 'ADD':
                                    if len(incom) >= 7:
                                        if len(incom) >=8:
                                            tmpudata = pulluser(rtnlower(incom[6]))
                                            if tmpudata == 'FALSE':
                                                tmppass = pwmaker(incom[7])
                                                sql = "INSERT INTO users (username, password, global, server, channel, msgtype) VALUES ('{rtnlower(incom[6])}', '{tmppass.hexdigest()}', 'NULL', 'NULL', 'NULL', 'msg')"
                                                db.insert(sql)
                                                buildmsg(sock,'NORMAL',myuser,chan,'PRIV',"You have successfully created '{rtnlower(incom[6])}' with the password '{incom[7]}'")
                                            else:
                                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"The username you entered already exists")
                                        else:
                                            buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You only entered a username, please enter a password as well")
                                    else:
                                        buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You are missing <username> <password>")
                                elif incom[5].upper() == 'CHG':
                                    if len(incom) >= 7:
                                        if len(incom) >= 8:
                                            if incom[7].upper() == 'PASS':
                                                if len(incom) >= 9:
                                                    tmppass = pwmaker(incom[8])
                                                    sql = f"UPDATE users SET password = '{tmppass.hexdigest()}' where username = '{incom[6]}'"
                                                    db.execute(sql)
                                                    buildmsg(sock,'NORMAL',myuser,chan,'PRIV',f"You have successfully changed the password for '{rtnlower(incom[6])}'")
                                                else:
                                                    buildmsg(sock,'ERROR',myuser,chan,'PRIV',"Error, Use format <username> PASS <newpass>")
                                            elif incom[7].upper() == 'MSGTYPE':
                                                if len(incom) >= 9:
                                                    if incom[8].lower() == 'notice':
                                                        newtype = 'notice'
                                                    else:
                                                        newtype = 'msg'
                                                    sql = f"UPDATE users SET msgtype = '{newtype}' where username = '{rtnlower(incom[6])}'"
                                                    db.execute(sql)
                                                    if islogged(sock,rtnlower(incom[6])) == 'TRUE':
                                                        loggedin[sock][rtnlower(incom[6])]['msgtype'] = newtype
                                                    buildmsg(sock,'NORMAL',myuser,chan,'PRIV',f"You have successfully changed the message type for '{rtnlower(incom[6])}' to '{newtype}'")
                                                else:
                                                    buildmsg(sock,'ERROR',myuser,chan,'PRIV',"Error, Use format <username> MSGTYPE <notice/msg>")
                                            else:
                                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"Error, Use Either Pass, Msgtype")
                                        else:
                                            buildmsg(sock,'ERROR',myuser,chan,'PRIV',"Error, Use Either Pass, Msgtype")
                                    else:
                                        buildmsg(sock,'ERROR',myuser,chan,'PRIV',"Missing Username")
                                elif incom[5].upper() == 'DEL':
                                    #this bit of coding is only gonna be temperary for the time being due to abuse possiblities
                                    sql = f"DELETE FROM users WHERE username = '{rtnlower(incom[6])}'"
                                    db.execute(sql)
                                    buildmsg(sock,'NORMAL',myuser,chan,'PRIV',f"Deleted {rtnlower(incom[6])} or attempted to delete from the database")
                                elif incom[5].upper() == 'LIST':
                                    sql = "SELECT * FROM users"
                                    records = db.select(sql)
                                    for record in records:
                                        buildmsg(sock,'NORMAL',myuser,chan,'PRIV',f"UID: {int(record[0])} Username: {record[1]} Global: {record[3]} Server: {record[4]} Channel: {record[5]} MsgType: {record[6]}")
                                else:
                                    buildmsg(sock,'ERROR',myuser,chan,'PRIV',"Error, Use Either List, Add, Del, or Chg")
                            else:
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"Error, Use Either List, Add, Del, or Chg")
                        else:
                            buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                    else:
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You can not access users via channel commands")
                elif incom[4].upper() == 'ACCESS':
                    logger.debug("Channel Access called")
                elif incom[4].upper() == 'USERLIST':
                    if loggedgetaccess(sock,myuser,chan,'SERVER') >= 4:
                        sql = "SELECT * FROM users"
                        records = db.select(sql)
                        buildmsg(sock,'NORMAL',myuser,chan,'PRIV',"Displaying user list, only showing Usernames atm, do note may be a big ammount of infomation")
                        for record in records:
                            buildmsg(sock,'NORMAL',myuser,chan,'PRIV',f"Username: {record[1]}")
                    else:
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                elif incom[4].upper() == 'MOWNER':
                    if islogged(sock,myuser) == 'FALSE':
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                    else:
                        if imsgtype in ('PMSG', 'PNOTE'):
                            if len(incom) >= 6:
                                chan = rtnlower(incom[5])
                                passthrough = 1
                            else:
                                passthrough = 0
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter a channel")
                        if imsgtype in ('CMSG', 'CNOTE'):
                            passthrough = 1
                        if passthrough == 1:
                            if getaccess(sock,loggedin[sock][myuser]['username'],chan,'CHANNEL') >= 5:
                                massmodes(sock,myuser,chan,['ADD','q','ALL'])
                            else:
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                elif incom[4].upper() == 'OWNER':
                    if islogged(sock,myuser) == 'FALSE':
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                    else:
                        if imsgtype in ('PMSG', 'PNOTE'):
                            if len(incom) >= 6:
                                chan = rtnlower(incom[5])
                                if len(incom) >= 7:
                                    data = incom[6:]
                                    passthrough = 1
                                else:
                                    passthrough = 0
                                    buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter any nicks")
                            else:
                                passthrough = 0
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter a channel")
                        if imsgtype in ('CMSG', 'CNOTE'):
                            if len(incom) >= 6:
                                data = incom[5:]
                                passthrough = 1
                            else:
                                passthrough = 0
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter any nicks")
                        if passthrough == 1:
                            if getaccess(sock,loggedin[sock][myuser]['username'],chan,'CHANNEL') >= 5:
                                massmodes(sock,myuser,chan,['ADD','q',data])
                            else:
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                elif incom[4].upper() == 'MDEOWNER':
                    if islogged(sock,myuser) == 'FALSE':
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                    else:
                        if imsgtype in ('PMSG', 'PNOTE'):
                            if len(incom) >= 6:
                                chan = rtnlower(incom[5])
                                passthrough = 1
                            else:
                                passthrough = 0
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter a channel")
                        if imsgtype in ('CMSG', 'CNOTE'):
                            passthrough = 1
                        if passthrough == 1:
                            if getaccess(sock,loggedin[sock][myuser]['username'],chan,'CHANNEL') >= 5:
                                massmodes(sock,myuser,chan,['REM','q','BC'])
                            else:
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                elif incom[4].upper() == 'DEOWNER':
                    if islogged(sock,myuser) == 'FALSE':
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                    else:
                        if imsgtype in ('PMSG', 'PNOTE'):
                            if len(incom) >= 6:
                                chan = rtnlower(incom[5])
                                if len(incom) >= 7:
                                    data = incom[6:]
                                    passthrough = 1
                                else:
                                    passthrough = 0
                                    buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter any nicks")
                            else:
                                passthrough = 0
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter a channel")
                        if imsgtype in ('CMSG', 'CNOTE'):
                            if len(incom) >= 6:
                                data = incom[5:]
                                passthrough = 1
                            else:
                                passthrough = 0
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter any nicks")
                        if passthrough == 1:
                            if getaccess(sock,loggedin[sock][myuser]['username'],chan,'CHANNEL') >= 5:
                                massmodes(sock,myuser,chan,['REM','q',data])
                            else:
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                elif incom[4].upper() == 'OWNERME':
                    if islogged(sock,myuser) == 'FALSE':
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                    else:
                        if imsgtype in ('PMSG', 'PNOTE'):
                            if len(incom) >= 6:
                                chan = rtnlower(incom[5])
                                passthrough = 1
                            else:
                                passthrough = 0
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter a channel")
                        if imsgtype in ('CMSG', 'CNOTE'):
                            passthrough = 1
                        if passthrough == 1:
                            if getaccess(sock,loggedin[sock][myuser]['username'],chan,'CHANNEL') >= 5:
                                massmodes(sock,myuser,chan,['ADD','q',myuser]) #can be ADD or REM
                            else:
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                elif incom[4].upper() == 'DEOWNERME':
                    if islogged(sock,myuser) == 'FALSE':
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                    else:
                        if imsgtype in ('PMSG', 'PNOTE'):
                            if len(incom) >= 6:
                                chan = rtnlower(incom[5])
                                passthrough = 1
                            else:
                                passthrough = 0
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter a channel")
                        if imsgtype in ('CMSG', 'CNOTE'):
                            passthrough = 1
                        if passthrough == 1:
                            if getaccess(sock,loggedin[sock][myuser]['username'],chan,'CHANNEL') >= 5:
                                massmodes(sock,myuser,chan,['REM','q',myuser])
                            else:
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                elif incom[4].upper() == 'MPROTECT':
                    if islogged(sock,myuser) == 'FALSE':
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                    else:
                        if imsgtype in ('PMSG', 'PNOTE'):
                            if len(incom) >= 6:
                                chan = rtnlower(incom[5])
                                passthrough = 1
                            else:
                                passthrough = 0
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter a channel")
                        if imsgtype in ('CMSG', 'CNOTE'):
                            passthrough = 1
                        if passthrough == 1:
                            if getaccess(sock,loggedin[sock][myuser]['username'],chan,'CHANNEL') >= 5:
                                massmodes(sock,myuser,chan,['ADD','a','ALL'])
                            else:
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                elif incom[4].upper() == 'PROTECT':
                    if islogged(sock,myuser) == 'FALSE':
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                    else:
                        if imsgtype in ('PMSG', 'PNOTE'):
                            if len(incom) >= 6:
                                chan = rtnlower(incom[5])
                                if len(incom) >= 7:
                                    data = incom[6:]
                                    passthrough = 1
                                else:
                                    passthrough = 0
                                    buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter any nicks")
                            else:
                                passthrough = 0
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter a channel")
                        if imsgtype in ('CMSG', 'CNOTE'):
                            if len(incom) >= 6:
                                data = incom[5:]
                                passthrough = 1
                            else:
                                passthrough = 0
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter any nicks")
                        if passthrough == 1:
                            if getaccess(sock,loggedin[sock][myuser]['username'],chan,'CHANNEL') >= 5:
                                massmodes(sock,myuser,chan,['ADD','a',data])
                            else:
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                elif incom[4].upper() == 'MDEPROTECT':
                    if islogged(sock,myuser) == 'FALSE':
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                    else:
                        if imsgtype in ('PMSG', 'PNOTE'):
                            if len(incom) >= 6:
                                chan = rtnlower(incom[5])
                                passthrough = 1
                            else:
                                passthrough = 0
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter a channel")
                        if imsgtype in ('CMSG', 'CNOTE'):
                            passthrough = 1
                        if passthrough == 1:
                            if getaccess(sock,loggedin[sock][myuser]['username'],chan,'CHANNEL') >= 5:
                                massmodes(sock,myuser,chan,['REM','a','BC'])
                            else:
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                elif incom[4].upper() == 'DEPROTECT':
                    if islogged(sock,myuser) == 'FALSE':
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                    else:
                        if imsgtype in ('PMSG', 'PNOTE'):
                            if len(incom) >= 6:
                                chan = rtnlower(incom[5])
                                if len(incom) >= 7:
                                    data = incom[6:]
                                    passthrough = 1
                                else:
                                    passthrough = 0
                                    buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter any nicks")
                            else:
                                passthrough = 0
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter a channel")
                        if imsgtype in ('CMSG', 'CNOTE'):
                            if len(incom) >= 6:
                                data = incom[5:]
                                passthrough = 1
                            else:
                                passthrough = 0
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter any nicks")
                        if passthrough == 1:
                            if getaccess(sock,loggedin[sock][myuser]['username'],chan,'CHANNEL') >= 5:
                                massmodes(sock,myuser,chan,['REM','a',data])
                            else:
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                elif incom[4].upper() == 'PROTECTME':
                    if islogged(sock,myuser) == 'FALSE':
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                    else:
                        if imsgtype in ('PMSG', 'PNOTE'):
                            if len(incom) >= 6:
                                chan = rtnlower(incom[5])
                                passthrough = 1
                            else:
                                passthrough = 0
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter a channel")
                        if imsgtype in ('CMSG', 'CNOTE'):
                            passthrough = 1
                        if passthrough == 1:
                            if getaccess(sock,loggedin[sock][myuser]['username'],chan,'CHANNEL') >= 4:
                                massmodes(sock,myuser,chan,['ADD','a',myuser]) #can be ADD or REM
                            else:
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                elif incom[4].upper() == 'DEPROTECTME':
                    if islogged(sock,myuser) == 'FALSE':
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                    else:
                        if imsgtype in ('PMSG', 'PNOTE'):
                            if len(incom) >= 6:
                                chan = rtnlower(incom[5])
                                passthrough = 1
                            else:
                                passthrough = 0
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter a channel")
                        if imsgtype in ('CMSG', 'CNOTE'):
                            passthrough = 1
                        if passthrough == 1:
                            if getaccess(sock,loggedin[sock][myuser]['username'],chan,'CHANNEL') >= 4:
                                massmodes(sock,myuser,chan,['REM','a',myuser])
                            else:
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                elif incom[4].upper() == 'MOP':
                    if islogged(sock,myuser) == 'FALSE':
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                    else:
                        if imsgtype in ('PMSG', 'PNOTE'):
                            if len(incom) >= 6:
                                chan = rtnlower(incom[5])
                                passthrough = 1
                            else:
                                passthrough = 0
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter a channel")
                        if imsgtype in ('CMSG', 'CNOTE'):
                            passthrough = 1
                        if passthrough == 1:
                            if getaccess(sock,loggedin[sock][myuser]['username'],chan,'CHANNEL') >= 3:
                                massmodes(sock,myuser,chan,['ADD','o','ALL'])
                            else:
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                elif incom[4].upper() == 'OP':
                    if islogged(sock,myuser) == 'FALSE':
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                    else:
                        if imsgtype in ('PMSG', 'PNOTE'):
                            if len(incom) >= 6:
                                chan = rtnlower(incom[5])
                                if len(incom) >= 7:
                                    data = incom[6:]
                                    passthrough = 1
                                else:
                                    passthrough = 0
                                    buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter any nicks")
                            else:
                                passthrough = 0
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter a channel")
                        if imsgtype in ('CMSG', 'CNOTE'):
                            if len(incom) >= 6:
                                data = incom[5:]
                                passthrough = 1
                            else:
                                passthrough = 0
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter any nicks")
                        if passthrough == 1:
                            if getaccess(sock,loggedin[sock][myuser]['username'],chan,'CHANNEL') >= 3:
                                massmodes(sock,myuser,chan,['ADD','o',data])
                            else:
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                elif incom[4].upper() == 'MDEOP':
                    if islogged(sock,myuser) == 'FALSE':
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                    else:
                        if imsgtype in ('PMSG', 'PNOTE'):
                            if len(incom) >= 6:
                                chan = rtnlower(incom[5])
                                passthrough = 1
                            else:
                                passthrough = 0
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter a channel")
                        if imsgtype in ('CMSG', 'CNOTE'):
                            passthrough = 1
                        if passthrough == 1:
                            if getaccess(sock,loggedin[sock][myuser]['username'],chan,'CHANNEL') >= 3:
                                massmodes(sock,myuser,chan,['REM','o','BC'])
                            else:
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                elif incom[4].upper() == 'DEOP':
                    if islogged(sock,myuser) == 'FALSE':
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                    else:
                        if imsgtype in ('PMSG', 'PNOTE'):
                            if len(incom) >= 6:
                                chan = rtnlower(incom[5])
                                if len(incom) >= 7:
                                    data = incom[6:]
                                    passthrough = 1
                                else:
                                    passthrough = 0
                                    buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter any nicks")
                            else:
                                passthrough = 0
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter a channel")
                        if imsgtype in ('CMSG', 'CNOTE'):
                            if len(incom) >= 6:
                                data = incom[5:]
                                passthrough = 1
                            else:
                                passthrough = 0
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter any nicks")
                        if passthrough == 1:
                            if getaccess(sock,loggedin[sock][myuser]['username'],chan,'CHANNEL') >= 3:
                                massmodes(sock,myuser,chan,['REM','o',data])
                            else:
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                elif incom[4].upper() == 'OPME':
                    if islogged(sock,myuser) == 'FALSE':
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                    else:
                        if imsgtype in ('PMSG', 'PNOTE'):
                            if len(incom) >= 6:
                                chan = rtnlower(incom[5])
                                passthrough = 1
                            else:
                                passthrough = 0
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter a channel")
                        if imsgtype in ('CMSG', 'CNOTE'):
                            passthrough = 1
                        if passthrough == 1:
                            if getaccess(sock,loggedin[sock][myuser]['username'],chan,'CHANNEL') >= 3:
                                massmodes(sock,myuser,chan,['ADD','o',myuser]) #can be ADD or REM
                            else:
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                elif incom[4].upper() == 'DEOPME':
                    if islogged(sock,myuser) == 'FALSE':
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                    else:
                        if imsgtype in ('PMSG', 'PNOTE'):
                            if len(incom) >= 6:
                                chan = rtnlower(incom[5])
                                passthrough = 1
                            else:
                                passthrough = 0
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter a channel")
                        if imsgtype in ('CMSG', 'CNOTE'):
                            passthrough = 1
                        if passthrough == 1:
                            if getaccess(sock,loggedin[sock][myuser]['username'],chan,'CHANNEL') >= 3:
                                massmodes(sock,myuser,chan,['REM','o',myuser])
                            else:
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                elif incom[4].upper() == 'MHALFOP':
                    if islogged(sock,myuser) == 'FALSE':
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                    else:
                        if imsgtype in ('PMSG', 'PNOTE'):
                            if len(incom) >= 6:
                                chan = rtnlower(incom[5])
                                passthrough = 1
                            else:
                                passthrough = 0
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter a channel")
                        if imsgtype in ('CMSG', 'CNOTE'):
                            passthrough = 1
                        if passthrough == 1:
                            if getaccess(sock,loggedin[sock][myuser]['username'],chan,'CHANNEL') >= 3:
                                massmodes(sock,myuser,chan,['ADD','h','ALL'])
                            else:
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                elif incom[4].upper() == 'HALFOP':
                    if islogged(sock,myuser) == 'FALSE':
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                    else:
                        if imsgtype in ('PMSG', 'PNOTE'):
                            if len(incom) >= 6:
                                chan = rtnlower(incom[5])
                                if len(incom) >= 7:
                                    data = incom[6:]
                                    passthrough = 1
                                else:
                                    passthrough = 0
                                    buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter any nicks")
                            else:
                                passthrough = 0
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter a channel")
                        if imsgtype in ('CMSG', 'CNOTE'):
                            if len(incom) >= 6:
                                data = incom[5:]
                                passthrough = 1
                            else:
                                passthrough = 0
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter any nicks")
                        if passthrough == 1:
                            if getaccess(sock,loggedin[sock][myuser]['username'],chan,'CHANNEL') >= 3:
                                massmodes(sock,myuser,chan,['ADD','h',data])
                            else:
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                elif incom[4].upper() == 'MDEHALFOP':
                    if islogged(sock,myuser) == 'FALSE':
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                    else:
                        if imsgtype in ('PMSG', 'PNOTE'):
                            if len(incom) >= 6:
                                chan = rtnlower(incom[5])
                                passthrough = 1
                            else:
                                passthrough = 0
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter a channel")
                        if imsgtype in ('CMSG', 'CNOTE'):
                            passthrough = 1
                        if passthrough == 1:
                            if getaccess(sock,loggedin[sock][myuser]['username'],chan,'CHANNEL') >= 3:
                                massmodes(sock,myuser,chan,['REM','h','BC'])
                            else:
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                elif incom[4].upper() == 'DEHALFOP':
                    if islogged(sock,myuser) == 'FALSE':
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                    else:
                        if imsgtype in ('PMSG', 'PNOTE'):
                            if len(incom) >= 6:
                                chan = rtnlower(incom[5])
                                if len(incom) >= 7:
                                    data = incom[6:]
                                    passthrough = 1
                                else:
                                    passthrough = 0
                                    buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter any nicks")
                            else:
                                passthrough = 0
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter a channel")
                        if imsgtype in ('CMSG', 'CNOTE'):
                            if len(incom) >= 6:
                                data = incom[5:]
                                passthrough = 1
                            else:
                                passthrough = 0
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter any nicks")
                        if passthrough == 1:
                            if getaccess(sock,loggedin[sock][myuser]['username'],chan,'CHANNEL') >= 3:
                                massmodes(sock,myuser,chan,['REM','h',data])
                            else:
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                elif incom[4].upper() == 'HALFOPME':
                    if islogged(sock,myuser) == 'FALSE':
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                    else:
                        if imsgtype in ('PMSG', 'PNOTE'):
                            if len(incom) >= 6:
                                chan = rtnlower(incom[5])
                                passthrough = 1
                            else:
                                passthrough = 0
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter a channel")
                        if imsgtype in ('CMSG', 'CNOTE'):
                            passthrough = 1
                        if passthrough == 1:
                            if getaccess(sock,loggedin[sock][myuser]['username'],chan,'CHANNEL') >= 2:
                                massmodes(sock,myuser,chan,['ADD','h',myuser]) #can be ADD or REM
                            else:
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                elif incom[4].upper() == 'DEHALFOPME':
                    if islogged(sock,myuser) == 'FALSE':
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                    else:
                        if imsgtype in ('PMSG', 'PNOTE'):
                            if len(incom) >= 6:
                                chan = rtnlower(incom[5])
                                passthrough = 1
                            else:
                                passthrough = 0
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter a channel")
                        if imsgtype in ('CMSG', 'CNOTE'):
                            passthrough = 1
                        if passthrough == 1:
                            if getaccess(sock,loggedin[sock][myuser]['username'],chan,'CHANNEL') >= 2:
                                massmodes(sock,myuser,chan,['REM','h',myuser])
                            else:
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                elif incom[4].upper() == 'MVOICE':
                    if islogged(sock,myuser) == 'FALSE':
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                    else:
                        if imsgtype in ('PMSG', 'PNOTE'):
                            if len(incom) >= 6:
                                chan = rtnlower(incom[5])
                                passthrough = 1
                            else:
                                passthrough = 0
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter a channel")
                        if imsgtype in ('CMSG', 'CNOTE'):
                            passthrough = 1
                        if passthrough == 1:
                            if getaccess(sock,loggedin[sock][myuser]['username'],chan,'CHANNEL') >= 2:
                                massmodes(sock,myuser,chan,['ADD','v','ALL'])
                            else:
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                elif incom[4].upper() == 'VOICE':
                    if islogged(sock,myuser) == 'FALSE':
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                    else:
                        if imsgtype in ('PMSG', 'PNOTE'):
                            if len(incom) >= 6:
                                chan = rtnlower(incom[5])
                                if len(incom) >= 7:
                                    data = incom[6:]
                                    passthrough = 1
                                else:
                                    passthrough = 0
                                    buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter any nicks")
                            else:
                                passthrough = 0
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter a channel")
                        if imsgtype in ('CMSG', 'CNOTE'):
                            if len(incom) >= 6:
                                data = incom[5:]
                                passthrough = 1
                            else:
                                passthrough = 0
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter any nicks")
                        if passthrough == 1:
                            if getaccess(sock,loggedin[sock][myuser]['username'],chan,'CHANNEL') >= 2:
                                massmodes(sock,myuser,chan,['ADD','v',data])
                            else:
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                elif incom[4].upper() == 'MDEVOICE':
                    if islogged(sock,myuser) == 'FALSE':
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                    else:
                        if imsgtype in ('PMSG', 'PNOTE'):
                            if len(incom) >= 6:
                                chan = rtnlower(incom[5])
                                passthrough = 1
                            else:
                                passthrough = 0
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter a channel")
                        if imsgtype in ('CMSG', 'CNOTE'):
                            passthrough = 1
                        if passthrough == 1:
                            if getaccess(sock,loggedin[sock][myuser]['username'],chan,'CHANNEL') >= 2:
                                massmodes(sock,myuser,chan,['REM','v','BC'])
                            else:
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                elif incom[4].upper() == 'DEVOICE':
                    if islogged(sock,myuser) == 'FALSE':
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                    else:
                        if imsgtype in ('PMSG', 'PNOTE'):
                            if len(incom) >= 6:
                                chan = rtnlower(incom[5])
                                if len(incom) >= 7:
                                    data = incom[6:]
                                    passthrough = 1
                                else:
                                    passthrough = 0
                                    buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter any nicks")
                            else:
                                passthrough = 0
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter a channel")
                        if imsgtype in ('CMSG', 'CNOTE'):
                            if len(incom) >= 6:
                                data = incom[5:]
                                passthrough = 1
                            else:
                                passthrough = 0
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter any nicks")
                        if passthrough == 1:
                            if getaccess(sock,loggedin[sock][myuser]['username'],chan,'CHANNEL') >= 2:
                                massmodes(sock,myuser,chan,['REM','v',data])
                            else:
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                elif incom[4].upper() == 'VOICEME':
                    if islogged(sock,myuser) == 'FALSE':
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                    else:
                        if imsgtype in ('PMSG', 'PNOTE'):
                            if len(incom) >= 6:
                                chan = rtnlower(incom[5])
                                passthrough = 1
                            else:
                                passthrough = 0
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter a channel")
                        if imsgtype in ('CMSG', 'CNOTE'):
                            passthrough = 1
                        if passthrough == 1:
                            if getaccess(sock,loggedin[sock][myuser]['username'],chan,'CHANNEL') >= 1:
                                massmodes(sock,myuser,chan,['ADD','v',myuser]) #can be ADD or REM
                            else:
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                elif incom[4].upper() == 'DEVOICEME':
                    if islogged(sock,myuser) == 'FALSE':
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                    else:
                        if imsgtype in ('PMSG', 'PNOTE'):
                            if len(incom) >= 6:
                                chan = rtnlower(incom[5])
                                passthrough = 1
                            else:
                                passthrough = 0
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter a channel")
                        if imsgtype in ('CMSG', 'CNOTE'):
                            passthrough = 1
                        if passthrough == 1:
                            if getaccess(sock,loggedin[sock][myuser]['username'],chan,'CHANNEL') >= 1:
                                massmodes(sock,myuser,chan,['REM','v',myuser])
                            else:
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                elif incom[4].upper() == 'SAY':
                    if islogged(sock,myuser) == 'FALSE':
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                    else:
                        if imsgtype in ('PMSG', 'PNOTE'):
                            if len(incom) >= 6:
                                chan = rtnlower(incom[5])
                                if len(incom) >= 7:
                                    data = incom[6:]
                                    passthrough = 1
                                else:
                                    passthrough = 0
                                    buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter a message")
                            else:
                                passthrough = 0
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter a channel")
                        if imsgtype in ('CMSG', 'CNOTE'):
                            if len(incom) >= 6:
                                data = incom[5:]
                                passthrough = 1
                            else:
                                passthrough = 0
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter a message")
                        if passthrough == 1:
                            if getaccess(sock,loggedin[sock][myuser]['username'],chan,'CHANNEL') >= 1:
                                sts(sock,f"PRIVMSG {chan} :{splitjoiner(data)}")
                            else:
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                elif incom[4].upper() == 'ACT':
                    if islogged(sock,myuser) == 'FALSE':
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                    else:
                        if imsgtype in ('PMSG', 'PNOTE'):
                            if len(incom) >= 6:
                                chan = rtnlower(incom[5])
                                if len(incom) >= 7:
                                    data = incom[6:]
                                    passthrough = 1
                                else:
                                    passthrough = 0
                                    buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter a action")
                            else:
                                passthrough = 0
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter a channel")
                        if imsgtype in ('CMSG', 'CNOTE'):
                            if len(incom) >= 6:
                                data = incom[5:]
                                passthrough = 1
                            else:
                                passthrough = 0
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter a action")
                        if passthrough == 1:
                            if getaccess(sock,loggedin[sock][myuser]['username'],chan,'CHANNEL') >= 1:
                                sts(sock,f"PRIVMSG {chan} :\x01ACTION {splitjoiner(data)}\x01")
                            else:
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                elif incom[4].upper() == 'ACCOUNT':
                    if imsgtype in ('PMSG', 'PNOTE'):
                        if islogged(sock,myuser) == 'TRUE':
                            if len(incom) >= 6:
                                userdetails = pulluser(loggedin[sock][myuser]['username'])
                                if incom[5].upper() == 'CHGPASS':
                                    if len(incom) >= 7:
                                        if len(incom) >= 8:
                                            tmppass = pwmaker(incom[6])
                                            if userdetails['password'] == tmppass.hexdigest():
                                                tmppass2 = pwmaker(incom[7])
                                                sql = f"UPDATE users SET password = '{tmppass2.hexdigest()}' where id = '{userdetails['id']}'"
                                                db.execute(sql)
                                                buildmsg(sock,'NORMAL',myuser,chan,'PRIV',"You have successfully changed your password.")
                                            else:
                                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You sure you entered your current password right")
                                        else:
                                            buildmsg(sock,'ERROR',myuser,chan,'PRIV',"Missing New Password")
                                    else:
                                        buildmsg(sock,'ERROR',myuser,chan,'PRIV',"Missing Current Password")
                                if incom[5].upper() == 'MSGTYPE':
                                    if len(incom) >= 7:
                                        if incom[6].lower() == 'notice':
                                            newtype = 'notice'
                                        else:
                                            newtype = 'msg'
                                        sql = f"UPDATE users SET msgtype = '{newtype}' where id = '{userdetails['id']}'"
                                        db.execute(sql)
                                        loggedin[sock][myuser]['msgtype'] = newtype
                                        buildmsg(sock,'NORMAL',myuser,chan,'PRIV',f"You have successfully changed your message type to {newtype}")
                                    else:
                                        buildmsg(sock,'NORMAL',myuser,chan,'PRIV',"You have to enter a Message type")
                            else:
                                buildmsg(sock,'NORMAL',myuser,chan,'PRIV',f"Your Account Details {myuser}({loggedin[sock][myuser]['username']})")
                                buildmsg(sock,'NORMAL',myuser,chan,'PRIV',f"MSGTYPE: {loggedin[sock][myuser]['msgtype']}")
                        else:
                            buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOTLOGGED')
                    else:
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You can not access your account via channel commands")
                elif incom[4].upper() == 'LOGOUT':
                    if islogged(sock,myuser) == 'TRUE':
                        buildmsg(sock,'NORMAL',myuser,chan,'PRIV',f"You have been logged out of {loggedin[sock][myuser]['username']}")
                        del loggedin[sock][myuser]
                    else:
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOTLOGGED')
                elif incom[4].upper() == 'LOGIN':
                    if imsgtype in ('PMSG', 'PNOTE'):
                        if islogged(sock,myuser) == 'FALSE':
                            if len(incom) >= 6:
                                if len(incom) >= 7:
                                    udata = pulluser(rtnlower(incom[5]))
                                    if udata != 'FALSE':
                                        tmppass = pwmaker(incom[6])
                                        if udata['password'] == tmppass.hexdigest():
                                            loggedin[sock][myuser] = {'username': udata['username'], 'msgtype': udata['msgtype'], 'umask': incom[0]}
                                            buildmsg(sock,'NORMAL',myuser,chan,'PRIV',f"You have successfully logged in as {incom[5]}")
                                        else:
                                            buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You have failed to login")
                                    else:
                                        buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter a valid username")
                                else:
                                    buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You only entered a username, please enter a password as well")
                            else:
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You are missing <username> <password>")
                        else:
                            buildmsg(sock,'ERROR',myuser,chan,'PRIV',f"You are already LOGGED In as {loggedin[sock][myuser]['username']}")
                    else:
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You can not log in via channel commands")
                elif incom[4].upper() == 'REGISTER':
                    if imsgtype in ('PMSG', 'PNOTE'):
                        if islogged(sock,myuser) == 'FALSE':
                            if len(incom) >= 6:
                                if len(incom) >=7:
                                    tmpudata = pulluser(rtnlower(incom[5]))
                                    if tmpudata == 'FALSE':
                                        tmppass = pwmaker(incom[6])
                                        sql = f"INSERT INTO users (username, password, global, server, channel, msgtype) VALUES ('{rtnlower(incom[5])}', '{tmppass.hexdigest()}', 'NULL', 'NULL', 'NULL', 'msg')"
                                        db.insert(sql)
                                        loggedin[sock][myuser] = {'username': rtnlower(incom[5]), 'msgtype': 'msg', 'umask': incom[0]}
                                        buildmsg(sock,'NORMAL',myuser,chan,'PRIV',f"You have successfully registered as {incom[5]} and have been auto logged-in")
                                    else:
                                        buildmsg(sock,'ERROR',myuser,chan,'PRIV',"The username you entered already exists")
                                else:
                                    buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You only entered a username, please enter a password as well")
                            else:
                                buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You are missing <username> <password>")
                        else:
                            buildmsg(sock,'ERROR',myuser,chan,'PRIV','LOGIN')
                    else:
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You can not register via channel commands")
                elif incom[4].upper() == 'HELP':
                    if imsgtype in ('PMSG', 'PNOTE'):
                        if len(incom) >= 6:
                            chan = incom[5]
                    helpcmd(sock,myuser,chan,incom)
                elif incom[4].upper() == 'WHOIS':
                    if imsgtype in ('PMSG', 'PNOTE'):
                        if len(incom) >= 6:
                            chan = incom[5]
                            if len(incom) >= 7:
                                uwho = incom[6]
                                passthrough = 1
                            else:
                                uwho = 'NULL'
                                passthrough = 1
                        else:
                            buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter a channel")
                    if imsgtype in ('CMSG', 'CNOTE'):
                        if len(incom) >= 6:
                            uwho = incom[5]
                            passthrough = 1
                        else:
                            uwho = 'NULL'
                            passthrough = 1
                    if passthrough == 1:
                        getwhois(sock,myuser,chan,'WHOIS',uwho)
                elif incom[4].upper() == 'WHOAMI':
                    if imsgtype in ('PMSG', 'PNOTE'):
                        if len(incom) >= 6:
                            chan = rtnlower(incom[5])
                            passthrough = 1
                        else:
                            buildmsg(sock,'ERROR',myuser,chan,'PRIV',"You didn't enter a channel")
                    if imsgtype in ('CMSG', 'CNOTE'):
                        passthrough = 1
                    if passthrough == 1:
                        getwhois(sock,myuser,chan,'WHOAMI','NULL')
                elif incom[4].upper() == 'VERSION':
                    buildmsg(sock,'NORMAL',myuser,chan,'PRIV',f"Ch3wyB0t Version {__version__}")
                elif incom[4].upper() == 'TESTCMD':
                    if loggedgetaccess(sock,myuser,chan,'GLOBAL') >= 7:
                        debug(sock,mysockets[sock])
                    else:
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                elif incom[4].upper() == 'TESTDATA':
                    if loggedgetaccess(sock,myuser,chan,'GLOBAL') >= 7:
                        debug(sock,mysockets)
                    else:
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                elif incom[4].upper() == 'TEST':
                    if loggedgetaccess(sock,myuser,chan,'GLOBAL') >= 7:

                        #sts(sock,"MODE :{0}".format(mysockets[sock]['nick']))
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV',"data 'blarg'")
                    else:
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESS')
                else:
                    debug(sock,incom)
                    if imsgtype in ('CMSG', 'CNOTE'):
                        buildmsg(sock,'ERROR',myuser,chan,'CHAN',f"The command {incom[4]} doesn't exist at the momment")
                    if imsgtype in ('PMSG', 'PNOTE'):
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV',f"The command {incom[4]} doesn't exist at the momment")
        else:
            if imsgtype == 'PNOTE':
                if myuser == 'NickServ':
                    if len(incom) >= 9:
                        if (incom[6] == 'registered') and (incom[8] == 'protected.'):
                            if mysockets[sock]['server']['nickservpass'] != 'NULL':
                                mysockets[sock]['nickserv'] = '1ST'
                        elif (incom[6] == 'NickServ') and (incom[7] == 'IDENTIFY'):
                            if (mysockets[sock]['server']['nickservpass'] != 'NULL') and (mysockets[sock]['nickserv'] == '1ST'):
                                del mysockets[sock]['nickserv']
                                sts(sock,f"PRIVMSG NickServ :IDENTIFY {mysockets[sock]['server']['nickservpass']}")
                                mysockets[sock]['identified'] = 'TRUE'
                                autojoinchannels(sock)
                else:
                    debug(sock,incom)
            else:
                #buildmsg(sock,'NORMAL',myuser,chan,'PRIV',output) #imsgtypes are NORMAL, HELP, ERROR  mtype are PRIV, CHAN
                debug(sock,incom)
    else:
        #blarg = 'TRUE'
        #buildmsg(sock,'ERROR',myuser,chan,'PRIV',"The command {0} doesn't exist at the momment".format(incom[3]))
        debug(sock,incom)

def helpcmd(sock,myuser,chan,incom):
    """
    Help command
    """
    buildmsg(sock,'HELP',myuser,chan,'PRIV',f"{settings['botname']} help system")
    buildmsg(sock,'HELP',myuser,chan,'PRIV',"If you need help on a certain command go help <command>")
    buildmsg(sock,'HELP',myuser,chan,'PRIV',f"{settings['chancom']}{settings['signal']} = CHAN, {settings['dcccom']}{settings['signal']} = DCC, {settings['pvtcom']}{settings['signal']} = MSG")
    if len(incom) >= 6:
        if chan == incom[5]:
            if len(incom) >= 7:
                hcmds = incom[6:]
                processhelp = 1
            else:
                processhelp = 0
        else:
            hcmds = incom[5:]
            processhelp = 1
    else:
        processhelp = 0
    if processhelp == 1:
        #debug(sock,len(incom))
        if hcmds[0].upper() == 'EXIT':
            if loggedgetaccess(sock,myuser,chan,'GLOBAL') >= 6:
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(EXIT)- This Command will cause the bot to exit completely")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(EXIT)- Command Structure: {settings['pvtcom']}{settings['signal']} exit <message>")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(EXIT)- Command Structure: {settings['chancom']}{settings['signal']} exit <message>")
            else:
                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESSHELP')
        elif hcmds[0].upper() == 'RAW':
            if loggedgetaccess(sock,myuser,chan,'GLOBAL') >= 7:
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(RAW)- This Command is super dangerous as it will send whatever is entered into it")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(RAW)- Command Structure: {settings['pvtcom']}{settings['signal']} raw <data to send>")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(RAW)- Command Structure: {settings['chancom']}{settings['signal']} raw <data to send>")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(RAW)- It is highly recommend you DO NOT use this command")
            else:
                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESSHELP')
        elif hcmds[0].upper() == 'RAWDB':
            if loggedgetaccess(sock,myuser,chan,'GLOBAL') >= 7:
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(RAWDB)- This Command is super dangerous as it will send whatever is entered into it")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(RAWDB)- Command Structure: {settings['pvtcom']}{settings['signal']} rawdb <data to send>")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(RAWDB)- Command Structure: {settings['chancom']}{settings['signal']} rawdb <data to send>")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(RAWDB)- It is highly recommend you DO NOT use this command")
            else:
                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESSHELP')
        elif hcmds[0].upper() == 'QUIT':
            if loggedgetaccess(sock,myuser,chan,'SERVER') >= 6:
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(QUIT)- This Command will cause the bot to quit from the current network")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(QUIT)- Command Structure: {settings['pvtcom']}{settings['signal']} quit <message>")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(QUIT)- Command Structure: {settings['chancom']}{settings['signal']} quit <message>")
            else:
                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESSHELP')
        elif hcmds[0].upper() == 'REHASH':
            if loggedgetaccess(sock,myuser,chan,'GLOBAL') >= 6:
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(REHASH)- This Command will cause the bot to reload from the database")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(REHASH)- Command Structure: {settings['pvtcom']}{settings['signal']} rehash")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(REHASH)- Command Structure: {settings['chancom']}{settings['signal']} rehash")
            else:
                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESSHELP')
        elif hcmds[0].upper() == 'SETTINGS':
            if loggedgetaccess(sock,myuser,chan,'GLOBAL') >= 6:
                if len(hcmds) >= 2:
                    if hcmds[1].upper() == 'LIST':
                        buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(SETTINGS)-(LIST)- This Command will list the values that are currently in the bots settings")
                        buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(SETTINGS)-(LIST)- Command Structure: {settings['pvtcom']}{settings['signal']} settings list")
                    elif hcmds[1].upper() == 'SET':
                        buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(SETTINGS)-(SET)- This Command will set the value you pick and update both local and the db")
                        buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(SETTINGS)-(SET)- Command Structure: {settings['pvtcom']}{settings['signal']} settings set <setting> <value>")
                    else:
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV',f"-(SETTINGS)- The help topic account {hcmds[1]} is not in the database")
                else:
                    buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(SETTINGS)- This Command deals with the bots settings")
                    buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(SETTINGS)- Command Structure: {settings['pvtcom']}{settings['signal']} settings [<list>][<set> <setting> <value>]")
                    buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(SETTINGS)- Topics available: list set")
            else:
                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESSHELP')

        #loggedgetaccess(sock,myuser,chan,type)
        elif hcmds[0].upper() == 'MOWNER':
            if loggedgetaccess(sock,myuser,chan,'CHANNEL') >= 5:
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(MOWNER)- This Command will Owner everyone in <channel>")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(MOWNER)- Command Structure: {settings['pvtcom']}{settings['signal']} MOwner <channel>")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(MOWNER)- Command Structure: {settings['chancom']}{settings['signal']} MOwner")
            else:
                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESSHELP')
        elif hcmds[0].upper() == 'OWNER':
            if loggedgetaccess(sock,myuser,chan,'CHANNEL') >= 5:
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(OWNER)- This Command will Owner the <nicks> you pick on <channel>")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(OWNER)- Command Structure: {settings['pvtcom']}{settings['signal']} Owner <channel> <nick> [<nick> [<nick>]]")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(OWNER)- Command Structure: {settings['chancom']}{settings['signal']} Owner <nick> [<nick> [<nick>]]")
            else:
                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESSHELP')
        elif hcmds[0].upper() == 'MDEOWNER':
            if loggedgetaccess(sock,myuser,chan,'CHANNEL') >= 5:
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(MDEOWNER)- This Command will DeOwner everyone in <channel> but the bot and you")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(MDEOWNER)- Command Structure: {settings['pvtcom']}{settings['signal']} MDeOwner <channel>")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(MDEOWNER)- Command Structure: {settings['chancom']}{settings['signal']} MDeOwner")
            else:
                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESSHELP')
        elif hcmds[0].upper() == 'DEOWNER':
            if loggedgetaccess(sock,myuser,chan,'CHANNEL') >= 5:
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(DEOWNER)- This Command will de-Owner the <nicks> you pick on <channel>")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(DEOWNER)- Command Structure: {settings['pvtcom']}{settings['signal']} DeOwner <channel> <nick> [<nick> [<nick>]]")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(DEOWNER)- Command Structure: {settings['chancom']}{settings['signal']} DeOwner <nick> [<nick> [<nick>]]")
            else:
                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESSHELP')
        elif hcmds[0].upper() == 'OWNERME':
            if loggedgetaccess(sock,myuser,chan,'CHANNEL') >= 5:
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(OWNERME)- This Command will Owner yourself on <channel>")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(OWNERME)- Command Structure: {settings['pvtcom']}{settings['signal']} OwnerMe <channel>")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(OWNERME)- Command Structure: {settings['chancom']}{settings['signal']} OwnerMe")
            else:
                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESSHELP')
        elif hcmds[0].upper() == 'DEOWNERME':
            if loggedgetaccess(sock,myuser,chan,'CHANNEL') >= 5:
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(DEOWNERME)- This Command will de-Owner yourself on <channel>")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(DEOWNERME)- Command Structure: {settings['pvtcom']}{settings['signal']} DeOwnerMe <channel>")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(DEOWNERME)- Command Structure: {settings['chancom']}{settings['signal']} DeOwnerMe")
            else:
                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESSHELP')
        elif hcmds[0].upper() == 'MPROTECT':
            if loggedgetaccess(sock,myuser,chan,'CHANNEL') >= 5:
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(MPROTECT)- This Command will Protect everyone in <channel>")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(MPROTECT)- Command Structure: {settings['pvtcom']}{settings['signal']} MProtect <channel>")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(MPROTECT)- Command Structure: {settings['chancom']}{settings['signal']} MProtect")
            else:
                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESSHELP')
        elif hcmds[0].upper() == 'PROTECT':
            if loggedgetaccess(sock,myuser,chan,'CHANNEL') >= 5:
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(PROTECT)- This Command will Protect the <nicks> you pick on <channel>")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(PROTECT)- Command Structure: {settings['pvtcom']}{settings['signal']} Protect <channel> <nick> [<nick> [<nick>]]")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(PROTECT)- Command Structure: {settings['chancom']}{settings['signal']} Protect <nick> [<nick> [<nick>]]")
            else:
                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESSHELP')
        elif hcmds[0].upper() == 'MDEPROTECT':
            if loggedgetaccess(sock,myuser,chan,'CHANNEL') >= 5:
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(MDEPROTECT)- This Command will DeProtect everyone in <channel> but the bot and you")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(MDEPROTECT)- Command Structure: {settings['pvtcom']}{settings['signal']} MDeProtect <channel>")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(MDEPROTECT)- Command Structure: {settings['chancom']}{settings['signal']} MDeProtect")
            else:
                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESSHELP')
        elif hcmds[0].upper() == 'DEPROTECT':
            if loggedgetaccess(sock,myuser,chan,'CHANNEL') >= 5:
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(DEPROTECT)- This Command will de-Protect the <nicks> you pick on <channel>")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(DEPROTECT)- Command Structure: {settings['pvtcom']}{settings['signal']} DeProtect <channel> <nick> [<nick> [<nick>]]")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(DEPROTECT)- Command Structure: {settings['chancom']}{settings['signal']} DeProtect <nick> [<nick> [<nick>]]")
            else:
                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESSHELP')
        elif hcmds[0].upper() == 'PROTECTME':
            if loggedgetaccess(sock,myuser,chan,'CHANNEL') >= 4:
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(PROTECTME)- This Command will Protect yourself on <channel>")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(PROTECTME)- Command Structure: {settings['pvtcom']}{settings['signal']} ProtectMe <channel>")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(PROTECTME)- Command Structure: {settings['chancom']}{settings['signal']} ProtectMe")
            else:
                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESSHELP')
        elif hcmds[0].upper() == 'DEPROTECTME':
            if loggedgetaccess(sock,myuser,chan,'CHANNEL') >= 4:
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(DEPROTECTME)- This Command will de-Protect yourself on <channel>")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(DEPROTECTME)- Command Structure: {settings['pvtcom']}{settings['signal']} DeProtectMe <channel>")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(DEPROTECTME)- Command Structure: {settings['chancom']}{settings['signal']} DeProtectMe")
            else:
                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESSHELP')
        elif hcmds[0].upper() == 'MOP':
            if loggedgetaccess(sock,myuser,chan,'CHANNEL') >= 3:
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(MOP)- This Command will Op everyone in <channel>")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(MOP)- Command Structure: {settings['pvtcom']}{settings['signal']} MOp <channel>")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(MOP)- Command Structure: {settings['chancom']}{settings['signal']} MOp")
            else:
                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESSHELP')
        elif hcmds[0].upper() == 'OP':
            if loggedgetaccess(sock,myuser,chan,'CHANNEL') >= 3:
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(OP)- This Command will Op the <nicks> you pick on <channel>")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(OP)- Command Structure: {settings['pvtcom']}{settings['signal']} Op <channel> <nick> [<nick> [<nick>]]")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(OP)- Command Structure: {settings['chancom']}{settings['signal']} Op <nick> [<nick> [<nick>]]")
            else:
                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESSHELP')
        elif hcmds[0].upper() == 'MDEOP':
            if loggedgetaccess(sock,myuser,chan,'CHANNEL') >= 3:
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(MDEOP)- This Command will DeOp everyone in <channel> but the bot and you")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(MDEOP)- Command Structure: {settings['pvtcom']}{settings['signal']} MDeOp <channel>")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(MDEOP)- Command Structure: {settings['chancom']}{settings['signal']} MDeOp")
            else:
                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESSHELP')
        elif hcmds[0].upper() == 'DEOP':
            if loggedgetaccess(sock,myuser,chan,'CHANNEL') >= 3:
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(DEOP)- This Command will de-Op the <nicks> you pick on <channel>")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(DEOP)- Command Structure: {settings['pvtcom']}{settings['signal']} DeOp <channel> <nick> [<nick> [<nick>]]")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(DEOP)- Command Structure: {settings['chancom']}{settings['signal']} DeOp <nick> [<nick> [<nick>]]")
            else:
                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESSHELP')
        elif hcmds[0].upper() == 'OPME':
            if loggedgetaccess(sock,myuser,chan,'CHANNEL') >= 3:
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(OPME)- This Command will Op yourself on <channel>")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(OPME)- Command Structure: {settings['pvtcom']}{settings['signal']} OpMe <channel>")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(OPME)- Command Structure: {settings['chancom']}{settings['signal']} OpMe")
            else:
                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESSHELP')
        elif hcmds[0].upper() == 'DEOPME':
            if loggedgetaccess(sock,myuser,chan,'CHANNEL') >= 3:
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(DEOPME)- This Command will de-Op yourself on <channel>")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(DEOPME)- Command Structure: {settings['pvtcom']}{settings['signal']} DeOpMe <channel>")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(DEOPME)- Command Structure: {settings['chancom']}{settings['signal']} DeOpMe")
            else:
                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESSHELP')
        elif hcmds[0].upper() == 'MHALFOP':
            if loggedgetaccess(sock,myuser,chan,'CHANNEL') >= 3:
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(MHALFOP)- This Command will HalfOp everyone in <channel>")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(MHALFOP)- Command Structure: {settings['pvtcom']}{settings['signal']} MHalfOp <channel>")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(MHALFOP)- Command Structure: {settings['chancom']}{settings['signal']} MHalfOp")
            else:
                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESSHELP')
        elif hcmds[0].upper() == 'HALFOP':
            if loggedgetaccess(sock,myuser,chan,'CHANNEL') >= 3:
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(HALFOP)- This Command will HalfOp the <nicks> you pick on <channel>")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(HALFOP)- Command Structure: {settings['pvtcom']}{settings['signal']} HalfOp <channel> <nick> [<nick> [<nick>]]")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(HALFOP)- Command Structure: {settings['chancom']}{settings['signal']} HalfOp <nick> [<nick> [<nick>]]")
            else:
                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESSHELP')
        elif hcmds[0].upper() == 'MDEHALFOP':
            if loggedgetaccess(sock,myuser,chan,'CHANNEL') >= 3:
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(MDEHALFOP)- This Command will DeHalfOp everyone in <channel> but the bot and you")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(MDEHALFOP)- Command Structure: {settings['pvtcom']}{settings['signal']} MDeHalfOp <channel>")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(MDEHALFOP)- Command Structure: {settings['chancom']}{settings['signal']} MDeHalfOp")
            else:
                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESSHELP')
        elif hcmds[0].upper() == 'DEHALFOP':
            if loggedgetaccess(sock,myuser,chan,'CHANNEL') >= 3:
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(DEHALFOP)- This Command will de-HalfOp the <nicks> you pick on <channel>")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(DEHALFOP)- Command Structure: {settings['pvtcom']}{settings['signal']} DeHalfOp <channel> <nick> [<nick> [<nick>]]")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(DEHALFOP)- Command Structure: {settings['chancom']}{settings['signal']} DeHalfOp <nick> [<nick> [<nick>]]")
            else:
                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESSHELP')
        elif hcmds[0].upper() == 'HALFOPME':
            if loggedgetaccess(sock,myuser,chan,'CHANNEL') >= 2:
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(HALFOPME)- This Command will HalfOp yourself on <channel>")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(HALFOPME)- Command Structure: {settings['pvtcom']}{settings['signal']} HalfOpMe <channel>")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(HALFOPME)- Command Structure: {settings['chancom']}{settings['signal']} HalfOpMe")
            else:
                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESSHELP')
        elif hcmds[0].upper() == 'DEHALFOPME':
            if loggedgetaccess(sock,myuser,chan,'CHANNEL') >= 2:
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(DEHALFOPME)- This Command will de-HalfOp yourself on <channel>")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(DEHALFOPME)- Command Structure: {settings['pvtcom']}{settings['signal']} DeHalfOpMe <channel>")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(DEHALFOPME)- Command Structure: {settings['chancom']}{settings['signal']} DeHalfOpMe")
            else:
                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESSHELP')
        elif hcmds[0].upper() == 'MVOICE':
            if loggedgetaccess(sock,myuser,chan,'CHANNEL') >= 2:
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(MVOICE)- This Command will Voice everyone in <channel>")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(MVOICE)- Command Structure: {settings['pvtcom']}{settings['signal']} MVoice <channel>")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(MVOICE)- Command Structure: {settings['chancom']}{settings['signal']} MVoice")
            else:
                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESSHELP')
        elif hcmds[0].upper() == 'VOICE':
            if loggedgetaccess(sock,myuser,chan,'CHANNEL') >= 2:
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(VOICE)- This Command will voice the <nicks> you pick on <channel>")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(VOICE)- Command Structure: {settings['pvtcom']}{settings['signal']} Voice <channel> <nick> [<nick> [<nick>]]")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(VOICE)- Command Structure: {settings['chancom']}{settings['signal']} Voice <nick> [<nick> [<nick>]]")
            else:
                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESSHELP')
        elif hcmds[0].upper() == 'MDEVOICE':
            if loggedgetaccess(sock,myuser,chan,'CHANNEL') >= 2:
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(MDEVOICE)- This Command will DeVoice everyone in <channel> but the bot and you")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(MDEVOICE)- Command Structure: {settings['pvtcom']}{settings['signal']} MDeVoice <channel>")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(MDEVOICE)- Command Structure: {settings['chancom']}{settings['signal']} MDeVoice")
            else:
                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESSHELP')
        elif hcmds[0].upper() == 'DEVOICE':
            if loggedgetaccess(sock,myuser,chan,'CHANNEL') >= 2:
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(DEVOICE)- This Command will de-voice the <nicks> you pick on <channel>")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(DEVOICE)- Command Structure: {settings['pvtcom']}{settings['signal']} DeVoice <channel> <nick> [<nick> [<nick>]]")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(DEVOICE)- Command Structure: {settings['chancom']}{settings['signal']} DeVoice <nick> [<nick> [<nick>]]")
            else:
                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESSHELP')
        elif hcmds[0].upper() == 'VOICEME':
            if loggedgetaccess(sock,myuser,chan,'CHANNEL') >= 1:
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(VOICEME)- This Command will voice yourself on <channel>")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(VOICEME)- Command Structure: {settings['pvtcom']}{settings['signal']} VoiceMe <channel>")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(VOICEME)- Command Structure: {settings['chancom']}{settings['signal']} VoiceMe")
            else:
                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESSHELP')
        elif hcmds[0].upper() == 'DEVOICEME':
            if loggedgetaccess(sock,myuser,chan,'CHANNEL') >= 1:
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(DEVOICEME)- This Command will de-voice yourself on <channel>")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(DEVOICEME)- Command Structure: {settings['pvtcom']}{settings['signal']} DeVoiceMe <channel>")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(DEVOICEME)- Command Structure: {settings['chancom']}{settings['signal']} DeVoiceMe")
            else:
                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESSHELP')
        elif hcmds[0].upper() == 'SAY':
            if loggedgetaccess(sock,myuser,chan,'CHANNEL') >= 1:
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(SAY)- This command will cause the bot to say a message on a channel")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(SAY)- Command Structure: {settings['pvtcom']}{settings['signal']} say <channel> <message>")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(SAY)- Command Structure: {settings['chancom']}{settings['signal']} say <message>")
            else:
                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESSHELP')
        elif hcmds[0].upper() == 'ACT':
            if loggedgetaccess(sock,myuser,chan,'CHANNEL') >= 1:
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(ACT)- This command will cause the bot to do a action on a channel")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(ACT)- Command Structure: {settings['pvtcom']}{settings['signal']} act <channel> <action>")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(ACT)- Command Structure: {settings['chancom']}{settings['signal']} act <action>")
            else:
                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOACCESSHELP')
        elif hcmds[0].upper() == 'ACCOUNT':
            if islogged(sock,myuser) == 'TRUE':
                if len(hcmds) >= 2:
                    if hcmds[1].upper() == 'CHGPASS':
                        buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(ACCOUNT)-(CHGPASS)- This Command will allow you to change your password")
                        buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(ACCOUNT)-(CHGPASS)- Command Structure: {settings['pvtcom']}{settings['signal']} account chgpass <old pass> <new pass>")
                    elif hcmds[1].upper() == 'MSGTYPE':
                        buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(ACCOUNT)-(MSGTYPE)- This Command will allow you to change your Message Type")
                        buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(ACCOUNT)-(MSGTYPE)- Command Structure: {settings['pvtcom']}{settings['signal']} account msgtype <notice/msg>")
                    else:
                        buildmsg(sock,'ERROR',myuser,chan,'PRIV',f"-(ACCOUNT)- The help topic account {hcmds[1]} is not in the database")
                else:
                    buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(ACCOUNT)- This Command will allow the user to do some modifications to their account")
                    buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(ACCOUNT)- Command Structure: {settings['pvtcom']}{settings['signal']} account <chgpass/msgtype>")
                    buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(ACCOUNT)- Topics available: chgpass msgtype")
            else:
                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOTLOGGED')
        elif hcmds[0].upper() == 'LOGOUT':
            if islogged(sock,myuser) == 'TRUE':
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(LOGOUT)- This Command will logout from the bot, this is the only command that works with users that is allowed in channel")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(LOGOUT)- Command Structure: {settings['pvtcom']}{settings['signal']} logout")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(LOGOUT)- Command Structure: {settings['chancom']}{settings['signal']} logout")
            else:
                buildmsg(sock,'ERROR',myuser,chan,'PRIV','NOTLOGGED')
        elif hcmds[0].upper() == 'LOGIN':
            if islogged(sock,myuser) == 'FALSE':
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(LOGIN)- This Command will login to the bot, should the username and password be right")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(LOGIN)- Command Structure: {settings['pvtcom']}{settings['signal']} login <username> <password>")
            else:
                buildmsg(sock,'ERROR',myuser,chan,'PRIV','LOGGED')
        elif hcmds[0].upper() == 'REGISTER':
            if islogged(sock,myuser) == 'FALSE':
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(REGISTER)- This Command will register a user to the bot if that username doesn't already exists")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(REGISTER)- Command Structure: {settings['pvtcom']}{settings['signal']} register <username> <password>")
            else:
                buildmsg(sock,'ERROR',myuser,chan,'PRIV','LOGGED')
        elif hcmds[0].upper() == 'HELP':
            buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(HELP)- This Command Displays The Help System and Certain Command information")
            buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(HELP)- Command Structure: {settings['pvtcom']}{settings['signal']} help <channel> <topic>")
            #buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(HELP)- Command Structure: {0}{1} help <channel> <topic>".format(settings['dcccom'],settings['signal']))
            buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(HELP)- Command Structure: {settings['chancom']}{settings['signal']} help <topic>".format(settings['chancom'],settings['signal']))
        elif hcmds[0].upper() == 'WHOIS':
            buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(WHOIS)- This Command will send you a whois on the <nick> you choose")
            buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(WHOIS)- Command Structure: {settings['pvtcom']}{settings['signal']} whois <channel> <nick>")
            #buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(WHOIS)- Command Structure: {0}{1} whois <channel> <nick>".format(settings['dcccom'],settings['signal']))
            buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(WHOIS)- Command Structure: {settings['chancom']}{settings['signal']} whois <nick>")
        elif hcmds[0].upper() == 'WHOAMI':
            buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(WHOAMI)- This Command will send you a whois on your current logged in user account")
            buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(WHOAMI)- Command Structure: {settings['pvtcom']}{settings['signal']} whoami <channel>")
            #buildmsg(sock,'HELP',myuser,chan,'PRIV',"-(WHOAMI)- Command Structure: {0}{1} whoami <channel>".format(settings['dcccom'],settings['signal']))
            buildmsg(sock,'HELP',myuser,chan,'PRIV',f"-(WHOAMI)- Command Structure: {settings['chancom']}{settings['signal']} whoami")
        else:
            buildmsg(sock,'ERROR',myuser,chan,'PRIV',f"The help topic {hcmds[0]} is not in the database")
    else:
        buildmsg(sock,'HELP',myuser,chan,'PRIV',"The bot has the following Commands Available")
        if islogged(sock,myuser) == 'TRUE':
            if loggedgetaccess(sock,myuser,chan,'GLOBAL') >= 7:
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"Creator Level Access (7) Only (Due to dangerous level to bot and system):")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"Raw Rawdb")
            if loggedgetaccess(sock,myuser,chan,'CHANNEL') >= 6:
                #Master & Creator Commands 6/7 Global, 6 Server, 6 Channel
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"Master Level Access (6):")
                if loggedgetaccess(sock,myuser,chan,'GLOBAL') >= 6:
                    buildmsg(sock,'HELP',myuser,chan,'PRIV',"Exit Rehash Settings") #Server User
                if loggedgetaccess(sock,myuser,chan,'SERVER') >= 6:
                    buildmsg(sock,'HELP',myuser,chan,'PRIV',"Quit") #Channel
                if loggedgetaccess(sock,myuser,chan,'CHANNEL') >= 6:
                    logger.debug("Help description, Master channel")
            if loggedgetaccess(sock,myuser,chan,'CHANNEL') >= 5:
                #Owner Commands - 5 Global, 6 Server, 5 Channel
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"Owner Level Access (5):")
                if loggedgetaccess(sock,myuser,chan,'GLOBAL') >= 5:
                    logger.debug("Help description, Owner Global")
                if loggedgetaccess(sock,myuser,chan,'SERVER') >= 5:
                    logger.debug("Help description, Owner Server")
                if loggedgetaccess(sock,myuser,chan,'CHANNEL') >= 5:
                    buildmsg(sock,'HELP',myuser,chan,'PRIV',"MOwner Owner MDeOwner DeOwner Ownerme DeOwnerme")
                    buildmsg(sock,'HELP',myuser,chan,'PRIV',"MProtect Protect MDeProtect DeProtect")
            if loggedgetaccess(sock,myuser,chan,'CHANNEL') >= 4:
                #Protected Commands - 4 Global, 4 Server, 4 Channel
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"Protected Level Access (4):")
                if loggedgetaccess(sock,myuser,chan,'GLOBAL') >= 4:
                    logger.debug("Help description, Protected Global")
                if loggedgetaccess(sock,myuser,chan,'SERVER') >= 4:
                    logger.debug("Help description, Protected Server")
                if loggedgetaccess(sock,myuser,chan,'CHANNEL') >= 4:
                    buildmsg(sock,'HELP',myuser,chan,'PRIV',"Protectme DeProtectme")
                    #Access Protectme DeProtectme
            if loggedgetaccess(sock,myuser,chan,'CHANNEL') >= 3:
                #Op Commands - 3 Global, 3 Server, 3 Channel
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"Op Level Access (3):")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"MOp Op MDeOp DeOp Opme DeOpme")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"MHalfop Halfop MDeHalfop DeHalfop")
            if loggedgetaccess(sock,myuser,chan,'CHANNEL') >= 2:
                #Half-Op Commands - 2 Global, 2 Server, 2 Channel
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"Half-Op Level Access (2):")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"Halfopme DeHalfopme MVoice Voice MDeVoice DeVoice")
                #channel Kick Ban
            if loggedgetaccess(sock,myuser,chan,'CHANNEL') >= 1:
                #Voice Commands - 1 Global, 1 Server, 1 Channel
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"Voice Level Access (1):")
                buildmsg(sock,'HELP',myuser,chan,'PRIV',"Voiceme DeVoiceme Say Act")
            #Logged in with - 0 Global, 0 Server, 0 Channel
            buildmsg(sock,'HELP',myuser,chan,'PRIV',"Logged In Access (0):")
            buildmsg(sock,'HELP',myuser,chan,'PRIV',"Account Logout")
        else :
            #Logged out with - 0 Global, 0 Server, 0 Channel
            buildmsg(sock,'HELP',myuser,chan,'PRIV',"Logged out Access (0):")
            buildmsg(sock,'HELP',myuser,chan,'PRIV',"Login Register")
        #Anyone Commands - 0 global, 0 server, 0 channel
        buildmsg(sock,'HELP',myuser,chan,'PRIV',"Anyone Can Access (0):")
        buildmsg(sock,'HELP',myuser,chan,'PRIV',"Help Whoami Whois")
        buildmsg(sock,'HELP',myuser,chan,'PRIV',f"Pvt Command: {settings['pvtcom']}{settings['signal']} help <channel> <topic>, Channel Command: {settings['chancom']}{settings['signal']} help <topic>")
    buildmsg(sock,'HELP',myuser,chan,'PRIV',f"End Of {settings['botname']} help system")

def rawp(sock,extra):
    """
    Raw output for debugging i guess
    """
    #buildmsg(sock,'NORMAL',myuser,chan,'PRIV',output) #types are NORMAL, HELP, ERROR  mtype are PRIV, CHAN
    debug(sock,f"this is temp {extra}")

def parse_data(sock,data: str):
    """
    Parse data from the socket and send it on
    """
    screenoutput(sock,'in',data)
    incom = data
    incom = incom.split(' ')
    raw = data
    raw = raw.split(' ')
    stripcount = len(incom)
    while stripcount:
        stripcount = stripcount - 1
        incom[stripcount] = incom[stripcount].strip(':')
        incom[stripcount] = incom[stripcount].strip('\r')
        incom[stripcount] = incom[stripcount].strip('\n')
    stripcount = len(raw)
    while stripcount:
        stripcount = stripcount - 1
        raw[stripcount] = raw[stripcount].strip('\r')
        raw[stripcount] = raw[stripcount].strip('\n')
    sender = incom[0].split('!')
    sender = sender[0]
    if incom[0] == 'PING':
        sts(sock,f"PONG :{incom[1]}")
        mysockets[sock]['lastping'] = time.time()
    elif incom[0] == 'ERROR':
        if (mysockets[sock]['lastcmd'] == 'QUIT') or (mysockets[sock]['lastcmd'] == 'EXIT') or (mysockets[sock]['lastcmd'] == 'RELOAD'):
            mysocket[sock].close()
            del mysocket[sock]
            del mysockets[sock]
        else:
            mysocket[sock].close()
            doconnection(sock)
            mysockets[sock]['lastping'] = time.time()
    elif len(incom) >= 2:
        #start the numerics
        if incom[1] == '001':
            #debug(sock,"Numeric 001 - Welcome to server")
            mysockets[sock]['networkname'] = incom[6]
            mysockets[sock]['connectumask'] = incom[9]
            sts(sock,f"MODE {mysockets[sock]['nick']} +B")
            operupcheck(sock)
            if mysockets[sock]['identified'] == 'TRUE':
                autojoinchannels(sock)
        elif incom[1] == '002':
            logger.debug("Numeric 002: %s", incom[2:])
        elif incom[1] == '003':
            logger.debug("Numeric 003: %s", incom[2:])
        elif incom[1] == '004':
            #debug(sock,"Numeric 004 - server var usermode charmode")
            mysockets[sock]['connectaddress'] = incom[3]
            mysockets[sock]['sversion'] = incom[4]
            mysockets[sock]['connectumodes'] = incom[5]
            mysockets[sock]['connectcmodes'] = incom[6]
            modeprocessor_user(sock,'umode',incom[5])
        elif incom[1] == '005':
            #debug(sock,"Numeric 005 - map")
            i = 0
            while i < len(incom):
                tmpdata = incom[i].split('=')
                #if (tmpdata[0] == 'UHNAMES'):
                if tmpdata[0] == 'MAXCHANNELS':
                    mysockets[sock]['maxchannels'] = int(tmpdata[1])
                elif tmpdata[0] == 'CHANLIMIT':
                    mysockets[sock]['chanlimit'] = tmpdata[1]
                elif tmpdata[0] == 'MAXLIST':
                    mysockets[sock]['maxlist'] = tmpdata[1]
                elif tmpdata[0] == 'NICKLEN':
                    mysockets[sock]['nicklen'] = int(tmpdata[1])
                elif tmpdata[0] == 'CHANNELLEN':
                    mysockets[sock]['channellen'] = int(tmpdata[1])
                elif tmpdata[0] == 'TOPICLEN':
                    mysockets[sock]['topiclen'] = int(tmpdata[1])
                elif tmpdata[0] == 'KICKLEN':
                    mysockets[sock]['kicklen'] = int(tmpdata[1])
                elif tmpdata[0] == 'AWAYLEN':
                    mysockets[sock]['awaylen'] = int(tmpdata[1])
                elif tmpdata[0] == 'MAXTARGETS':
                    mysockets[sock]['maxtargets'] = int(tmpdata[1])
                elif tmpdata[0] == 'MODES':
                    mysockets[sock]['modespl'] = int(tmpdata[1])
                elif tmpdata[0] == 'CHANTYPES':
                    mysockets[sock]['chantypes'] = tmpdata[1]
                elif tmpdata[0] == 'PREFIX':
                    mysockets[sock]['prefix'] = tmpdata[1]
                elif tmpdata[0] == 'CHANMODES':
                    mysockets[sock]['chanmodes'] = tmpdata[1]
                elif tmpdata[0] == 'EXTBAN':
                    mysockets[sock]['extban'] = tmpdata[1]
                i = i + 1

        elif incom[1] == '007':
            debug(sock,"Numeric 007 - end of map")
        elif incom[1] == '008':
            #debug(sock,"Numeric 008 - num - server notice mask")
            if incom[2] == mysockets[sock]['nick']:
                modeprocessor_user(sock,'smask',incom[6])

        elif incom[1] == '010':
            #debug(sock,"Numeric 010 - JumpServer")
            mysockets[sock]['connection']['address'] = incom[3]
            mysockets[sock]['connection']['serverport'] = int(incom[4])

        elif incom[1] == '211':
            debug(sock,"Numeric 211 - connection sendq sentmsg sentbyte recdmsg recdbyte :open")
        elif incom[1] == '212':
            debug(sock,"Numeric 212 - command uses bytes")
        elif incom[1] == '213':
            debug(sock,"Numeric 213 - C address * server port class")
        elif incom[1] == '214':
            debug(sock,"Numeric 214 - N address * server port class")
        elif incom[1] == '215':
            debug(sock,"Numeric 215 - I ipmask * hostmask port class")
        elif incom[1] == '216':
            debug(sock,"Numeric 216 - k address * username details")
        elif incom[1] == '217':
            debug(sock,"Numeric 217 - P port ?? ??")
        elif incom[1] == '218':
            debug(sock,"Numeric 218 - Y class ping freq maxconnect sendq")
        elif incom[1] == '219':
            logger.debug("Numeric 219: %s", incom[2:])

        elif incom[1] == '221':
            if incom[2] == mysockets[sock]['nick']:
                modeprocessor_user(sock,'umode',incom[3])
        elif incom[1] == '222':
            debug(sock,"Numeric 222 - mask :comment")
        elif incom[1] == '223':
            debug(sock,"Numeric 223 - E hostmask * username ?? ??")
        elif incom[1] == '224':
            debug(sock,"Numeric 224 - D ipmask * username ?? ??")

        elif incom[1] == '241':
            debug(sock,"Numeric 241 - L address * server ?? ??")
        elif incom[1] == '242':
            debug(sock,"Numeric 242 - :Server Up num days, time")
        elif incom[1] == '243':
            if incom[6] == mysockets[sock]['server']['botoper']:
                modeprocessor_user(sock,'oflags','+'+incom[7])
        elif incom[1] == '244':
            debug(sock,"Numeric 244 - H address * server ?? ??")

        elif incom[1] == '247':
            debug(sock,"Numeric 247 - G address timestamp :reason")
        elif incom[1] == '248':
            debug(sock,"Numeric 248 - U host * ?? ?? ??")
        elif incom[1] == '249':
            debug(sock,"Numeric 249 - :info")
        elif incom[1] == '250':
            logger.debug("Numeric 250: %s", incom[2:])
        elif incom[1] == '251':
            logger.debug("Numeric 251: %s", incom[2:])
        elif incom[1] == '252':
            logger.debug("Numeric 252: %s", incom[2:])
        elif incom[1] == '253':
            logger.debug("Numeric 253: %s", incom[2:])
        elif incom[1] == '254':
            logger.debug("Numeric 254: %s", incom[2:])
        elif incom[1] == '255':
            logger.debug("Numeric 255: %s", incom[2:])
        elif incom[1] == '256':
            debug(sock,"Numeric 256 - :Administrative info about server")
        elif incom[1] == '257':
            debug(sock,"Numeric 257 - :info")
        elif incom[1] == '258':
            debug(sock,"Numeric 258 - :info")
        elif incom[1] == '259':
            debug(sock,"Numeric 259 - :info")

        elif incom[1] == '263':
            debug(sock,"Numeric 263 - :Server load is temporarily too heavy. Please wait a while and try again.")

        elif incom[1] == '265':
            logger.debug("Numeric 265: %s", incom[2:])
        elif incom[1] == '266':
            logger.debug("Numeric 266: %s", incom[2:])

        elif incom[1] == '271':
            debug(sock,"Numeric 271 - nick mask")
        elif incom[1] == '272':
            debug(sock,"Numeric 272 - nick :End of Silence List")

        elif incom[1] == '280':
            debug(sock,"Numeric 280 - address timestamp reason")
        elif incom[1] == '281':
            debug(sock,"Numeric 281 - :End of G-line List")

        elif incom[1] == '290':
            debug(sock,"Numeric 290 - :num ***** topic *****")
        elif incom[1] == '291':
            debug(sock,"Numeric 291 - :text")
        elif incom[1] == '292':
            debug(sock,"Numeric 292 - : ***** Go to #dalnethelp if you have any further questions *****")
        elif incom[1] == '293':
            debug(sock,"Numeric 293 - :text")
        elif incom[1] == '294':
            debug(sock,"Numeric 294 - :Your help-request has been forwarded to Help Operators")

        elif incom[1] == '298':
            debug(sock,"Numeric 298 - nick :Nickname conflict has been resolved")

        elif incom[1] == '301':
            debug(sock,"Numeric 301 - nick :away")
        elif incom[1] == '302':
            debug(sock,"Numeric 302 - :userhosts")
        elif incom[1] == '303':
            debug(sock,"Numeric 303 - :nicknames")
        elif incom[1] == '304':
            debug(sock,"Numeric 304 - Unknown Raw Code")
        elif incom[1] == '305':
            debug(sock,"Numeric 305 - :You are no longer marked as being away")
        elif incom[1] == '306':
            debug(sock,"Numeric 306 - :You have been marked as being away")
        elif incom[1] == '307':
            debug(sock,"Numeric 307 - :userips")

        elif incom[1] == '310':
            debug(sock,"Numeric 310 - nick :looks very helpful")
        elif incom[1] == '311':
            debug(sock,"Numeric 311 - nick username address * :info")
        elif incom[1] == '312':
            debug(sock,"Numeric 312 - nick server :info")
        elif incom[1] == '313':
            debug(sock,"Numeric 313 - nick :is an IRC Operator")
        elif incom[1] == '314':
            debug(sock,"Numeric 314 - nick username address * :info")
        elif incom[1] == '315':
            debug(sock,"Numeric 315 - request :End of /WHO list.")

        elif incom[1] == '317':
            debug(sock,"Numeric 317 - nick seconds signon :info")
        elif incom[1] == '318':
            debug(sock,"Numeric 318 - request :End of /WHOIS list.")
        elif incom[1] == '319':
            debug(sock,"Numeric 319 - nick :channels")

        elif incom[1] == '321':
            debug(sock,"Numeric 321 - Channel :Users Name")
        elif incom[1] == '322':
            debug(sock,"Numeric 322 - channel users :topic")
        elif incom[1] == '323':
            debug(sock,"Numeric 323 - :End of /LIST")
        elif incom[1] == '324':
            modeprocessor_chan(sock,rtnlower(incom[3]),incom[4:])
            if chanmodes(sock,rtnlower(incom[3])) != 'NULL':
                sts(sock,f"MODE {incom[3]} {chanmodes(sock,rtnlower(incom[3]))}")

        elif incom[1] == '328':
            debug(sock,"Numeric 328 - channel :url")
        elif incom[1] == '329':
            logger.debug("Numeric 329: %s", incom[2:])
            #debug(sock,"Numeric 329 - Channel Creation time")
            #-1-> :chewy.chewynet.co.uk 329 ^chewy_god^ #home 1280495592
            #DEBUG: ChewyNet ['chewy.chewynet.co.uk', '329', '^chewy_god^', '#home', '1280495592']

        elif incom[1] == '331':
            debug(sock,"Numeric 331 - No topic is set")
        elif incom[1] == '332':
            debug(sock,"Numeric 332 - Topic")
        elif incom[1] == '333':
            debug(sock,"Numeric 333 - Nickname time")

        elif incom[1] == '340':
            debug(sock,"Numeric 340 - nick :nickname=+user@IP.address")
        elif incom[1] == '341':
            debug(sock,"Numeric 341 - nick channel")

        elif incom[1] == '346':
            #DEBUG: ChewyNet ['chewy.chewynet.co.uk', '346', '^chewy_god^', '#home', 'doe!*@*', 'chewyb_13', '1280533501']
            #debug(sock,"Numeric 346 - Channel Invex list
            try:
                mysockets[sock]['channels'][rtnlower(incom[3])]['INVEX']
            except KeyError:
                mysockets[sock]['channels'][rtnlower(incom[3])]['INVEX']:dict = {}
            mysockets[sock]['channels'][rtnlower(incom[3])]['INVEX'][incom[4]] = 'TRUE'
        elif incom[1] == '347':
            logger.debug("Numeric 347: %s", incom[2:])
            #debug(sock,"Numeric 347 - End of Channel Invite List")
        elif incom[1] == '348':
            #DEBUG: ChewyNet ['chewy.chewynet.co.uk', '348', '^chewy_god^', '#home', 'blond!*@*', 'chewyb_13', '1280533501']
            #debug(sock,"Numeric 348 - Channel Exception list
            try:
                mysockets[sock]['channels'][rtnlower(incom[3])]['EXCEPT']
            except KeyError:
                mysockets[sock]['channels'][rtnlower(incom[3])]['EXCEPT']:dict = {}
            mysockets[sock]['channels'][rtnlower(incom[3])]['EXCEPT'][incom[4]] = 'TRUE'
        elif incom[1] == '349':
            logger.debug("Numeric 349: %s", incom[2:])
            #debug(sock,"Numeric 349 - End of Channel Exception List")

        elif incom[1] == '351':
            debug(sock,"Numeric 351 - version.debug server :info")
        elif incom[1] == '352':
            debug(sock,"Numeric 352 - channel username address server nick flags :hops info")
        elif incom[1] == '353':
            #debug(sock,"Numeric 353 - Names")
            try:
                mysockets[sock]['channels'][rtnlower(incom[4])]
            except KeyError:
                mysockets[sock]['channels'][rtnlower(incom[4])]:dict = {}
            tmpdata = incom[5:]
            #debug(sock,tmpdata)
            i = 0
            while i < len(tmpdata):
                if tmpdata[i] == '':
                    break
                try:
                    mysockets[sock]['channels'][rtnlower(incom[4])]['users']
                except KeyError:
                    mysockets[sock]['channels'][rtnlower(incom[4])]['users']:dict = {}
                if tmpdata[i][0] == '~':
                    tmpuser = tmpdata[i][1:]
                    tmpmode = 'FOP'
                elif tmpdata[i][0] == '&':
                    tmpuser = tmpdata[i][1:]
                    tmpmode = 'SOP'
                elif tmpdata[i][0] == '@':
                    tmpuser = tmpdata[i][1:]
                    tmpmode = 'OP'
                elif tmpdata[i][0] == '%':
                    tmpuser = tmpdata[i][1:]
                    tmpmode = 'HOP'
                elif tmpdata[i][0] == '+':
                    tmpuser = tmpdata[i][1:]
                    tmpmode = 'VOICE'
                else:
                    tmpuser = tmpdata[i]
                    tmpmode = 'REGULAR'
                try:
                    mysockets[sock]['channels'][rtnlower(incom[4])]['users'][tmpuser]
                except KeyError:
                    mysockets[sock]['channels'][rtnlower(incom[4])]['users'][tmpuser]:dict = {}
                mysockets[sock]['channels'][rtnlower(incom[4])]['users'][tmpuser]['inchan'] = 'TRUE'
                mysockets[sock]['channels'][rtnlower(incom[4])]['users'][tmpuser][tmpmode] = 'TRUE'
                i = i + 1

        elif incom[1] == '364':
            debug(sock,"Numeric 364 - server hub :hops info")
        elif incom[1] == '365':
            debug(sock,"Numeric 365 - mask :End of /LINKS list.")
        elif incom[1] == '366':
            logger.debug("Numeric 366 - End of Names: %s", incom[2:])
        elif incom[1] == '367':
            #DEBUG: ChewyNet ['chewy.chewynet.co.uk', '367', '^chewy_god^', '#home', 'blarg!*@*', 'chewyb_13', '1280533501']
            #debug(sock,"Numeric 367 - Channel Ban list
            try:
                mysockets[sock]['channels'][rtnlower(incom[3])]['BAN']
            except KeyError:
                mysockets[sock]['channels'][rtnlower(incom[3])]['BAN']:dict = {}
            mysockets[sock]['channels'][rtnlower(incom[3])]['BAN'][incom[4]] = 'TRUE'
        elif incom[1] == '368':
            logger.debug("Numeric 368 - End of Channel Ban List: %s", incom[2:])
        elif incom[1] == '369':
            debug(sock,"Numeric 369 - request :End of WHOWAS")

        elif incom[1] == '371':
            debug(sock,"Numeric 371 - :info")
        elif incom[1] == '372':
            logger.debug("Numeric 372 - MOTD info: %s", incom[2:])

        elif incom[1] == '374':
            debug(sock,"Numeric 374 - :End of /INFO list.")
        elif incom[1] == '375':
            logger.debug("Numeric 375 - server motd: %s", incom[2:])
        elif incom[1] == '376':
            logger.debug("Numeric 376 - end of motd: %s", incom[2:])
        elif incom[1] == '377':
            debug(sock,"Numeric 377 - info")
        elif incom[1] == '378':
            debug(sock,"Numeric 378 - info")

        elif incom[1] == '381':
            if mysockets[sock]['isoper'] == 'ATTEMPTING':
                mysockets[sock]['isoper'] = 'TRUE'
                sts(sock,"STATS O")
        elif incom[1] == '382':
            debug(sock,"Numeric 382 - file :Rehashing")

        elif incom[1] == '391':
            debug(sock,"Numeric 391 - server :time")

        elif incom[1] == '401':
            debug(sock,"Numeric 401 - No such nick")
        elif incom[1] == '402':
            debug(sock,"Numeric 402 - server :No such server")
        elif incom[1] == '403':
            debug(sock,"Numeric 403 - No such channel")
        elif incom[1] == '404':
            debug(sock,"Numeric 404 - channel :Cannot send to channel")
        elif incom[1] == '405':
            debug(sock,"Numeric 405 - channel :You have joined too many channels")
        elif incom[1] == '406':
            debug(sock,"Numeric 406 - nickname :There was no such nickname")
        elif incom[1] == '407':
            debug(sock,"Numeric 407 - target :Duplicate recipients. No message delivered")
        elif incom[1] == '408':
            debug(sock,"Numeric 408 - nickname #channel :You cannot use colors on this channel. Not sent: text")
        elif incom[1] == '409':
            debug(sock,"Numeric 409 - :No origin specified")

        elif incom[1] == '411':
            debug(sock,"Numeric 411 - :No recipient given (command)")
        elif incom[1] == '412':
            debug(sock,"Numeric 412 - :No text to send")
        elif incom[1] == '413':
            debug(sock,"Numeric 413 - mask :No toplevel domain specified")
        elif incom[1] == '414':
            debug(sock,"Numeric 414 - mask :Wildcard in toplevel Domain")

        elif incom[1] == '416':
            debug(sock,"Numeric 416 - command :Too many lines in the output, restrict your query")

        elif incom[1] == '421':
            debug(sock,"Numeric 421 - command :Unknown command")
        elif incom[1] == '422':
            logger.debug(sock,"Numeric 422 - MOTD missing: %s", incom[2:])
        elif incom[1] == '423':
            debug(sock,"Numeric 423 - server :No administrative info available")

        elif incom[1] == '431':
            debug(sock,"Numeric 431 - :No nickname given")
        elif incom[1] == '432':
            debug(sock,"Numeric 432 - nickname :Erroneus Nickname")
        elif incom[1] == '433':
            if incom[3] == mysockets[sock]['nick']:
                if mysockets[sock]['nick'] == mysockets[sock]['server']['nick']:
                    sts(sock,f"NICK {mysockets[sock]['server']['bnick']}")
                    mysockets[sock]['nick'] = mysockets[sock]['server']['bnick']
                if mysockets[sock]['nick'] == mysockets[sock]['server']['bnick']:
                    sts(sock,f"NICK {mysockets[sock]['server']['nick']}")
                    mysockets[sock]['nick'] = mysockets[sock]['server']['nick']

        elif incom[1] == '436':
            debug(sock,"Numeric 436 - nickname :Nickname collision KILL")
        elif incom[1] == '437':
            debug(sock,"Numeric 437 - channel :Cannot change nickname while banned on channel")
        elif incom[1] == '438':
            debug(sock,"Numeric 438 - nick :Nick change too fast. Please wait sec seconds.")
        elif incom[1] == '439':
            debug(sock,"Numeric 439 - target :Target change too fast. Please wait sec seconds.")

        elif incom[1] == '441':
            debug(sock,"Numeric 441 - nickname channel :They aren't on that channel")
        elif incom[1] == '442':
            debug(sock,"Numeric 442 - You are not on that channel")
        elif incom[1] == '443':
            debug(sock,"Numeric 443 - nickname channel :is already on channel")

        elif incom[1] == '445':
            debug(sock,"Numeric 445 - :SUMMON has been disabled")
        elif incom[1] == '446':
            debug(sock,"Numeric 446 - :USERS has been disabled")

        elif incom[1] == '451':
            debug(sock,"Numeric 451 - command :Register first.")

        elif incom[1] == '455':
            debug(sock,"Numeric 455 - :Your username ident contained the invalid character(s) chars and has been changed to new. Please use only the characters 0-9 a-z A-Z _ - or . in your username. Your username is the part before the @ in your email address.")

        elif incom[1] == '461':
            debug(sock,"Numeric 461 - command :Not enough parameters")
        elif incom[1] == '462':
            debug(sock,"Numeric 462 - :You may not reregister")

        elif incom[1] == '467':
            debug(sock,"Numeric 467 - channel :Channel key already set")
        elif incom[1] == '468':
            debug(sock,"Numeric 468 - channel :Only servers can change that mode")

        elif incom[1] == '471':
            #debug(sock,"Numeric 471 - channel :Cannot join channel (+l)")
            if mysockets[sock]['identified'] == 'TRUE':
                sts(sock,f"PRIVMSG ChanServ :INVITE {incom[3]}")
                joinchan(sock,rtnlower(incom[3]))
            elif mysockets[sock]['isoper'] == 'TRUE':
                sts(sock,f"SAJOIN {mysockets[sock]['nick']} {incom[3]}")
            else:
                logger.debug("Numeric 471 - channel Limit Failure: %s", incom[2:])
        elif incom[1] == '472':
            debug(sock,"Numeric 472 - char :is unknown mode char to me")
        elif incom[1] == '473':
            #debug(sock,"Numeric 474 - channel :Cannot join channel (+i)")
            if mysockets[sock]['identified'] == 'TRUE':
                sts(sock,f"PRIVMSG ChanServ :INVITE {incom[3]}")
                joinchan(sock,rtnlower(incom[3]))
        elif incom[1] == '474':
            #debug(sock,"Numeric 474 - channel :Cannot join channel (+b)")
            if mysockets[sock]['identified'] == 'TRUE':
                sts(sock,f"PRIVMSG ChanServ :UNBAN {incom[3]}")
                joinchan(sock,rtnlower(incom[3]))
            elif mysockets[sock]['isoper'] == 'TRUE':
                sts(sock,f"SAJOIN {mysockets[sock]['nick']} {incom[3]}")
            else:
                logger.debug("Numeric 471 - channel Ban Failure: %s", incom[2:])
        elif incom[1] == '475':
            #debug(sock,"Numeric 475 - channel :Cannot join channel (+k)")
            if mysockets[sock]['identified'] == 'TRUE':
                sts(sock,f"PRIVMSG ChanServ :INVITE {incom[3]}")
                joinchan(sock,rtnlower(incom[3]))
            elif mysockets[sock]['isoper'] == 'TRUE':
                sts(sock,f"SAJOIN {mysockets[sock]['nick']} {incom[3]}")
            else:
                logger.debug("Numeric 471 - channel Password Failure: %s", incom[2:])

        elif incom[1] == '477':
            debug(sock,"Numeric 477 - channel :You need a registered nick to join that channel.")
        elif incom[1] == '478':
            debug(sock,"Numeric 478 - channel ban :Channel ban/ignore list is full")

        elif incom[1] == '481':
            debug(sock,"Numeric 481 - :Permission Denied- You're not an IRC operator")
        elif incom[1] == '482':
            debug(sock,"Numeric 482 - channel :You're not channel operator")
        elif incom[1] == '483':
            debug(sock,"Numeric 483 - :You cant kill a server!")
        elif incom[1] == '484':
            debug(sock,"Numeric 484 - nick channel :Cannot kill, kick or deop channel service")
        elif incom[1] == '485':
            debug(sock,"Numeric 485 - channel :Cannot join channel (reason)")

        elif incom[1] == '491':
            debug(sock,"Numeric 491 - :No O-lines for your host")

        elif incom[1] == '499':
            logger.debug("Numeric 499 - Not owner of the channel: %s", incom[2:])

        elif incom[1] == '501':
            debug(sock,"Numeric 501 - :Unknown MODE flag")
        elif incom[1] == '502':
            debug(sock,"Numeric 502 - :Cant change mode for other users")

        elif incom[1] == '510':
            debug(sock,"Numeric 510 - :You must resolve the nickname conflict before you can proceed")
        elif incom[1] == '511':
            debug(sock,"Numeric 511 - mask :Your silence list is full")
        elif incom[1] == '512':
            debug(sock,"Numeric 512 - address :No such gline")
        elif incom[1] == '513':
            debug(sock,"Numeric 513 - If you can't connect, type /QUOTE PONG code or /PONG code")

        elif incom[1] == '600':
            debug(sock,"Numeric 600 - nick userid host time :logged offline")
        elif incom[1] == '601':
            debug(sock,"Numeric 601 - nick userid host time :logged online")
        elif incom[1] == '602':
            debug(sock,"Numeric 602 - nick userid host time :stopped watching")
        elif incom[1] == '603':
            debug(sock,"Numeric 603 - :You have mine and are on other WATCH entries")
        elif incom[1] == '604':
            debug(sock,"Numeric 604 - nick userid host time :is online")
        elif incom[1] == '605':
            debug(sock,"Numeric 605 - nick userid host time :is offline")
        elif incom[1] == '606':
            debug(sock,"Numeric 606 - :nicklist")

        elif incom[1] == '972':
            logger.debug("Numeric 972 - Can't kick user due to +q: %s", incom[2:])

        #start normal
        elif incom[1].upper() == 'JOIN':
            try:
                mysockets[sock]['channels'][rtnlower(incom[2])]
            except KeyError:
                mysockets[sock]['channels'][rtnlower(incom[2])]:dict = {}
            try:
                mysockets[sock]['channels'][rtnlower(incom[2])]['users']
            except KeyError:
                mysockets[sock]['channels'][rtnlower(incom[2])]['users']:dict = {}
            try:
                mysockets[sock]['channels'][rtnlower(incom[2])]['users'][sender]
            except KeyError:
                mysockets[sock]['channels'][rtnlower(incom[2])]['users'][sender]:dict = {}
            mysockets[sock]['channels'][rtnlower(incom[2])]['users'][sender]['inchan'] = 'TRUE'
            if sender == mysockets[sock]['nick']:
                if checkchan(sock,rtnlower(incom[2])) == 'FALSE':
                    sts(sock,f"PART {incom[2]} :Not supposed to be in here")
                else:
                    sts(sock,f"MODE {incom[2]}")
                    sts(sock,f"MODE {incom[2]} +b")
                    sts(sock,f"MODE {incom[2]} +e")
                    sts(sock,f"MODE {incom[2]} +I")
            else:
                #debug(sock,"{0} joined channel {1}".format(sender,incom[2]))
                if islogged(sock,sender) == 'TRUE':
                    if len(tempdata[sock]) > 0:
                        if tempdata[sock][sender] == 'UHCHANGE':
                            loggedin[sock][sender]['umask'] = incom[0]
                        del tempdata[sock][sender]
        elif incom[1].upper() == 'PART':
            del mysockets[sock]['channels'][rtnlower(incom[2])]['users'][sender]['inchan']
            if sender == mysockets[sock]['nick']:
                if checkchan(sock,rtnlower(incom[2])) == 'TRUE':
                    joinchan(sock,rtnlower(incom[2]))
                else:
                    del mysockets[sock]['channels'][rtnlower(incom[2])]
                #debug(sock,"I parted channel {0}".format(incom[2]))
            else:
                #debug(sock,"{0} parted channel {1}".format(sender,incom[2]))
                if islogged(sock,sender) == 'TRUE':
                    if len(incom) >= 8:
                        if (incom[3] == 'Rejoining') and (incom[4] == 'because') and (incom[5] == 'of') and (incom[6] == 'user@host') and (incom[7] == 'change'):
                            tempdata[sock][sender] = 'UHCHANGE'
        elif incom[1].upper() == 'QUIT':
            if sender == mysockets[sock]['nick']:
                debug(sock,"I quit")
            else:
                #Still gotta make the netsplit detection coding for here *.*.*.* iswm $1 $2
                if islogged(sock,sender) == 'TRUE':
                    botlog(sock,sender,'COMMON',f"Auto-Logout for {sender}({loggedin[sock][sender]['username']})")
                    del loggedin[sock][sender]
            if len(mysockets[sock]['channels']) > 0:
                tmpckeys = mysockets[sock]['channels'].keys()
                for tmpckey in tmpckeys:
                    if len(mysockets[sock]['channels'][tmpckey]['users']) > 0:
                        tmpuukeys = mysockets[sock]['channels'][tmpckey]['users'].keys()
                        for tmpuukey in tmpuukeys:
                            if tmpuukey == sender:
                                del mysockets[sock]['channels'][tmpckey]['users'][sender]
        elif incom[1].upper() == 'KICK':
            if incom[3] == mysockets[sock]['nick']:
                if checkchan(sock,rtnlower(incom[2])) == 'TRUE':
                    joinchan(sock,rtnlower(incom[2]))
            else:
                debug(sock,"Another user KICKed")
            del mysockets[sock]['channels'][rtnlower(incom[2])]['users'][incom[3]]
        elif incom[1].upper() == 'NICK':
            if sender == mysockets[sock]['nick']:
                debug(sock,"My nick changed --- AHHHHHHH")
            else:
                if islogged(sock,sender) == 'TRUE':
                    tmpmask = incom[0].split('!')
                    output = incom[2]+"!"
                    output = output+tmpmask[1]
                    loggedin[sock][incom[2]] = {'username': loggedin[sock][sender]['username'], 'msgtype': loggedin[sock][sender]['msgtype'], 'umask': output}
                    del loggedin[sock][sender]
            tmpmodes = ['FOP', 'SOP', 'OP', 'HOP', 'VOICE', 'inchan']
            if len(mysockets[sock]['channels']) > 0:
                tmpckeys = mysockets[sock]['channels'].keys()
                for tmpckey in tmpckeys:
                    if len(mysockets[sock]['channels'][tmpckey]['users']) > 0:
                        tmpuukeys = mysockets[sock]['channels'][tmpckey]['users'].keys()
                        for tmpuukey in tmpuukeys:
                            if tmpuukey == sender:
                                if len(mysockets[sock]['channels'][tmpckey]['users'][sender]) > 0:
                                    tmpukeys = mysockets[sock]['channels'][tmpckey]['users'][sender].keys()
                                    try:
                                        mysockets[sock]['channels'][tmpckey]['users'][incom[2]]
                                    except KeyError:
                                        mysockets[sock]['channels'][tmpckey]['users'][incom[2]]:dict = {}
                                    for tmpukey in tmpukeys:
                                        for tmpmode in tmpmodes:
                                            if tmpukey == tmpmode:
                                                mysockets[sock]['channels'][tmpckey]['users'][incom[2]][tmpmode] = mysockets[sock]['channels'][tmpckey]['users'][sender][tmpmode]
                                del mysockets[sock]['channels'][tmpckey]['users'][sender]
        elif incom[1].upper() == 'MODE':
            if incom[2] == mysockets[sock]['nick']:
                modeprocessor_user(sock,'umode',incom[3])
            else:
                modeprocessor_chan(sock,rtnlower(incom[2]),incom[3:])
                if chanmodes(sock,rtnlower(incom[2])) != 'NULL':
                    sts(sock,f"MODE {incom[2]} {chanmodes(sock,rtnlower(incom[2]))}")
        elif incom[1].upper() == 'TOPIC':
            debug(sock,"TOPIC")
        elif incom[1].upper() == 'WALLOPS':
            debug(sock,"WALLOPS")
        elif incom[1].upper() == 'INVITE':
            debug(sock,"INVITE")
        elif incom[1].upper() == 'NOTICE':
            if incom[2] == mysockets[sock]['nick']:
                mycommands(sock,'PNOTE',sender,incom,raw)
            else:
                mycommands(sock,'CNOTE',sender,incom,raw)
        elif incom[1].upper() == 'PRIVMSG':
            if incom[2] == mysockets[sock]['nick']:
                mycommands(sock,'PMSG',sender,incom,raw)
            else:
                mycommands(sock,'CMSG',sender,incom,raw)
        else:
            debug(sock,incom)
            debug(sock,"Unknown feature at this momment")
    else:
        debug(sock,f"Unknown Lenght {incom}")

def massmodes(sock,myuser,chan,modes):
    # pylint: disable=unused-variable
    """
    Mass Modes
    """
    modespl = mysockets[sock]['modespl']
    tmpusers = deque()
    if len(mysockets[sock]['channels'][chan]['users']) > 0:
        tmplogged = 'FALSE'
        tmpkeys = mysockets[sock]['channels'][chan]['users'].keys()
        for tmpkey in tmpkeys:
            if modes[2] == 'ALL':
                tmpusers.append(tmpkey)
            elif modes[2] == 'BC':
                if modes[0] == 'ADD':
                    tmpusers.append(tmpkey)
                else:
                    if tmpkey == myuser:
                        tmplogged = 'TRUE'
                    elif tmpkey == mysockets[sock]['nick']:
                        tmplogged = 'TRUE'
                    else:
                        tmpusers.append(tmpkey)
            else:
                for tmpmode in modes[2]:
                    if tmpkey == tmpmode:
                        tmpusers.append(tmpkey)

    i = 0
    outputmode = ''
    while i != modespl:
        outputmode = outputmode+modes[1]
        i = i + 1
    outputmode = outputmode.rstrip()
    if modes[0] == 'ADD':
        omode = '+'
    else:
        omode = '-'
    i = linnum = 0
    output = ''
    length = len(tmpusers)
    while i != length:
        output = output+tmpusers.popleft()+" "
        linnum = linnum + 1
        if linnum == modespl:
            output = output.rstrip()
            sts(sock,f"MODE {chan} {omode}{outputmode} {output}")
            output = ''
            linnum = 0
        i = i + 1
    output = output.rstrip()
    sts(sock,f"MODE {chan} {omode}{outputmode} {output}")

def modeprocessor_chan(sock,chan,data):
    """
    Mode processor for channels
    """
    try:
        mysockets[sock]['channels'][chan]['modes']
    except KeyError:
        mysockets[sock]['channels'][chan]['modes']:dict = {}
    i = 0
    pos = 1
    mode = 'SUB'
    while i < len(data[0]):
        if (data[0][i] == '+') or (data[0][i] == '-') or (data[0][i] == '(') or (data[0][i] == ')'):
            if data[0][i] == '+':
                mode = 'ADD'
            else:
                mode = 'SUB'
        else:
            if data[0][i] == 'q':
                tmpmode = 'FOP'
            elif data[0][i] == 'a':
                tmpmode = 'SOP'
            elif data[0][i] == 'o':
                tmpmode = 'OP'
            elif data[0][i] == 'h':
                tmpmode = 'HOP'
            elif data[0][i] == 'v':
                tmpmode = 'VOICE'
            elif data[0][i] == 'e':
                tmpmode = 'EXCEPT'
            elif data[0][i] == 'I':
                tmpmode = 'INVEX'
            elif data[0][i] == 'b':
                tmpmode = 'BAN'
            elif data[0][i] == 'l':
                tmpmode = 'LIMIT'
            elif data[0][i] == 'k':
                tmpmode = 'CHANPASS'
            elif data[0][i] == 'f':
                tmpmode = 'FLOOD'
            elif data[0][i] == 'j':
                tmpmode = 'JOIN'
            elif data[0][i] == 'L':
                tmpmode = 'LINK'
            elif data[0][i] == 'B':
                tmpmode = 'BANLINK'
            else:
                tmpmode = data[0][i]
            if mode == 'ADD':
                if tmpmode in ('FOP', 'SOP', 'OP', 'HOP', 'VOICE', 'EXCEPT', 'INVEX', 'BAN', 'LIMIT', 'LINK', 'BANLINK', 'CHANPASS', 'FLOOD', 'JOIN'):
                    if tmpmode in ('FOP', 'SOP', 'OP', 'HOP', 'VOICE'):
                        try:
                            mysockets[sock]['channels'][chan]['users'][data[pos]]
                        except KeyError:
                            mysockets[sock]['channels'][chan]['users'][data[pos]]:dict = {}
                        mysockets[sock]['channels'][chan]['users'][data[pos]][tmpmode] = 'TRUE'
                    else:
                        try:
                            mysockets[sock]['channels'][chan][tmpmode]
                        except KeyError:
                            mysockets[sock]['channels'][chan][tmpmode]:dict = {}
                        if tmpmode in ('BAN', 'EXCEPT', 'INVEX'):
                            mysockets[sock]['channels'][chan][tmpmode][data[pos]] = 'TRUE'
                        else:
                            mysockets[sock]['channels'][chan][tmpmode] = data[pos]
                    pos = pos + 1
                else:
                    try:
                        mysockets[sock]['channels'][chan]['modes']
                    except KeyError:
                        mysockets[sock]['channels'][chan]['modes']:dict = {}
                    mysockets[sock]['channels'][chan]['modes'][tmpmode] = 'TRUE'
            if mode == 'SUB':
                if tmpmode in ('FOP', 'SOP', 'OP', 'HOP', 'VOICE', 'EXCEPT', 'INVEX', 'BAN', 'LIMIT', 'LINK', 'BANLINK', 'CHANPASS', 'FLOOD', 'JOIN'):
                    if tmpmode in ('FOP', 'SOP', 'OP', 'HOP', 'VOICE'):
                        try:
                            mysockets[sock]['channels'][chan]['users'][data[pos]]
                        except KeyError:
                            mysockets[sock]['channels'][chan]['users'][data[pos]]:dict = {}
                        mysockets[sock]['channels'][chan]['users'][data[pos]][tmpmode] = 'FALSE'
                    else:
                        try:
                            mysockets[sock]['channels'][chan][tmpmode]
                        except KeyError:
                            mysockets[sock]['channels'][chan][tmpmode]:dict = {}
                        if tmpmode in ('BAN', 'EXCEPT', 'INVEX'):
                            del mysockets[sock]['channels'][chan][tmpmode][data[pos]]
                        else:
                            del mysockets[sock]['channels'][chan][tmpmode]
                    pos = pos + 1
                else:
                    try:
                        mysockets[sock]['channels'][chan]['modes']
                    except KeyError:
                        mysockets[sock]['channels'][chan]['modes']:dict = {}
                    mysockets[sock]['channels'][chan]['modes'][tmpmode] = 'FALSE'
        i = i + 1

def modeprocessor_user(sock,imsgtype,data):
    """
    Mode processor for the User
    """
    i = 0
    mode = 'SUB'
    while i < len(data):
        #debug(sock,incom[3][i])
        if (data[i] == '+') or (data[i] == '-') or (data[i] == '(') or (data[i] == ')'):
            if data[i] == '+':
                mode = 'ADD'
            else:
                mode = 'SUB'
        else:
            if mode == 'ADD':
                try:
                    mysockets[sock][imsgtype]
                except KeyError:
                    mysockets[sock][imsgtype]:dict = {}
                mysockets[sock][imsgtype][data[i]] = 'TRUE'
            if mode == 'SUB':
                try:
                    mysockets[sock][imsgtype]
                except KeyError:
                    mysockets[sock][imsgtype]:dict = {}
                mysockets[sock][imsgtype][data[i]] = 'FALSE'
        i = i + 1

def pwmaker(data):
    """
    Password hasher
    """
    tmppass = hashlib.md5()
    tmppass.update(data.encode())
    return tmppass

def pulluser(myuser):
    """
    Pull user from the database
    """
    sql = f"SELECT * FROM users WHERE username = '{myuser}'"
    records = db.select(sql)
    if len(records) == 0:
        return 'FALSE'
    for record in records:
        #debug("NULL","{0} , {1} , {2} , {3} , {4} , {5} , {6}".format(record[0],record[1],record[2],record[3],record[4],record[5],record[6]))
        udata = {'id': int(record[0]),'username': record[1],'password': record[2],'global': record[3],'server': record[4],'channel': record[5],'msgtype': record[6]}
    return udata

def getwhois(sock,myuser,chan,mode,otheruser):
    """
    Gets the whois information for a user
    """
    if otheruser == 'NULL':
        if islogged(sock,myuser) == 'TRUE':
            userdata = pulluser(loggedin[sock][myuser]['username'])
        else:
            userdata = pulluser(myuser)
        tmpuinfo = myuser
    else:
        if islogged(sock,otheruser) == 'TRUE':
            userdata = pulluser(loggedin[sock][otheruser]['username'])
        else:
            userdata = pulluser(otheruser)
        tmpuinfo = otheruser
    if userdata == 'FALSE':
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
    if mode == 'WHOIS':
        buildmsg(sock,'NORMAL',myuser,chan,'PRIV',f"Your Bot Whois on {tmpuinfo}")
        buildmsg(sock,'NORMAL',myuser,chan,'PRIV',f"Nick(Username): {tmpuinfo} ({tmpusername})")
        buildmsg(sock,'NORMAL',myuser,chan,'PRIV',f"Global: {wordaccess(tmpglobaccess)} Server: {wordaccess(tmpservaccess)} Channel: {wordaccess(tmpchanaccess)}")
        buildmsg(sock,'NORMAL',myuser,chan,'PRIV',f"End of Your Bot Whois on {tmpuinfo}")
    if mode == 'WHOAMI':
        buildmsg(sock,'NORMAL',myuser,chan,'PRIV',"Your Bot Whois")
        buildmsg(sock,'NORMAL',myuser,chan,'PRIV',f"Nick(Username): {tmpuinfo} ({tmpusername})")
        buildmsg(sock,'NORMAL',myuser,chan,'PRIV',f"Your Global Access: {wordaccess(tmpglobaccess)}")
        buildmsg(sock,'NORMAL',myuser,chan,'PRIV',f"Your Server Access: {wordaccess(tmpservaccess)}")
        buildmsg(sock,'NORMAL',myuser,chan,'PRIV',f"Your Channel Access: {wordaccess(tmpchanaccess)}")
        buildmsg(sock,'NORMAL',myuser,chan,'PRIV',f"Your Current MsgType: {tmpmsgtype}")
        buildmsg(sock,'NORMAL',myuser,chan,'PRIV',"End of Your Bot Whois")

def islogged(sock,myuser):
    """
    Checks if a user is logged in
    """
    tmplogged = 'FALSE'
    if len(loggedin[sock]) > 0:
        tmpkeys = loggedin[sock].keys()
        for tmpkey in tmpkeys:
            if tmpkey == myuser:
                tmplogged = 'TRUE'
            else:
                if tmplogged != 'TRUE':
                    tmplogged = 'FALSE'
    return tmplogged

def getglobaccess(data):
    """
    Gets global access for the user
    """
    #Global Straight access numbers
    if data['global'] != 'NULL':
        tmpglobaccess = data['global']
    else:
        tmpglobaccess = 0
    return int(tmpglobaccess)

def getservaccess(sock,data):
    """
    Gets server access for the User
    """
    #Server ServerName~Access%ServerName~Access
    if data['server'] != 'NULL':
        tmpdata = data['server']
        tmpdata = tmpdata.split(chr(37))
        for tmpdata2 in tmpdata:
            tmpdata2 = tmpdata2.split(chr(126))
            if tmpdata2[0] == mysockets[sock]['server']['servername']:
                tmpservaccess = tmpdata2[1]
    else:
        tmpservaccess = 0
    return int(tmpservaccess)

def getchanaccess(sock,chan,data):
    """
    Gets channel access for the User
    """
    #Channel ServerName|ChannelName~Access|ChannelName~Access%ServerName|ChannelName~Access|ChannelName~Access
    if data['channel'] != 'NULL':
        tmpdata = data['channel']
        tmpdata = tmpdata.split(chr(37))
        for tmpdata2 in tmpdata:
            tmpdata2 = tmpdata2.split(chr(124))
            if tmpdata2[0] == mysockets[sock]['server']['servername']:
                tmpdata3 = tmpdata2[1:]
                for tmpdata4 in tmpdata3:
                    tmpdata4 = tmpdata4.split(chr(126))
                    if tmpdata4[0] == chan:
                        tmpchanaccess = tmpdata4[1]
    else:
        tmpchanaccess = 0
    return int(tmpchanaccess)

def getaccess(sock,myuser,chan,datatype):
    """
    Get the access for the User
    """
    userdata = pulluser(myuser)
    if userdata == 'FALSE':
        return 0
    tmpglobaccess = getglobaccess(userdata)
    tmpservaccess = getservaccess(sock,userdata)
    tmpchanaccess = getchanaccess(sock,chan,userdata)
    if datatype == 'GLOBAL':
        tmpaccess = tmpglobaccess
    if datatype == 'SERVER':
        tmpaccess = tmpglobaccess
        tmpaccess = max(tmpaccess,tmpservaccess)
    if datatype == 'CHANNEL':
        tmpaccess = tmpglobaccess
        tmpaccess = max(tmpaccess,tmpservaccess)
        tmpaccess = max(tmpaccess,tmpchanaccess)
    return int(tmpaccess)

def loggedgetaccess(sock,myuser,chan,datatype):
    """
    Get the access of a logged in User
    """
    if islogged(sock,myuser) == 'TRUE':
        return getaccess(sock,loggedin[sock][myuser]['username'],chan,datatype)
    return 0

def botlog(sock,myuser: str,chan: str,text: str):
    """
    Bot logging to the screen
    """
    logger.info("BOTLOG: %s %s %s %s",mysockets[sock]['server']['servername'],myuser,chan,text)
    #print ("BOTLOG: {0} {1} {2} {3}".format(mysockets[sock]['server']['servername'],myuser,chan,text))

def debug(sock,text: str):
    """
    Debug output to the screen
    """
    if sock == 'NULL':
        logger.debug(text)
        #print ("DEBUG: {0}".format(text))
    else:
        logger.debug("%s %s",mysockets[sock]['server']['servername'],text)
        #print ("DEBUG: {0} {1}".format(mysockets[sock]['server']['servername'],text))

def screenoutput(sock,mode: str,text: str):
    """
    Prettifing the output to the screen
    """
    if mode == 'in':
        print (f"-{sock}-> {text}")
    if mode == 'out':
        print (f"<-{sock}- {text}")

def splitjoiner(data):
    """
    Join split data
    """
    outcounti = 0
    output = ''
    while outcounti != len(data):
        output = output+data[outcounti]+" "
        outcounti = outcounti + 1
    output = output.rstrip()
    return output

def buildmsg(sock,datatype,myuser,chan: str,uctype: str,message: str):
    """
    Build the outgoing message for the bot
    """
    #sock = server($1) imsgtype = messagetype($4) uctype = priv/chan($2) user/chan = sendto($3) message = message($5-)
    if uctype == 'PRIV':
        sendto = myuser
        if islogged(sock,myuser) == 'TRUE':
            userdata = pulluser(loggedin[sock][myuser]['username'])
            msgtype = userdata['msgtype']
        else: msgtype = "msg"
    else:
        sendto = chan
        msgtype = "msg"
    if msgtype == "msg":
        msgoutput = "PRIVMSG"
    if msgtype == "notice":
        msgoutput = "NOTICE"
    if datatype == 'RAW':
        mtoutput = "-(RAW)-"
    elif datatype == 'BLOG':
        mtoutput = "-(CBOT)-(LOG)-"
    elif datatype == 'ELOG':
        mtoutput = "-(CBOT)-(ERROR-LOG)-"
    elif datatype == 'RELAY':
        mtoutput = "*"
    elif datatype == 'NORMAL':
        mtoutput = "-(CBOT)-"
    elif datatype == 'HELP':
        mtoutput = "-(CBOT)-(HELP)-"
    elif datatype == 'ERROR':
        mtoutput = "-(CBOT)-(ERROR)-"
        if message == 'LOGIN':
            message = "You are already Logged in."
        elif message == 'PASSPROB':
            message = "There was a problem with changing your password"
        elif message == 'LOGGED':
            message = "You are Logged in."
        elif message == 'NOTLOGGED':
            message = "You are not Logged in."
        elif message == 'NOACCESS':
            message = "You either have no access to this command or you are not Logged in."
        elif message == 'NOACCESSHELP':
            message = "You do not have access to read help on this command."
    else:
        mtoutput = "-(CBOT)-"
    sts(sock,f"{msgoutput} {sendto} :{chr(3)}4,1{mtoutput}{chr(3)} {message}")

def sts(sock,data):
    """
    Send data to the socket
    """
    #mysocket[sock].send("{0}\n\r".format(data))
    #screenoutput(sock,'out',data)
    queue[sock].append(f"{data}\n\r")

def run_timer(sock):
    """
    Run Local to Socket timer
    """
    lasttimer[sock] = time.time()

def run_globtimer():
    """
    Global timer
    """
    globtimer['lastcheck'] = time.time()

def run_queue(sock):
    """
    The Message queue
    """
    now = time.time()
    i = 0
    queuelimit = int(settings['msgqueue'])
    msginterval = int(settings['msginterval'])
    if (lastqueue[sock] + msginterval) < now:
        #debug(sock,now)
        #debug(sock,lastqueue[sock])
        while i != queuelimit:
            #debug(sock,"Queue Loop {0} and Queue Lenght is {1}, Queue Loop Max should be {2}".format(i,len(queue[sock]),queuelimit))
            if len(queue[sock]) != 0:
                data = queue[sock].popleft()
                #debug(sock,data)
                mysocket[sock].send(data.encode())
                screenoutput(sock,'out',data.strip('\n\r'))
                i = i + 1
            else:
                i = queuelimit
            lastqueue[sock] = time.time()

def rtnlower(item):
    """
    Returns to lowercase
    """
    return item.lower()

def checkchan(sock,chan: str):
    """
    Check channels
    """
    channels = mysockets[sock]['chans'].keys()
    for channel in channels:
        if channel == chan:
            if mysockets[sock]['chans'][channel]['enabled'] == 'enabled':
                return 'TRUE'
            return 'FALSE'
    return 'FALSE'

def chanmodes(sock,chan: str):
    # pylint: disable=unused-variable
    """
    Channel modes
    """
    channels = mysockets[sock]['chans'].keys()
    foutput = ''
    for channel in channels:
        if channel == chan:
            if mysockets[sock]['chans'][chan]['chanmodes'] != 'NULL':
                tmpmodes = mysockets[sock]['channels'][chan]['modes'].keys()
                tmpimodes = mysockets[sock]['chans'][chan]['chanmodes']
                mydata = mysockets[sock]['channels'][chan]['users'][mysockets[sock]['nick']]
                isop = 'FALSE'
                try:
                    if mydata['FOP'] == 'TRUE':
                        isop = 'TRUE'
                except KeyError:
                    isop = 'FALSE'
                try:
                    if mydata['SOP'] == 'TRUE':
                        isop = 'TRUE'
                except KeyError:
                    isop = 'FALSE'
                try:
                    if mydata['OP'] == 'TRUE':
                        isop = 'TRUE'
                except KeyError:
                    isop = 'FALSE'
                try:
                    if mysockets[sock]['isoper'] == 'TRUE':
                        isop = 'TRUE'
                except KeyError:
                    isop = 'FALSE'
                if isop == 'TRUE':
                    data = tmpimodes.split(' ')
                    i = 0
                    pos = 1
                    output = ''
                    output2 = ''
                    mode = 'SUB'
                    while i < len(data[0]):
                        if (data[0][i] == '+') or (data[0][i] == '-') or (data[0][i] == '(') or (data[0][i] == ')'):
                            if data[0][i] == '+':
                                mode = 'ADD'
                            else:
                                mode = 'SUB'
                            if (data[0][i] == '+') or (data[0][i] == '-'):
                                output = output+data[0][i]
                        else:
                            if data[0][i] == 'l':
                                tmpmode = 'LIMIT'
                            elif data[0][i] == 'k':
                                tmpmode = 'CHANPASS'
                            elif data[0][i] == 'f':
                                tmpmode = 'FLOOD'
                            elif data[0][i] == 'j':
                                tmpmode = 'JOIN'
                            elif data[0][i] == 'L':
                                tmpmode = 'LINK'
                            elif data[0][i] == 'B':
                                tmpmode = 'BANLINK'
                            else:
                                tmpmode = data[0][i]
                            if mode == 'ADD':
                                if tmpmode in ('LIMIT', 'LINK', 'BANLINK', 'CHANPASS', 'FLOOD', 'JOIN'):
                                    output = output+data[0][i]
                                    output2 = output2+data[pos]+' '
                                    pos = pos + 1
                                else:
                                    output = output+tmpmode
                            if mode == 'SUB':
                                if tmpmode in ('LIMIT', 'LINK', 'BANLINK', 'CHANPASS', 'FLOOD', 'JOIN'):
                                    output = output+data[0][i]
                                    output2 = output2+data[pos]+' '
                                    pos = pos + 1
                                else:
                                    output = output+tmpmode
                        i = i + 1
                    output = output.strip(' ')
                    if len(output) >= 2:
                        output2 = output2.rstrip()
                        foutput = output+' '+output2
                        foutput = foutput.rstrip()
                        return foutput
                    return 'NULL'
                return 'NULL'
            return 'NULL'
    return 'NULL'

def joinchan(sock,chan: str):
    """
    Join channels
    """
    channels = mysockets[sock]['chans'].keys()
    for channel in channels:
        if channel == chan:
            if mysockets[sock]['chans'][channel]['chanpass'] == 'NULL':
                sts(sock,f"JOIN :{channel}")
            else:
                sts(sock,f"JOIN :{channel} {mysockets[sock]['chans'][channel]['chanpass']}")

def autojoinchannels(sock):
    """
    Auto Join channels
    """
    channels = mysockets[sock]['chans'].keys()
    for channel in channels:
        if checkchan(sock,channel) == 'TRUE':
            joinchan(sock,channel)

def operupcheck(sock):
    """
    Oper check for the bot
    """
    if mysockets[sock]['server']['botoper'] != 'NULL':
        sts(sock,f"OPER {mysockets[sock]['server']['botoper']} {mysockets[sock]['server']['botoperpass']}")
        mysockets[sock]['isoper'] = 'ATTEMPTING'

def wordaccess(access: int):
    """
    Process the number access value and change it to a word
    """
    if access == 7:
        waccess = "Creator(7)"
    elif access == 6:
        waccess = "Master(6)"
    elif access == 5:
        waccess = "Owner(5)"
    elif access == 4:
        waccess = "Protected(4)"
    elif access == 3:
        waccess = "OP(3)"
    elif access == 2:
        waccess = "Half-Op(2)"
    elif access == 1:
        waccess = "Voice(1)"
    else:
        waccess = "No Access(0)"
    return waccess

def rehash():
    """
    Rehash the bot, thus reloading data from the database
    """
    sql = "SELECT * FROM settings"
    records = db.select(sql)
    for record in records:
        #debug("NULL","{0} = {1} ".format(record[1],record[2]))
        settings[record[1]] = record[2]

    sql = "SELECT * FROM servers"
    records = db.select(sql)
    sockcount = 1
    for record in records:
        try:
            mysockets[sockcount]
        except KeyError:
            mysockets[sockcount]:dict = {}
        try:
            mysockets[sockcount]['server']
        except KeyError:
            mysockets[sockcount]['server']:dict = {}
        try:
            mysockets[sockcount]['connection']
        except KeyError:
            mysockets[sockcount]['connection']:dict = {}
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
        try:
            mysockets[int(record[1])]['chans']
        except KeyError:
            mysockets[int(record[1])]['chans']:dict = {}
        try:
            mysockets[int(record[1])]['chans'][record[2]]
        except KeyError:
            mysockets[int(record[1])]['chans'][record[2]]:dict = {}
        mysockets[int(record[1])]['chans'][record[2]]['chanpass'] = record[3]
        mysockets[int(record[1])]['chans'][record[2]]['chanmodes'] = record[4]
        mysockets[int(record[1])]['chans'][record[2]]['chantopic'] = record[5]
        mysockets[int(record[1])]['chans'][record[2]]['options'] = record[6]
        mysockets[int(record[1])]['chans'][record[2]]['enabled'] = record[7]

    tempsocks = mysockets.keys()
    for tempsock in tempsocks:
        if mysockets[tempsock]['server']['enabled'] != 'enabled':
            del mysockets[tempsock]

def loaddata():
    """
    Load data from the database
    """
    sql = "SELECT * FROM settings"
    records = db.select(sql)
    for record in records:
        #debug("NULL","{0} = {1} ".format(record[1],record[2]))
        settings[record[1]] = record[2]

    sql = "SELECT * FROM servers"
    records = db.select(sql)
    sockcount = 1
    for record in records:
        try:
            mysockets[sockcount]
        except KeyError:
            mysockets[sockcount]:dict = {}
        try:
            mysockets[sockcount]['server']
        except KeyError:
            mysockets[sockcount]['server']:dict = {}
        try:
            mysockets[sockcount]['connection']
        except KeyError:
            mysockets[sockcount]['connection']:dict = {}
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
        try:
            mysockets[int(record[1])]['chans']
        except KeyError:
            mysockets[int(record[1])]['chans']:dict = {}
        try:
            mysockets[int(record[1])]['chans'][record[2]]
        except KeyError:
            mysockets[int(record[1])]['chans'][record[2]]:dict = {}
        mysockets[int(record[1])]['chans'][record[2]]['chanpass'] = record[3]
        mysockets[int(record[1])]['chans'][record[2]]['chanmodes'] = record[4]
        mysockets[int(record[1])]['chans'][record[2]]['chantopic'] = record[5]
        mysockets[int(record[1])]['chans'][record[2]]['options'] = record[6]
        mysockets[int(record[1])]['chans'][record[2]]['enabled'] = record[7]

    tempsocks = len(mysockets.keys())
    tempsock = 1
    while tempsock != tempsocks:
        if mysockets[tempsock]['server']['enabled'] != 'enabled':
            del mysockets[tempsock]
        tempsock = tempsock + 1

def doconnection(sock):
    """
    Create and start connection
    """
    debug(sock,f"Attempting to connect to {mysockets[sock]['server']['servername']}")
    mysockets[sock]['lastcmd'] = ''
    if mysockets[sock]['server']['nickservpass'] != 'NULL':
        mysockets[sock]['identified'] = 'FALSE'
    else:
        mysockets[sock]['identified'] = 'TRUE'
    mysockets[sock]['isoper'] = ''
    mysockets[sock]['lastping'] = time.time()
    mysocket[sock] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        mysocket[sock].connect((mysockets[sock]['connection']['address'], mysockets[sock]['connection']['serverport']))
        mysocket[sock].settimeout(0)
        if mysockets[sock]['server']['serverpass'] != 'NULL':
            sts(sock,f"PASS {mysockets[sock]['server']['serverpass']}")
        sts(sock,f"NICK {mysockets[sock]['nick']}")
        sts(sock,f"USER {settings['botname']} 0 {mysockets[sock]['server']['address']} :Ch3wyB0t Version {__version__}")
    except socket.error:
        #del mysocket[sock]
        #del mysockets[sock]
        debug(sock,f"Connection Attempt Failed for {mysockets[sock]['server']['servername']}")

def main () -> None:
    """
    Main process
    """
    if hasattr(os, 'fork'):
        attemptfork()
    tempsocks = mysockets.keys()
    globtimer['data']:dict = {}
    globtimer['lastcheck'] = time.time() - 10
    for tempsock in tempsocks:
        mysockets[tempsock]['channels']:dict = {}
        queue[tempsock] = deque()
        timer[tempsock]:dict = {}
        lastqueue[tempsock] = time.time() - 10
        lasttimer[tempsock] = time.time() - 10
        loggedin[tempsock]:dict = {}
        tempdata[tempsock]:dict = {}
        mysockets[tempsock]['lastcmd'] = ''
        if mysockets[tempsock]['server']['nickservpass'] != 'NULL':
            mysockets[tempsock]['identified'] = 'FALSE'
        else:
            mysockets[tempsock]['identified'] = 'TRUE'
        mysockets[tempsock]['lastping'] = time.time()
        mysockets[tempsock]['nick'] = mysockets[tempsock]['server']['nick']
        doconnection(tempsock)
        run_queue(tempsock)

    while True:
        if len(globtimer['data']) != 0:
            run_globtimer()
        tempsocks = mysockets.keys()
        sockcount = len(tempsocks)
        if sockcount == 0:
            break
        for tempsock in tempsocks:
            now = time.time()
            if (mysockets[tempsock]['lastping'] + 600) < now:
                mysocket[tempsock].close()
                doconnection(tempsock)
            if len(queue[tempsock]) != 0:
                run_queue(tempsock)
            if len(timer[tempsock]) != 0:
                run_timer(tempsock)
            try:
                data = mysocket[tempsock].recv(10240)
                process = 1
            except socket.timeout:
                #debug(tempsock,socket.timeout)
                process = 0
            except socket.error:
                #debug(tempsock,socket.error)
                process = 0
            if process == 1:
                tmpdata = data.decode().strip('\r')
                tmpdata = tmpdata.split('\n')
                #debug(tempsock,tmpdata)
                while tmpdata:
                    #debug(tempsock,tmpdata[0])
                    if tmpdata[0] != '':
                        parse_data(tempsock,tmpdata[0])
                    del tmpdata[0]
        time.sleep(0.5)

# attemptfork is thanks to phenny irc bot (http://inamidst.com/phenny/)
def attemptfork() -> None:
    # pylint: disable=no-member
    # due to a precheck to see if fork is in os and not writing in linux
    """
    Attempt to fork the process away from the main process
    """
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError:
        logger.debug('Could not daemonize process')
        #debug('NULL','Could not daemonize process: {0} ({1})'.format(e.errno, e.strerror))
    os.setsid()
    os.umask(0)
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError:
        logger.debug('Could not daemonize process')
        #debug('NULL','Could not daemonize process: {0} ({1})'.format(e.errno, e.strerror))

if __name__ == '__main__':
    # This line of code should never really be hit, but it's here just in case
    logger.info("Doing a check for python 3.x and above")
    if sys.version_info[0] < 3:
        # pylint: disable=pointless-string-statement
        """This section should only be accessable if the python version is below the required version """
        logger.debug("Bot failing due to old python version, needs python 3.x")
        logger.critical("Bot failing due to old python version, needs python 3.x")
        raise Exception("Must be using Python 3")
    logger.info("Bot is starting, loading settings, servers, and channels")
    loaddata()
    logger.info("Bot finished loading settings, servers, and channels. Gonna attempt to start the bot up")
    try:
        main()
    except KeyboardInterrupt:
        print ("Bot Exited due to KeyboardInterrupt")
