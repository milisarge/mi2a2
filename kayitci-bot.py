#!/usr/bin/env python2
# -*- coding:utf-8 -*-
import socket,sys,time,threading,os,re,datetime

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
    print "bye"
    sys.exit()

def console(strdizi):
    if len(sys.argv)>1:
        print "%s" %(strdizi) #debug print
    textArray = strdizi.split(" ")
    Msg = ""
    bufNick = textArray[0].split("!")
    Nick = bufNick[0].lstrip(":")
    kanal = textArray[2]
    ircmsg = textArray[3:]
    #:frigg!~frigg@freenode/utility-bot/frigg PRIVMSG pycirc :VERSION
    if Nick == IrcNick and textArray[1]=="JOIN":
        ip = textArray[0].split("@")
        global gIPaddr
        gIPaddr = ip[1] # bot ip adresi
    if textArray[1]=="PRIVMSG":
        saat = time.strftime("%H:%M")

        for i in ircmsg:
            Msg += i+" "
        Msg = Msg.strip() 
        logger(saat+"&nbsp; <b>"+Nick+"</b>&nbsp;"+remove_tags(Msg))
        #if Msg == ":VERSION":
        #   # \001VERSION #:#:#\001
        #   privmsg("\001VERSION pyircbot:v01:python2\001",Nick)
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
    dosya = open("milisarge_log/"+tarih+".htm","a")
    dosya.write("<b>"+tarih+"</b>&nbsp;"+logmsg+"</br>")
    dosya.close()
    lock.release()

def remove_tags(text):
    TAG_RE = re.compile(r'<[^>]+>')
    return TAG_RE.sub('', text)    

if __name__ == "__main__":
  try:
   IrcConn()
  except:
   print "Unexpected error:", sys.exc_info()[0]

