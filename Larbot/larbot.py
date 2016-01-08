# Socket library
"""
Created on 2015-03-15

@author: Laraeph
"""
import sys
import time
import socket
import threading

from Larbot.self_module.commands_manager import run
from Larbot.self_module.twitch_tags import get_tags

# IRC connection data
HOST = "irc.twitch.tv"  # This is the Twitch IRC ip, don't change it.
PORT = 6667  # Same with this port, leave it be.
s = None  # Creating the socket variable


def connect(nick, oauth, channel, qwindow=None):
    global s
    try:
        s.close()  # closing old socket if it exists
    except:
        pass

    s = socket.socket()

    try:
        s.connect((HOST, PORT))
    except ConnectionAbortedError:
        qwindow.statusbar.showMessage(
            "Connection couldn't even start, "
            "a firewall or temporary Twich ban?")
        print(
            "Connection couldn't even start, "
            "a firewall or temporary Twich ban?")
        return False
    except OSError as e:
        if(e.winerror == 10056):  # Already connected
            qwindow.statusbar.showMessage("Already connected")
            print("Already connected")
            return True
        # Connection aborted, may be due to existing connection
        elif(e.winerror == 10053):
            qwindow.statusbar.showMessage(
                "Connection aborted, maybe due to an existing connection?")
            print("Connection aborted, maybe due to an existing connection?")
            return False

    # Sending password (Twitch oauth) first
    s.send("PASS {0}\r\n".format(oauth).encode())
    # Then the rest of the info
    s.send("NICK {0}\r\n".format(nick.lower()).encode())
    s.send("USER {0} {1} bla :{2}\r\n".format(
        nick, HOST, nick + " Bot").encode())

    print("Done sending the info, waiting for the first answer...")

    readbuffer = s.recv(1024).decode()

    print(readbuffer)

    # Couldn't read anything, connection closed (empty pass?)
    if(readbuffer == "" or
       readbuffer == ":tmi.twitch.tv NOTICE * :Error logging in\r\n"):
        qwindow.statusbar.showMessage(
            "Wrong Login/OAuth combo. Make sure you copied the entire OAuth!")
        print(
            "Wrong Login/OAuth combo. Make sure you copied the entire OAuth!")
        return False

    # Requesting tags
    s.send("CAP REQ :twitch.tv/tags\r\n".encode())

    # Joining the channel.
    s.send("JOIN #{0}\r\n".format(channel.lower().replace("#", "")).encode())
    time.sleep(0.1)

    return True


def main(nick, oauth, channel, qwindow=None):
    global s

    if(not connect(nick, oauth, channel, qwindow)):
        return

    readbuffer = ""  # Empty buffer

    while(True):  # Eternal loop to listen the messages

        try:  # Receiving data from IRC
            readbuffer = readbuffer + s.recv(1024).decode()
        except:  # Error while reading the socket, try reconnecting
            time.sleep(3)
            if(connect(nick, oauth, channel, qwindow)):  # Reconnecting worked
                continue
            else:  # Reconnecting didn't work
                qwindow.statusbar.showMessage(
                    "Automatic reconnection failed, "
                    "please reconnect manually in the connection tab")
                print(
                    "Automatic reconnection failed, "
                    "please reconnect manually in the connection tab")
                break

        print(
            readbuffer.encode(encoding=sys.stdout.encoding,
                              errors='replace').decode())

        # Didn't receive anything, connection may be closed
        if(readbuffer == ""):
            time.sleep(1)  # Waiting a second not to flood with reconnections
            connect(nick, oauth, channel, qwindow)
            continue

        temp = str.split(readbuffer, "\r\n")
        readbuffer = temp.pop()  # The remainder may be an unfinished message

        for line in temp:
            line = str.split(line, " ")

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

            # Checks if it's a channel joined message
            elif (len(line) >= 6 and
                  line[1] == "353"):
                qwindow.statusbar.showMessage(
                    "Connected!")
                print("Connected!")
                continue

            # Checks if it's a login unsuccessful message
            elif (len(line) >= 5 and
                  line[3] == ":Login" and
                  line[4] == "unsuccessful"):
                qwindow.statusbar.showMessage(
                    "Wrong Login/OAuth combo. "
                    "Make sure you copied the entire OAuth!")
                print(
                    "Wrong Login/OAuth combo. "
                    "Make sure you copied the entire OAuth!")
                break

            # IRC checks connection with ping.
            # Every ping has to be replied to with a Pong.
            elif(line[0] == "PING"):
                s.send("PONG {0}\r\n".format(line[1]).encode())


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
