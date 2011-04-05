"""
database.py

class to interface with a sqlite database

for python 2.4 or earlier download pysqlite from http://pysqlite.org/

"""

import os

#from pysqlite2 import dbapi2 as sqlite3 # if using python 2.4
import sqlite3  # if using python 2.5 or greater

class Database(object):
    """ class to handle all python communication with a sqlite database file """
    def __init__(self, db_file="data/data.db"):
        database_already_exists = os.path.exists(db_file)    
        self.db = sqlite3.connect(db_file)
        if not database_already_exists:
            self.setupDefaultData()
        
    def select(self,sql):
        """ select records from the database """
        #print sql
        cursor = self.db.cursor()  
        cursor.execute(sql)
        records = cursor.fetchall()
        cursor.close()
        return records   
        
    def insert(self,sql):
        """ insert a new record to database and return the new primary key """
        #print sql       
        newID = 0
        cursor = self.db.cursor()            
        cursor.execute(sql)
        newID = cursor.lastrowid
        self.db.commit()
        cursor.close()
        return newID
        
    def execute(self,sql):
        """ execute any SQL statement but no return value given """
        #print sql 
        cursor = self.db.cursor()  
        cursor.execute(sql)
        self.db.commit()
        cursor.close()

    def executescript(self,sql):
        """ execute any SQL statement but no return value given """
        #print sql 
        cursor = self.db.cursor()  
        cursor.executescript(sql)
        self.db.commit()
        cursor.close()

    def setupDefaultData(self):
		#import hashlib
		#print "Start to do the questions, lol"
		#print "Questions with * can't be 'NULL'"
		#print "If the question doesn't have the *, enter in NULL as anything other than 'NULL' will be the value"
		#install = dict()
		#install = {'botname': 'NULL', 'chancom': 'NULL', 'pvtcom': 'NULL', 'dcccom': 'NULL', 'server': {'name': 'NULL', 'address': 'NULL', 'port': 'NULL', 'nick': 'NULL', 'bnick': 'NULL'}, 'channel': {'server': 'NULL', 'channel': 'NULL', 'chanmodes': '+nt'}, 'user': {'username': 'NULL', 'password': 'NULL'}}
		#while (install['botname'].upper() == 'NULL'):
		#	install['botname'] = raw_input("Enter The Bot's Name *: ").strip()
		#while (install['chancom'].upper() == 'NULL'):
		#	install['chancom'] = raw_input("Enter The Channel Command Trigger *: ").strip()
		#while (install['pvtcom'].upper() == 'NULL'):
		#	install['pvtcom'] = raw_input("Enter The PVT Command Trigger *: ").strip()
		#while (install['dcccom'].upper() == 'NULL'):
		#	install['dcccom'] = raw_input("Enter The Dcc Command Trigger *: ").strip()
		#while (install['server']['name'].upper() == 'NULL'):
		#	install['server']['name'] = raw_input("Enter The Server Network Name *: ").strip()
		#while (install['server']['address'].upper() == 'NULL'):
		#	install['server']['address'] = raw_input("Enter the Server Address *: ").strip()
		#while (install['server']['port'].upper() == 'NULL'):
		#	install['server']['port'] = raw_input("Enter the Server Port *: ").strip()
		#install['server']['pass'] = raw_input("Enter the Server Password: ").strip()
		#if (install['server']['pass'].upper() == 'NULL'):
		#	install['server']['pass'] = 'NULL'
		#while (install['server']['nick'].upper() == 'NULL'):
		#	install['server']['nick'] = raw_input("Enter the Bot's Main Nick for that Server *: ").strip()
		#while (install['server']['bnick'].upper() == 'NULL'):
		#	install['server']['bnick'] = raw_input("Enter the Bot's Backup Nick for that Server *: ").strip()
		#install['server']['nickpass'] = raw_input("Enter the Bot's Identification Password for that server: ").strip()
		#if (install['server']['nickpass'].upper() == 'NULL'):
		#	install['server']['nickpass'] = 'NULL'
		#install['server']['botoper'] = raw_input("Enter the Bot's Oper: ").strip()
		#if (install['server']['botoper'].upper() == 'NULL'):
		#	install['server']['botoper'] = 'NULL'
		#	install['server']['botoperpass'] = 'NULL'
		#if (install['server']['botoper'] != 'NULL'):
		#	install['server']['botoperpass'] = raw_input("Enter the Bot's Oper Pass: ").strip()
		#	if (install['server']['botoperpass'].upper() == 'NULL'):
		#		install['server']['botoper'] = 'NULL'
		#		install['server']['botoperpass'] = 'NULL'
		#install['channel']['server'] = install['server']['name']
		#while (install['channel']['channel'].upper() == 'NULL'):
		#	install['channel']['channel'] = raw_input("Enter the main channel you want to connect to *: ").strip()
		#install['channel']['chanpass'] = raw_input("Enter the channel password: ").strip()
		#if (install['channel']['chanpass'].upper() == 'NULL'):
		#	install['channel']['chanpass'] = 'NULL'
		#install['channel']['chanmodes'] = "+nt"
		#while (install['user']['username'].upper() == 'NULL'):
		#	tempuname = raw_input("Enter your username *: ").strip()
		#	install['user']['username'] = tempuname.lower()
		#while (install['user']['password'].upper() == 'NULL'):
		#	tempupass = raw_input("Enter your password *: ").strip()
		#	tmppass = hashlib.md5()
		#	tmppass.update(tempupass)
		#	install['user']['password'] = tmppass.hexdigest()

		#self.execute("CREATE TABLE IF NOT EXISTS settings (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, setting TEXT, value TEXT)")
		#self.execute("CREATE TABLE IF NOT EXISTS servers (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, servername TEXT, address TEXT, serverport TEXT, serverpass TEXT, nick TEXT, bnick TEXT, nickservpass TEXT, botoper TEXT, botoperpass TEXT, enabled TEXT)")
		#self.execute("CREATE TABLE IF NOT EXISTS channels (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, server TEXT, channel TEXT, chanpass TEXT, chanmodes TEXT, options TEXT, enabled TEXT)")
		#self.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, username TEXT, password TEXT, global TEXT, server TEXT, channel TEXT, msgtype TEXT)")
		#self.execute("CREATE TABLE IF NOT EXISTS errors (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, nickname TEXT, server TEXT, channel TEXT, username TEXT, timedate TEXT, errortype TEXT, extra TEXT)")
		#self.execute("CREATE TABLE IF NOT EXISTS botlog (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, nickname TEXT, server TEXT, channel TEXT, username TEXT, timedate TEXT, command TEXT, extra TEXT)")
		#self.execute("CREATE TABLE IF NOT EXISTS seen (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, nick TEXT, type TEXT, timedate TEXT, extra TEXT)")
		#self.execute("INSERT INTO settings (setting, value) VALUES ({0}, {1})".format('botname',install['botname']))
		#self.execute("INSERT INTO settings (setting, value) VALUES ({0}, {1})".format('chancom',install['chancom']))
		#self.execute("INSERT INTO settings (setting, value) VALUES ({0}, {1})".format('pvtcom',install['pvtcom']))
		#self.execute("INSERT INTO settings (setting, value) VALUES ({0}, {1})".format('dcccom',install['dcccom']))
		#self.execute("INSERT INTO settings (setting, value) VALUES ({0}, {1})".format('kcount','0'))
		#self.execute("INSERT INTO settings (setting, value) VALUES ({0}, {1})".format('bcount','0'))
		#self.execute("INSERT INTO settings (setting, value) VALUES ({0}, {1})".format('msgqueue','3'))
		#self.execute("INSERT INTO settings (setting, value) VALUES ({0}, {1})".format('msginterval','1'))
		#self.execute("INSERT INTO server (servername, address, serverport, serverpass, nick, bnick, nickservpass, botoper, botoperpass, enabled) VALUES ({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9})".format(install['server']['name'],install['server']['address'],install['server']['port'],install['server']['pass'],install['server']['nick'],install['server']['bnick'],install['server']['nickpass'],install['server']['botoper'],install['server']['botoperpass'],'enabled'))
		#self.execute("INSERT INTO channels (server, channel, chanpass, chanmodes, options, enabled) VALUES ({0}, {1}, {2}, {3}, {4}, {5})".format(install['channel']['server'],install['channel']['channel'],install['channel']['chanpass'],install['channel']['chanmodes'],'NULL','enabled'))
		#self.execute("INSERT INTO users (username, password, global, server, channel, msgtype) VALUES ({0}, {1}, {2}, {3}, {4}, {5})".format('chewyb_13','db5ae87de7c6ebd5352191a18207dc47','7','NULL','NULL','msg'))
		#self.execute("INSERT INTO users (username, password, global, server, channel, msgtype) VALUES ({0}, {1}, {2}, {3}, {4}, {5})".format(install['user']['username'],install['user']['password'],'6','NULL','NULL','msg'))

		
		print "Okay something is wrong here, lol"
                            
if __name__ == '__main__':
    db = Database()
    sql = "SELECT id, setting, value FROM Settings"
    records = db.select(sql)
    print records  
    for record in records:
        print "%s = %s " % (record[1],record[2])

    #sql = "UPDATE Settings SET value = '15' WHERE setting = 'slideshow_delay'"
    #sql = "DELETE FROM Settings WHERE id > 2"
    #db.execute(sql)