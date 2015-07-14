#! /usr/bin/env python3.4
# -*- coding: utf-8

import glob, os, sys
import importlib

class PluginBase(object):
    """docstring for PluginBase"""

    def __init__(self, relative_path, *args, **kwargs):
        super(PluginBase, self).__init__()

        #Be safe, make sure things exist first
        if not os.path.exists(relative_path):
            raise ValueError("'{}' must be a vaild directory".format(relative_path))
            #I don't know if I need a return here, I don't think I do...

        #Stuff exists yay! start init and other data
        self.URI = os.path.abspath(relative_path)
        self.relative_path = relative_path

        #Kwargs eval
        #debugging kwarg
        #    #store level as well, IE debug level 3 is stored in kwarg
        self.debug = kwargs.get("debug", False)

        #if kwarg for "load on init" then load all files in path
        if kwargs.get("load_on_init", False):
            self.load_all()

        #Variable setup
        self.storage = {}

    #I don't know if I like this function, we'll see
    def load(self, URI, R_pattern=None):
        #Load module from init dir
        name = URI.split('/')[-1].split('.')[:-1]
        if self.debug: print(name)
        self.storage[name] = importlib.import_module(URI)

    def reload(self, name):

        #reload module from storage
        pass
        #check type
        #if type is abs ref (coming from reload_all)
        #then call reload nativly
        #else
        #lookup and reload

    def load_all(self):
        #Load all files in specified directory
        #Config var for init function

        for i_file in glob.iglob(self.relative_path+"/*.py"):
            if self.debug:
                print("Loading: {}...".format(i_file))
                print("{}".format(i_file.split('/')))
            self.load(i_file)
            print()

    def reload_all(self):
        for plugin in self.storage.items():
            if self.debug: print("Reloading: {}...".format(plugin[0]))
            self.reload(plugin)
        #Reload all files in init directory

    def destroy(self, name):
        pass

    def test_plugin(self, *args, **kwargs):
        pass
        #TravisCL?
