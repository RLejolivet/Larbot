Larbot Source Code
==================

Welcome to Larbot's source code repository !

This code may be used to recompile Larbot, check for errors, or simply to see how a Python bot for Twitch can work.

Any improvement idea is welcome.

Important compatibility note
============================

This bot only works with the standard Twitch IRC server. Not that I think it will ever be needed on a channel with the special "giant crowd" chat server, but it currently wouldn't be able to connect to it.

Documentation
=============

There is unfortunately no code documentation for people trying to read it. The basic idea is:

	- *run_ui.pyw* contains the Qt part of the project to make the interface work (along with the files in Larbot/ui)
	- *Larbot/larbot.py* contains the main loop, connecting to Twitch, receiving messages and parsing them
	- *Larbot/self_modules/message_queue.py* contains functions to make sending messages easier to Twitch
	- *Larbot/self_modules/commands_manager.py* links commands to the associated functions
	- *Larbot/self_modules/commands* contains all modules providing the functions to call for commands

Recompiling Larbot
==================

Requirements
------------

Python 3.4
~~~~~~~~~~

Larbot has been written for Python3, using Python3.4. It can be downloaded from `www.python.org`

PySide
~~~~~~

The graphical part of Larbot has been created using PySide.

It can easily be installed after Python has been installed by opening a command line interface and typing the command line::

	>>> pip install pyside

Py2Exe
~~~~~~

Turning the python program into an executable binary is done using Py2Exe. It is not necessary but very useful for distributing to people who won't have all this installed.

It can easily be installed after Python has been installed by opening a command line interface and typing the command line::

	>>> pip install py2exe

Running from source
-------------------

Python is an interpreted language, meaning it can be run directly without the need to compile.

To do so, run the file *run_ui.pyw*. If run directly from an explorer, il will behave like the compiled version.

You may also run it from a command line interface to have some debug messages::

	>>> python run_ui.pyw

Creating a compiled version
---------------------------

From a command line interface, run the command line::

	>>> python setup.py py2exe

The result will be in the folder *dist/*