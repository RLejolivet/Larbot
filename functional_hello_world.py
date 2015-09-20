## Python3 script for a simple IRC bot on twitch.

##Socket library
import socket

##IRC connection data
HOST="irc.twitch.tv" ##This is the Twitch IRC ip, don't change it.
PORT=6667 ##Same with this port, leave it be.
NICK="Larbot" ##This has to be your bots username.
PASS="oauth:alonglistoflettersandnumbers" ##Instead of a password, use this http://twitchapps.com/tmi/, since Twitch is soon updating to it.
IDENT="Larbot" ##Bot username again
REALNAME="Laraeph Bot" ##This doesn't really matter.
CHANNEL="#laraeph" ##This is the channel your bot will be working on.

s = socket.socket( ) ##Creating the socket variable
s.connect((HOST, PORT)) ##Connecting to Twitch
s.send("PASS {0}\r\n".format(PASS).encode()) ##Notice how I'm sending the password BEFORE the username!
##Just sending the rest of the data now.
s.send("NICK {0}\r\n".format(NICK).encode())
s.send("USER {0} {1} bla :{2}\r\n".format(IDENT, HOST, REALNAME).encode())
##Connecting to the channel.
s.send("JOIN {0}\r\n".format(CHANNEL).encode())

readbuffer = ""
##Eternal loop letting the bot run.
while (1):
    ##Receiving data from IRC and spitting it into manageable lines.
    readbuffer=readbuffer+s.recv(1024).decode()
    temp=str.split(readbuffer, "\r\n")
    readbuffer=temp.pop( )
    for line in temp:
        line = str.split(line, " ")
        ##Checks if the first character is a !, for commands.
        if len(line) >= 4 and (line[3][0:2]==":!"):
            QUERIED_COMMAND = line[3]
            print(QUERIED_COMMAND)
	    ##Checks what command was queried.
            if(QUERIED_COMMAND==":!hello"):
                ##Sending a reply to the channel. Notice the : before the actual message, that's mandatory, as well as the \r\n to let it post the new line.
                reply ="PRIVMSG "+CHANNEL+" :Hello world!\r\n"
                ##Sending the reply through the socket
                s.send(reply.encode())
            ##IRC checks connectiond with ping. Every ping has to be replied to with a Pong.
        elif(line[0]=="PING"):
            s.send("PONG {0}\r\n".format(line[1]).encode())

##Disclaimer:
##This is a VERY simple bot I've taken straight from my code, I've not tried running it nor can I guarantee it will. But perhaps it will give you some idea of the syntax to use and all that!
