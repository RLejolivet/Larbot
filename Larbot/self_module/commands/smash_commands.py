# -*- coding: utf-8 *-*

"""
Created on 2015-03-16

@author: Raph
"""

import threading
import json


from Larbot.self_module.message_queue import send_msg, create_msg


player_list = []
player_list_lock = threading.Lock()

player_list_cap = None
player_list_cap_lock = threading.Lock()

player_NNID = {}
player_NNID_lock = threading.Lock()

line_opened = False
line_opened_lock = threading.Lock()

try:
    with open("save_states/players.json", "rb") as infile:
        json_load = json.loads(infile.read().decode())
        try:
            player_list = json_load['player_list']
        except KeyError:
            pass

        try:
            if(json_load['player_list_cap']):
                player_list_cap = int(json_load['player_list_cap'])
        except (KeyError, ValueError):
            pass

        try:
            player_NNID = json_load['player_NNID']
        except KeyError:
            pass
except (FileNotFoundError, ValueError):
    pass


def enter(socket, channel, name, args, qwindow=None):
    global player_list
    global player_list_lock
    global player_list_cap
    global player_list_cap_lock
    global player_NNID
    global player_NNID_lock
    global line_opened
    global line_opened_lock

    player_NNID_lock.acquire()
    if(len(args) < 2 and name not in player_NNID.keys()):
        player_NNID_lock.release()
        ret = create_msg(
            channel,
            "@{:s}: Usage: '!enter <NNID> <Mii name>'".format(name))
        send_msg(socket, ret)
        return
    elif(name not in player_NNID.keys()):
        player_NNID[name] = {'NNID': args[0], 'Mii name': args[1]}
    player_NNID_lock.release()

    line_opened_lock.acquire()
    if(not line_opened):
        line_opened_lock.release()
        ret = create_msg(channel, "@{:s}: Line is not opened".format(name))
        send_msg(socket, ret)
        return
    line_opened_lock.release()

    player_list_cap_lock.acquire()
    player_list_lock.acquire()
    if(player_list_cap is not None and len(player_list) >= player_list_cap):
        player_list_cap_lock.release()
        player_list_lock.release()
        ret = create_msg(channel, "@{:s}: Line is currently full".format(name))
        send_msg(socket, ret)
        return
    player_list_cap_lock.release()
    player_list_lock.release()

    player_list_lock.acquire()
    if(name not in player_list):
        player_list.append(name)
        if(qwindow is not None):
            qwindow.set_list(player_list)
        ret = create_msg(
            channel,
            "@{:s}: Added to the line at #{:d}".format(name, len(player_list)))
        player_list_lock.release()
        send_msg(socket, ret)
    else:
        player_list_lock.release()
        ret = create_msg(channel, "@{:s}: You are already added".format(name))
        send_msg(socket, ret)

    save_to_file()


def open_list(socket, channel, name, args, qwindow=None):
    global player_list
    global player_list_lock
    global player_list_cap
    global player_list_cap_lock
    global player_NNID
    global player_NNID_lock
    global line_opened
    global line_opened_lock

    if(channel != name):
        return

    line_opened_lock.acquire()
    line_opened = True
    line_opened_lock.release()

    ret = create_msg(channel, "@{:s}: Line is now open!".format(name))
    send_msg(socket, ret)


def close_list(socket, channel, name, args, qwindow=None):
    global player_list
    global player_list_lock
    global player_list_cap
    global player_list_cap_lock
    global player_NNID
    global player_NNID_lock
    global line_opened
    global line_opened_lock

    if(channel != name):
        return

    line_opened_lock.acquire()
    line_opened = False
    line_opened_lock.release()

    ret = create_msg(channel, "@{:s}: Line is now closed!".format(name))
    send_msg(socket, ret)


