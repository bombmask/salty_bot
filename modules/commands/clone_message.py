#! /usr/bin/env python3.4
# -*- coding: utf-8



#module info = m_info`
#command info
cmd_info = {
    "name" :"clone message",
    "author" :"Bombmask",
    "description" :"Echos stuff back to twitch",
    "version" :(0 ,0 ,0),
    "help" :"Help text?"
}

class clone(object):
    """docstring for clone"""
    
    def __init__(self, arg):
        super(clone, self).__init__()
        self.arg = arg
