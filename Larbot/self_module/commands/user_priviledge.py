'''
Created on 20 avr. 2015

@author: Raph
'''


import threading


mod_list_lock = threading.Lock()
mod_list = []


def add_mod(name):
    global mod_list_lock
    global mod_list

    mod_list_lock.acquire()
    if(name not in mod_list):
        mod_list.append(name.lower())
    mod_list_lock.release()


def check_mod(name):
    return (name.lower() in mod_list)
