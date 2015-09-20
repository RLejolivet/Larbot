##Socket library
import socket

##IRC connection data
HOST="199.9.253.199" ##This is the Twitch IRC ip, don't change it.
PORT=6667 ##Same with this port, leave it be.
NICK="KanthBot" ##This has to be your bots username.
PASS="testpass1" ##Instead of a password, use this http://twitchapps.com/tmi/, since Twitch is soon updating to it.
IDENT="KanthBot" ##Bot username again
REALNAME="Kanthes Bot" ##This doesn't really matter.
CHANNEL="#kanthes" ##This is the channel your bot will be working on.

s = socket.socket( ) ##Creating the socket variable
s.connect((HOST, PORT)) ##Connecting to Twitch
s.send("PASS %s\r\n" % PASS) ##Notice how I'm sending the password BEFORE the username!
##Just sending the rest of the data now.
s.send("NICK %s\r\n" % NICK)
s.send("USER %s %s bla :%s\r\n" % (IDENT, HOST, REALNAME))
##Connecting to the channel.
s.send("JOIN %s\r\n" % CHANNEL)

readbuffer = ""
##Eternal loop letting the bot run.
while (1):
	##Receiving data from IRC and spitting it into manageable lines.
	readbuffer=readbuffer+nfSocket.recv(1024)
	temp=string.split(readbuffer, "\n")
	readbuffer=temp.pop( )
	for line in temp:
		##Checks if the first character is a !, for commands.
		if(line[3][0:2]==":!"):
			QUERIED_COMMAND = ENTIRE_MESSAGE.split(" ",1)[0]
			##Checks what command was queried.
			if(QUERIED_COMMAND=="!hello"):
				##Sending a reply to the channel. Notice the : before the actual message, that's mandatory, as well as the \r\n to let it post the new line.
				reply ="PRIVMSG "+CHANNEL+" :Hello world!\r\n"
				##Sending the reply through the socket
				s.send(reply)
		##IRC checks connectiond with ping. Every ping has to be replied to with a Pong.
		elif(line[0]=="PING"):
        	s.send("PONG %s\r\n" % line[1])

##Disclaimer:
##This is a VERY simple bot I've taken straight from my code, I've not tried running it nor can I guarantee it will. But perhaps it will give you some idea of the syntax to use and all that!