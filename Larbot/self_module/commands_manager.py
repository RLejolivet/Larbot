# -*- coding: utf-8 *-*

"""
Created on 2015-03-15

@author: Laraeph
"""


import threading


from Larbot.self_module.message_queue import send_msg, create_msg
import Larbot.self_module.commands.smash_commands


def run(command, socket, channel, name, args, qwindow=None):
    if(socket is None):
        if(qwindow is not None):
            qwindow.not_connected()
        return

    kwargs = {
        'socket': socket,
        'channel': channel,
        'name': name,
        'args': args,
        'qwindow': qwindow
        }
    if(command in commands.keys()):
        t = threading.Thread(target=commands[command], kwargs=kwargs)
        t.setDaemon(True)
        t.start()


def hello(socket, channel, name, args, qwindow=None):
    if len(args) == 0:
        reply = create_msg(channel, "Hello {:s}!".format(name))
    else:
        reply = create_msg(channel, "Hello {:s}!".format(" ".join(args)))
    send_msg(socket, reply)


def print_commands(socket, channel, name, args, qwindow=None):
    global commands
    ret = create_msg(channel, ", ".join(sorted(list(commands.keys()))))
    send_msg(socket, ret)

commands = dict()
commands["hello"] = hello
commands["commands"] = print_commands
commands["enter"] = Larbot.self_module.commands.smash_commands.enter
commands["open"] = Larbot.self_module.commands.smash_commands.open_list
commands["close"] = Larbot.self_module.commands.smash_commands.close_list
commands["setcap"] = Larbot.self_module.commands.smash_commands.set_cap
commands["next"] = Larbot.self_module.commands.smash_commands.next_player
commands["reset"] = Larbot.self_module.commands.smash_commands.reset_list
commands["line"] = Larbot.self_module.commands.smash_commands.list_entered
commands["eta"] = Larbot.self_module.commands.smash_commands.eta

if __name__ == "__main__":
    commands["hello"](None, "a")