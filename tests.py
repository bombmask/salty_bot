import Plugin

# load a plugin module
test = Plugin.PluginBase("modules/commands", debug=1, load_on_init=False)

test.load_all()
