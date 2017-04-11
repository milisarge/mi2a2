#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, disconnect
import irc.bot
import irc.strings
from irc.client import ip_numstr_to_quad, ip_quad_to_numstr
import profil as PROFIL
from random import randint

# async_mode "threading", "eventlet" ,"gevent" olabilir.None olursa kuruşu paketlerden uygun olan seçilir.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 's324fvre7reB!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None

rumuz="milis_"+str(randint(1000,9999))
kanal="#milisarge"
ircsunucu="irc.freenode.net"
ircport=6667

if PROFIL.rumuz != "":
	rumuz = PROFIL.rumuz

if PROFIL.kanal != "":
	kanal = PROFIL.kanal

if PROFIL.ircsunucu != "":
	ircsunucu = PROFIL.ircsunucu
	
if PROFIL.ircport != "":
	ircport = PROFIL.ircport


class MilisBot(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nickname, server, port=6667):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.channel)

    def on_privmsg(self, c, e):
        print "priv:",c
        print "priv:",e
        self.do_command(e, e.arguments[0])

    def on_pubmsg(self, c, e):
        gonderen = e.source.nick
        print "arg-*",e.arguments
        mesaj = e.arguments
        socketio.emit('kanala_gonder_cevap',{'data': mesaj,'gonderen':gonderen},namespace='/irc')
        a = e.arguments[0].split(":", 1)
        if len(a) > 1 and irc.strings.lower(a[0]) == irc.strings.lower(self.connection.get_nickname()):
            self.do_command(e, a[1].strip())
        return
            
    def gonder(self,mesaj):
        #self.connection.notice(None,mesaj)
        self.connection.privmsg("#milisarge",mesaj)
        
    def kanal_liste(self):
		users=[]
		for chname, chobj in self.channels.items():
			users = sorted(chobj.users())
		return users 
            
    def do_command(self, e, cmd):
        print "kanal_mesaji: ",cmd
        nick = e.source.nick
        c = self.connection

        if cmd == "disconnect":
            self.disconnect()
        elif cmd == "die":
            self.die()
        elif cmd == "stats":
            for chname, chobj in self.channels.items():
                c.notice(nick, "--- Channel statistics ---")
                c.notice(nick, "Channel: " + chname)
                users = sorted(chobj.users())
                c.notice(nick, "Users: " + ", ".join(users))
                opers = sorted(chobj.opers())
                c.notice(nick, "Opers: " + ", ".join(opers))
                voiced = sorted(chobj.voiced())
                c.notice(nick, "Voiced: " + ", ".join(voiced))
        elif cmd == "dcc":
            dcc = self.dcc_listen()
            c.ctcp("DCC", nick, "CHAT chat %s %d" % (
                ip_quad_to_numstr(dcc.localaddress),
                dcc.localport))
        else:
            c.notice(nick, "anlasılmadı: " + cmd)

'''
def arkaplan_islem():
    # belli periyodlarda olay üretmek için
    sayac = 0
    while True:
        socketio.sleep(10)
        count += 1
        socketio.emit('sunucu_cevap',
                      {'data': 'Sunucu olay üretti', 'count': sayac},
                      namespace='/irc')
'''

bot = MilisBot(kanal,rumuz,ircsunucu,ircport)

def ircbot():
    global bot
    bot.start()
                      
@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)

@socketio.on('sunucu_olay', namespace='/irc')
def sunucu_olay(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('sunucu_cevap',{'data': message['data'], 'count': session['receive_count']})

@socketio.on('kanala_gonder', namespace='/irc')
def kanala_gonder(mesaj):
    #session['receive_count'] = session.get('receive_count', 0) + 1
    gonderen="sen"
    mesajveri=mesaj['data']
    global bot
    bot.gonder(mesajveri)
    liste=bot.kanal_liste()
    print liste
    #emit('kanala_gonder_cevap',{'data': message['data'], 'count': session['receive_count']})
    emit('kanala_gonder_cevap',{'data': mesajveri,'gonderen':gonderen})

@socketio.on('baglantikes_istegi', namespace='/irc')
def baglantikes_istegi():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('sunucu_cevap',{'data': 'Bağlantı kesildi!'})
    disconnect()

@socketio.on('ping_olay', namespace='/irc')
def ping_olay():
    emit('pong_olay')

@socketio.on('connect', namespace='/irc')
def connect():
    global thread
    if thread is None:
       #thread = socketio.start_background_task(target=arkaplan_islem)
       thread = socketio.start_background_task(target=ircbot)
    emit('sunucu_cevap', {'data': 'Bağlandın', 'count': 0})

'''
@socketio.on('disconnect', namespace='/irc')
def test_disconnect():
    print('Bağlantı kesildi.', request.sid)
'''

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0",port=7070,debug=True)
