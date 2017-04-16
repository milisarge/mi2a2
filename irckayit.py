#!/usr/bin/env python2
# -*- coding:utf-8 -*-
import socket,sys,time,threading,os,re,datetime
import sqlite3 as vt
import codecs

gitlog =  False
kayitvt = "irckayit.db"
IrcAddr = "irc.freenode.net"
IrcNick = "irc_kayitci"
IrcChan = "#milisarge"
IrcUser = "irc_kayitci"
Irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
QUIT = 0
lock = threading.Lock()
gIPaddr = ""
def IrcConn():
    Irc.connect((IrcAddr,6667))
    sendmsg("NICK "+IrcNick)
    sendmsg("USER "+IrcUser+" "+IrcUser+" "+IrcUser+" :irc_kayitci")
    sendmsg("JOIN "+IrcChan)
    while 1:
        if QUIT == 1:
            Irc.close()
            break
        else:
            buf = Irc.recv(1024)
            buf = buf.strip()
            dizi = buf.split(" ")
            if dizi[0]=="PING":
                servaddr = dizi[1].lstrip(":")
                sendmsg("PONG "+servaddr)
            else:
                t = threading.Thread(target = console(buf))
                t.start()
    print "gule gule"
    sys.exit()
    
def vt_olustur():
	baglanti = vt.connect(kayitvt)
	with baglanti:
		cur = baglanti.cursor()
		cur.execute("DROP TABLE IF EXISTS kayit")
		cur.execute("CREATE TABLE kayit ( id INTEGER PRIMARY KEY NOT NULL,zaman TIMESTAMP DEFAULT CURRENT_TIMESTAMP,gonderen VARCHAR(30) NOT NULL,mesaj TEXT NOT NULL);")

def vt_kaydet(zaman,gonderen,mesaj):
	mesaj=mesaj[1:]
	baglanti = vt.connect(kayitvt)
	with baglanti:
		cur = baglanti.cursor()
		cur.execute("INSERT INTO kayit (zaman,gonderen,mesaj) VALUES(?, ?,?)", [zaman,gonderen,mesaj])

def console(strdizi):
    if len(sys.argv)>1:
        print "%s" %(strdizi) #debug print
    textArray = strdizi.split(" ")
    Msg = ""
    bufNick = textArray[0].split("!")
    Nick = bufNick[0].lstrip(":")
    kanal = textArray[2]
    ircmsg = textArray[3:]
    
    if Nick == IrcNick and textArray[1]=="JOIN":
        ip = textArray[0].split("@")
        global gIPaddr
        gIPaddr = ip[1] # bot ip adresi
    if textArray[1]=="PRIVMSG":
        saat = time.strftime("%H:%M")

        for i in ircmsg:
            Msg += i+" "
        Msg = Msg.strip() 
        Msg = Msg.decode("utf-8")
        logger(saat+"&nbsp; <b>"+Nick+"</b>&nbsp;"+remove_tags(Msg))
        sqlkayit(time.strftime("%d-%m-%y %H:%M"),Nick,remove_tags(Msg))
        if gitlog:
			gitkayit()
        if Nick == "sahip" and Msg == ":!kill":
            global QUIT
            QUIT = 1
    if textArray[1] == "KICK":
            time.sleep(0.5)
            sendmsg("JOIN "+kanal)

def privmsg(mesaj,nick):
    sendmsg("PRIVMSG "+nick+" :"+mesaj)

def sendmsg(msgtext):
    lock.acquire()
    Irc.send(msgtext+"\r\n")
    lock.release()

def logger(logmsg):
    tarih=time.strftime("%d-%m-%y")
    lock.acquire()
    dosya = codecs.open("log/"+tarih+".htm","a","iso-8859_9")
    dosya.write("<b>"+tarih+"</b>&nbsp;"+logmsg+"</br>")
    dosya.close()
    lock.release()

def sqlkayit(zaman,gonderen,mesaj):
	lock.acquire()
	vt_kaydet(zaman,gonderen,mesaj)
	lock.release()

def gitkayit():
	lock.acquire()
	os.system("cd log && ./git-guncelle kayit && cd -")
	lock.release()
	
def gitklon():
	lock.acquire()
	if os.path.exists("log/.git") is False:
		os.system("git clone 127.0.0.1:8003/irclog log")
	lock.release()
	
def remove_tags(text):
    TAG_RE = re.compile(r'<[^>]+>')
    return TAG_RE.sub('', text)    

if __name__ == "__main__":
	#try:
	if os.path.exists(kayitvt) is False:
		vt_olustur()
	IrcConn()
	#except:
	print "hata:", sys.exc_info()[0]
	
