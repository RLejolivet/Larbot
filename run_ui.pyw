# -*- coding: utf-8 *-*

"""
Created on 2015-03-17

@author: Raph
"""

import os
import sys
import platform
import json
import struct

import PySide
from PySide import QtCore
from PySide.QtGui import QApplication, QMainWindow, QTextEdit,\
    QPushButton,  QMessageBox


import Larbot.larbot
from Larbot.self_module.commands_manager import run
from Larbot.self_module.commands.smash_commands import load as load_ui
from Larbot.ui.ui_mainwindow import Ui_MainWindow
from Larbot.self_module.commands.user_priviledge import add_mod


class MainWindow(QMainWindow, Ui_MainWindow):

    login_unsuccessful = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.tabWidget.setCurrentIndex(0)
        self.actionAbout.triggered.connect(self.about)
        self.connect_button.clicked.connect(self.connect)
        self.statusbar.showMessage("Not Connected")
        self.bot_oauth_help_button.clicked.connect(self.oauth_help)
        self.next_button.clicked.connect(self.next)
        self.open_line_checkbox.toggled.connect(self.open_line)
        self.subscriber_checkbox.toggled.connect(self.subs_only)
        self.reset_line_button.clicked.connect(self.reset)
        self.entrants_cap_spinbox.editingFinished.connect(self.setcap)
        self.actionNoLogin.triggered.connect(self.login_failure_slot)
        self.remove_button.clicked.connect(self.remove_player)
        self.swap_button.clicked.connect(self.swap_players)

    def about(self):
        '''Popup a box with about message.'''
        QMessageBox.about(
            self,
            "Simple IRC bot for Twitch created by Laraeph",
            "Simple IRC bot for Twitch created by Laraeph\n"
            "Manage viewer battles for Smash Wii U easily!\n"
            "Howto use : http://mentor2.dyndns.org/Laraeph/Larbot\n"
            "\n"
            "Contact me for questions, evolution requests:\n"
            "twitch.tv/laraeph\n"
            "twitter.com/LaraephFR\n"
            "laraephddo@gmail.com\n")

    def not_connected(self):
        QMessageBox.about(
            self,
            "Bot isn't connected",
            "Could not send message because the bot isn't connected.\n"
            "Please head to the IRC Info tab and connect\n")

    def connect(self):
        self.statusbar.showMessage("Connecting...")
        bot_name = self.bot_name_line_edit.text()
        oauth = self.bot_oauth_line_edit.text()
        channel = self.channel_line_edit.text()

        add_mod(channel)

        save_dict = {
            'nick': bot_name,
            'oauth': oauth,
            'channel': channel
        }

        with open("save_states/config.json.bin", "wb") as outfile:
            outfile.write(json.dumps(save_dict, indent=4).encode())

        Larbot.larbot._start(bot_name, oauth, channel, self)

    def oauth_help(self):
        QMessageBox.about(
            self,
            "OAuth help",
            "This is the OAuth of your bot account, to connect to Twitch\n"
            "To obtain it:\n"
            "    - Log on the bot account on Twitch\n"
            "    - Go to http://twitchapps.com/tmi/\n"
            "    - Connect with Twitch\n"
            "    - Accept\n"
            "    - Copy and paste the OAuth given in the box\n"
        )

    def next(self):
        channel = self.channel_line_edit.text().lower()
        run('next', Larbot.larbot.s, channel, channel, [], self)

    def open_line(self, switch):
        channel = self.channel_line_edit.text().lower()
        type(self.open_line_checkbox.checkState())
        if(switch):
            run('open', Larbot.larbot.s, channel, channel, [], self)
        else:
            run('close', Larbot.larbot.s, channel, channel, [], self)

    def subs_only(self, switch):
        channel = self.channel_line_edit.text().lower()
        type(self.open_line_checkbox.checkState())
        if(switch):
            run('subsonly', Larbot.larbot.s, channel, channel, ["on"], self)
        else:
            run('subsonly', Larbot.larbot.s, channel, channel, ["off"], self)

    def reset(self):
        channel = self.channel_line_edit.text().lower()
        run('reset', Larbot.larbot.s, channel, channel, [], self)

    def setcap(self):
        value = self.entrants_cap_spinbox.value()
        channel = self.channel_line_edit.text().lower()
        run('setcap', Larbot.larbot.s, channel, channel, [value], self)

    def set_list(self, new_list):
        while(self.player_list.count() > 0):
            self.player_list.takeItem(0)
        self.player_list.addItems(new_list)

    def remove_player(self):
        channel = self.channel_line_edit.text().lower()
        players = self.player_list.selectedIndexes()
        if(len(players) == 0):
            return

        for player in players:
            run('drop', Larbot.larbot.s, channel, player.data(), [], self)

    def swap_players(self):
        channel = self.channel_line_edit.text().lower()
        players = self.player_list.selectedIndexes()
        if(len(players) != 2):
            return

        run('swap', Larbot.larbot.s, channel, channel,
            [players[0].data(), players[1].data()], self)

    def login_failure_slot(self):
        QMessageBox.about(
            self,
            "Login failure",
            "Login attempt failed.\n"
            "Make sure the bot name, oauth are correct"
        )
        self.statusbar.showMessage("Not Connected")

    def update_line_opened(self, is_open):
        if(is_open):
            self.open_line_checkbox.setCheckState(
                PySide.QtCore.Qt.CheckState.Checked)
        else:
            self.open_line_checkbox.setCheckState(
                PySide.QtCore.Qt.CheckState.Unchecked)

    def update_subs_only(self, is_open):
        if(is_open):
            self.subscriber_checkbox.setCheckState(
                PySide.QtCore.Qt.CheckState.Checked)
        else:
            self.subscriber_checkbox.setCheckState(
                PySide.QtCore.Qt.CheckState.Unchecked)

    def update_line_cap(self, new_cap):
        if(new_cap is None):
            new_cap = 0
        self.entrants_cap_spinbox.setValue(new_cap)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    frame = MainWindow()
    load_ui(frame)
    frame.show()

    if(not os.path.isdir("save_states")):
        os.mkdir("save_states")

    try:
        with open("save_states/config.json.bin", "rb") as infile:
            json_load = json.loads(infile.read().decode())
            try:
                frame.bot_name_line_edit.setText(json_load['nick'])
            except KeyError:
                pass

            try:
                frame.bot_oauth_line_edit.setText(json_load['oauth'])
            except (KeyError, ValueError):
                pass

            try:
                frame.channel_line_edit.setText(json_load['channel'])
            except KeyError:
                pass
    except (FileNotFoundError, ValueError):
        pass

    app.exec_()
