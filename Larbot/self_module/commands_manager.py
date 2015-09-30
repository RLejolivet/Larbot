# -*- coding: utf-8 *-*

"""
Created on 2015-03-15

@author: Laraeph
"""


import threading

from Larbot.self_module.message_queue import send_msg, create_msg
import Larbot.self_module.commands.smash_commands


def run(command, socket, channel, name, args, qwindow, tags={}):
    if(socket is None):
        if(qwindow is not None):
            qwindow.not_connected()
        return

    kwargs = {
        'socket': socket,
        'channel': channel,
        'name': name,
        'args': args,
        'tags': tags
    }

    target = None
    if(command in commands.keys()):
        target = commands[command]
    elif(command in mod_commands.keys()):
        target = mod_commands[command]
    elif(command in hidden_commands.keys()):
        target = hidden_commands[command]

    if(target is not None):
        t = threading.Thread(target=target, kwargs=kwargs)
        t.setDaemon(True)
        t.start()
    else:
        print("Unknown command: {!s}".format(command))


def hello(socket, channel, name, args):
    if len(args) == 0:
        reply = create_msg(channel, "Hello {:s}!".format(name))
    else:
        reply = create_msg(channel, "Hello {:s}!".format(" ".join(args)))
    send_msg(socket, reply)


def print_commands(socket, channel, name, args, qwindow=None, tags={}):
    global commands
    ret = create_msg(channel, "Available commands: " +
                     ", ".join(sorted(list(commands.keys()))))
    send_msg(socket, ret)

commands = dict()
commands["commands"] = print_commands
commands["enter"] = Larbot.self_module.commands.smash_commands.enter
commands["list"] = Larbot.self_module.commands.smash_commands.list_entered
commands["eta"] = Larbot.self_module.commands.smash_commands.eta
commands["drop"] = Larbot.self_module.commands.smash_commands.drop

mod_commands = dict()
mod_commands["open"] = Larbot.self_module.commands.smash_commands.open_list
mod_commands["close"] = Larbot.self_module.commands.smash_commands.close_list
mod_commands["setcap"] = Larbot.self_module.commands.smash_commands.set_cap
mod_commands["next"] = Larbot.self_module.commands.smash_commands.next_player
mod_commands["swap"] = Larbot.self_module.commands.smash_commands.swap
mod_commands["remove"] = Larbot.self_module.commands.smash_commands.remove
mod_commands["move"] = Larbot.self_module.commands.smash_commands.move
mod_commands["add"] = Larbot.self_module.commands.smash_commands.add
mod_commands["subsonly"] = Larbot.self_module.commands.smash_commands.set_subs_only
mod_commands["limit"] = Larbot.self_module.commands.smash_commands.set_limit_reentry

hidden_commands = dict()
hidden_commands["join"] = Larbot.self_module.commands.smash_commands.enter
hidden_commands["reset"] = Larbot.self_module.commands.smash_commands.reset_list
hidden_commands["leave"] = Larbot.self_module.commands.smash_commands.drop
hidden_commands["line"] = Larbot.self_module.commands.smash_commands.list_entered
hidden_commands["spot"] = Larbot.self_module.commands.smash_commands.eta


if __name__ == "__main__":
    commands["hello"](None, "a")
