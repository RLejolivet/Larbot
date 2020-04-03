"""
Created on 2015-03-15

@author: Raphael
"""

import time
import threading


nb_of_messages = 0
nb_of_messages_lock = threading.Lock()


def create_msg(channel, message):
    return "PRIVMSG #" + channel + " :" + message + "\r\n"


def send_msg(socket, string_message):
    global nb_of_messages
    global nb_of_messages_lock

    # Checking the number of messages
    nb_of_messages_lock.acquire()
    while(nb_of_messages > 19):
        nb_of_messages_lock.release()
        time.sleep(1)
        nb_of_messages_lock.acquire()

    # Adding one message. Note : after the loop, we still have the lock
    nb_of_messages += 1
    nb_of_messages_lock.release()
    print(string_message.encode())
    socket.send(string_message.encode())
    t = threading.Timer(30, decr_nb_of_messages)
    t.start()


def decr_nb_of_messages():
    global nb_of_messages
    global nb_of_messages_lock

    nb_of_messages_lock.acquire()
    if(nb_of_messages > 0):
        nb_of_messages -= 1
    nb_of_messages_lock.release()