def set_cap(socket, channel, name, args, qwindow=None):
    global player_list
    global player_list_lock
    global player_list_cap
    global player_list_cap_lock
    global player_NNID
    global player_NNID_lock
    global line_opened
    global line_opened_lock

    if(channel != name):
        return

    if(len(args) < 1):
        ret = create_msg(
            channel,
            "@{:s}: Usage: '!setcap <number>', 0 for infinity".format(name))
        send_msg(socket, ret)
        return

    try:
        player_list_cap_lock.acquire()
        new_cap = int(args[0])
        if(new_cap <= 0):
            new_cap = None
        if(new_cap == player_list_cap):
            return
        player_list_cap = None
        player_list_cap = new_cap
    except ValueError:
        ret = create_msg(
            channel,
            "@{:s}: Usage: '!setcap <number>', 0 for infinity".format(name))
        send_msg(socket, ret)
    finally:
        player_list_cap_lock.release()

    ret = create_msg(
        channel,
        "@{:s}: Line cap set to {:s}!".format(name, str(new_cap)))
    send_msg(socket, ret)

    save_to_file()


def next_player(socket, channel, name, args, qwindow=None):
    global player_list
    global player_list_lock
    global player_list_cap
    global player_list_cap_lock
    global player_NNID
    global player_NNID_lock
    global line_opened
    global line_opened_lock

    if(channel != name):
        return

    player_list_lock.acquire()
    if(len(player_list) <= 0):
        player_list_lock.release()
        ret = create_msg(
            channel,
            "@{:s}: Line is empty!".format(name))
        send_msg(socket, ret)
        return
    player_name = player_list.pop(0)
    if(qwindow is not None):
        qwindow.set_list(player_list)
    player_list_lock.release()

    player_NNID_lock.acquire()
    nnid = player_NNID[player_name]['NNID']
    mii_name = player_NNID[player_name]['Mii name']
    player_NNID_lock.release()

    ret = create_msg(
        channel,
        "@{:s}: Next player: {:s}, NNID: {:s}, Mii name: {:s}".format(
            channel, player_name, nnid, mii_name))
    send_msg(socket, ret)

    if(qwindow is not None):
        qwindow.player_name_line_edit.setText(player_name)
        qwindow.player_NNID_line_edit.setText(nnid)
        qwindow.mii_name_line_edit.setText(mii_name)

    save_to_file()


def reset_list(socket, channel, name, args, qwindow=None):
    global player_list
    global player_list_lock
    global player_list_cap
    global player_list_cap_lock
    global player_NNID
    global player_NNID_lock
    global line_opened
    global line_opened_lock

    if(channel != name):
        return

    player_list_lock.acquire()
    player_list = []
    if(qwindow is not None):
        qwindow.set_list(player_list)
    player_list_lock.release()

    ret = create_msg(
        channel,
        "@{:s}: Line reset!".format(name))
    send_msg(socket, ret)

    save_to_file()


def list_entered(socket, channel, name, args, qwindow=None):
    global player_list
    global player_list_lock
    global player_list_cap
    global player_list_cap_lock
    global player_NNID
    global player_NNID_lock
    global line_opened
    global line_opened_lock

    current_list = []
    player_list_lock.acquire()
    for player_name in player_list:
        current_list.append(player_name)
    player_list_lock.release()
    ret = create_msg(
        channel,
        "Current line: {:s}".format(", ".join(current_list)))
    send_msg(socket, ret)


def eta(socket, channel, name, args, qwindow=None):
    global player_list
    global player_list_lock
    global player_list_cap
    global player_list_cap_lock
    global player_NNID
    global player_NNID_lock
    global line_opened
    global line_opened_lock

    player_list_lock.acquire()
    if(name not in player_list):
        player_list_lock.release()
        ret = create_msg(
            channel,
            "@{:s}: You are not in the line!".format(name))
        send_msg(socket, ret)
        return
    eta_index = player_list.index(name)
    player_list_lock.release()
    ret = create_msg(
        channel,
        "@{:s}: You are on position #{:d}".format(name, eta_index + 1))
    send_msg(socket, ret)


def save_to_file():
    global player_list
    global player_list_lock
    global player_list_cap
    global player_list_cap_lock
    global player_NNID
    global player_NNID_lock
    global line_opened
    global line_opened_lock

    player_list_cap_lock.acquire()
    player_list_lock.acquire()
    player_NNID_lock.acquire()

    save_dict = {
        'player_list': player_list,
        'player_list_cap': player_list_cap,
        'player_NNID': player_NNID
        }

    try:
        with open("save_states/players.json", "wb") as outfile:
            outfile.write(json.dumps(save_dict, indent=4).encode())
    finally:
        player_list_cap_lock.release()
        player_list_lock.release()
        player_NNID_lock.release()