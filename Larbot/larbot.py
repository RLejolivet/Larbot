# Socket library
"""
Created on 2015-03-15

@author: Laraeph
"""

import socket
import time
import threading


from PySide.QtGui import QMessageBox

from Larbot.self_module.commands_manager import run
from Larbot.self_module.commands.user_priviledge import add_mod
from Larbot.self_module.twitch_tags import get_tags

# IRC connection data
HOST = "irc.twitch.tv"  # This is the Twitch IRC ip, don't change it.
PORT = 6667  # Same with this port, leave it be.
s = None  # Creating the socket variable


def connect(nick, oauth, channel, qwindow=None):
    global s
    if(s is None):
        s = socket.socket()
    try:
        s.connect((HOST, PORT))  # Connecting to Twitch
    except ConnectionAbortedError:
        if(qwindow is not None):
            QMessageBox.about(
                qwindow,
                "Connection aborted",
                "Connection has been closed, now quitting\n"
            )
            qwindow.close()
        print("\nQuitting...")
        return
    except OSError as e:
        if(e.winerror == 10056):
            if(qwindow is not None):
                qwindow.statusbar.showMessage("Connected")
            return
        if(e.winerror == 10053):
            if(qwindow is not None):
                qwindow.statusbar.showMessage("")
                s = None
                connect(nick, oauth, channel, qwindow)
            return
        else:
            raise

    s.send("PASS {0}\r\n".format(oauth).encode())
    # Just sending the rest of the data now.
    s.send("NICK {0}\r\n".format(nick.lower()).encode())
    s.send("USER {0} {1} bla :{2}\r\n".format(
        nick, HOST, nick + " Bot").encode())
    s.send("CAP REQ :twitch.tv/tags\r\n".encode())
    # Connecting to the channel.
    s.send("JOIN #{0}\r\n".format(channel.lower().replace("#", "")).encode())
    if(qwindow is not None):
        qwindow.statusbar.showMessage("Connected")
    print("Connected\n")


def main(nick, oauth, channel, qwindow=None):
    global s
    connect(nick, oauth, channel, qwindow)
    readbuffer = ""
    try:
        # Eternal loop letting the bot run.
        while (1):
            # Receiving data from IRC and spitting it into manageable lines.
            try:
                readbuffer = readbuffer + s.recv(1024).decode()
            except ConnectionAbortedError:
                print("\nQuitting...")
                return

            # connection closed, attempt to reconnect 5 seconds later
            if readbuffer == '':
                time.sleep(5)
                connect(nick, oauth, channel, qwindow)
                continue
            print(readbuffer)

            temp = str.split(readbuffer, "\r\n")
            readbuffer = temp.pop()
            for line in temp:
                line = str.split(line, " ")

                # For server admin messages:
                if (len(line) >= 5 and
                        line[0] == ":jtv" and
                        line[1] == "MODE" and
                        line[3] == "+o"):
                    add_mod(line[4])

                # For private messages:
                if len(line) >= 5 and line[2] == "PRIVMSG":
                    # Checks if the first character is a !, for commands.
                    if len(line) >= 4 and (line[4][0:2] == ":!"):
                        TAGS = get_tags(line[0])
                        COMMAND = line[4][2:].lower()
                        CHANNEL = line[3][1:].lower()
                        NAME = line[1].split("!")[0][1:].lower()
                        print(TAGS, CHANNEL, NAME, COMMAND, line[5:])

                        # Checks what command was queried.
                        run(COMMAND, s, CHANNEL, NAME,
                            line[5:], qwindow, tags=TAGS)

                    # Checks if it's a login unsuccessful message
                    if (len(line) >= 5 and
                            line[3] == ":Login" and
                            line[4] == "unsuccessful"):
                        time.sleep(1)
                        if(qwindow is not None):
                            qwindow.actionNoLogin.trigger()
                        else:
                            print("Login unsuccessful")
                        s = None
                        return

                # IRC checks connectiond with ping.
                # Every ping has to be replied to with a Pong.
                elif(line[0] == "PING"):
                    s.send("PONG {0}\r\n".format(line[1]).encode())

    except KeyboardInterrupt:
        print("\nQuitting...")


def console_loop(t):
    try:
        while 1:
            time.sleep(1)
            if(not t.is_alive()):
                return
    except KeyboardInterrupt:
        s.close()


def _start(nick, oauth, channel, qwindow=None):
    kwargs = {
        'nick': nick,
        'oauth': oauth,
        'channel': channel,
        'qwindow': qwindow
    }
    t = threading.Thread(target=main, kwargs=kwargs)
    t.setDaemon(qwindow is not None)
    t.start()
    if(qwindow is None):
        console_loop(t)

if (__name__ == "__main__"):
    _start()
