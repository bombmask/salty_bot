import os
import sys
import time
import random
import threading
import socket
import requests
import ConfigParser

class SaltyBot:
    messages_received = 0

    def __init__(self, config_data):
        self.config_data = config_data
        self.irc = socket.socket()
        self.config_data = config_data
        self.twitch_host = 'irc.twitch.tv'
        self.port = 6667
        self.twitch_nick = config_data['twitch_nick']
        self.twitch_oauth = config_data['twitch_oauth']
        self.osu_api_key = config_data['osu_api_key']
        self.osu_irc_pass = config_data['osu_irc_pass']
        self.channel = config_data['channel']

    def twitch_check(self):
        self.url = 'https://api.twitch.tv/kraken/streams/'+self.channel
        self.headers = {'Accept' : 'application/vnd.twitchtv.v2+json'}
        
        self.data = requests.get(self.url, headers = self.headers)
        self.data_decode = self.data.json()
        self.data_stream = self.data_decode['stream']
        
        if self.data_stream == None:
            self.game = ''
            self.title = ''
            return self.game, self.title
        else:
            self.data_channel = self.data_stream['channel']
            self.game = self.data_stream['game']
            self.title = self.data_channel['status']
            return self.game, self.title

    def twitch_connect(self):
        self.irc.connect((self.twitch_host, self.port))
        self.irc.send('PASS {}\r\n'.format(self.twitch_oauth))
        self.irc.send('NICK {}\r\n'.format(self.twitch_nick))
        self.irc.send('JOIN #{}\r\n'.format(self.config_data['channel']))

    def twitch_send_message(self, response):
        self.to_send = 'PRIVMSG #{} :{}\r\n'.format(self.channel, response)
        self.to_send = self.to_send.encode('utf-8')
        self.irc.send(self.to_send)
        time.sleep(1.5)

    def osu_api_user(self):
        self.osu_nick = self.config_data['osu_nick']
        self.url = 'https://osu.ppy.sh/api/get_user?k={}&u={}'.format(self.osu_api_key, self.osu_nick)
        self.data = requests.get(self.url)
        
        self.data_decode = self.data.json()
        self.data_decode = self.data_decode[0]
        
        self.username = self.data_decode['username']
        self.level = self.data_decode['level']
        self.level = round(float(self.level))
        self.level = int(self.level)
        self.accuracy = self.data_decode['accuracy']
        self.accuracy = round(float(self.accuracy), 2)
        self.pp_rank = self.data_decode['pp_rank']
        
        self.response = '{} is level {} with {}% accuracy and ranked {}.'.format(self.username, self.level, self.accuracy, self.pp_rank)
        self.twitch_send_message(self.response)

    def add_text(self, text_type, text_add):
        self.text = text_add.split(' ')[-1]
        self.fo = open('{}_{}.txt'.format(self.channel, text_type), 'a+')
        self.fo.write(self.text)
        self.fo.close()
        self.response = 'You {} has been added for review.'.format(text_type)
        self.twitch_send_message(self.response)

    def text_retrieve(self, text_type):
        self.lines = sum(1 for line in open('{}_{}.txt'.format(self.channel, text_type), 'w+'))
        with open('{}_{}.txt'.format(self.channel, text_type), 'r') as self.data_file:
            self.lines_read = self.data_file.readlines()
        if self.lines == 0:
            self.response = 'No {}s have been added.'.format(text_type)
        elif self.lines == 1:
            self.response = self.lines_read
        else:
            self.select_line = random.randrange(1, self.lines, 1)
            self.response = self.lines_read[self.select_line]
        self.twitch_send_message(self.response)

    def twitch_run(self):
        self.game, self.title = self.twitch_check()
        self.twitch_connect()

        while True:
            
            self.message = self.irc.recv(4096)
            self.message = self.message.split('\r\n')[0]
            
            if self.message.startswith('PING'):
                self.irc.send('PONG tmi.twitch.tv\r\n')
                
            else:
                try:
                    self.action = self.message.split(' ')[1]
                except:
                    self.action = ''
                    
                if self.action == 'PRIVMSG':
                    self.sender = self.message.split(':')[1].split('!')[0]
                    self.message_body = ':'.join(self.message.split(':')[2:])
                    self.messages_received += 1

                    if self.message_body.find('http://osu.ppy.sh/b/') != -1 or self.message_body.find('http://osu.ppy.sh/s/') != -1:
                        self.osu_nick = self.config_data['osu_nick']
                        osu_send_message(self.osu_irc_pass, self.osu_nick, self.message_body)
                        
                    if self.message_body.startswith('!'):
                        self.message_body = self.message_body.split('!')[-1]

                        if self.message_body.startswith('addquote'):
                            self.add_text('quote', self.message_body)

                        if self.message_body == 'quote':
                            self.text_retrieve('quote')

                        if self.message_body.startswith('addpun'):
                            self.add_text('pun', self.message_body)

                        if self.message_body == 'pun':
                            self.text_retrieve('pun')
                        
                        if self.message_body == 'rank':
                            self.osu_api_user()

                        if self.message_body == 'recheck':
                            self.game, self.title = self.twitch_check()


                            
                    
                elif self.action == 'MODE':
                    if '+o ' in self.message:
                        self.admin = self.message.split('+o ')[-1]
                        self.fo = open('{}_admins.txt'.format(self.channel), 'r')
                        self.admin_file = self.fo.read()
                        self.fo.close()
                        
                        if self.admin not in self.admin_file:
                            self.fo = open('{}_admins.txt'.format(self.channel), 'a+')
                            self.fo.write(self.admin)
                            self.fo.close()

def osu_send_message(osu_irc_pass, osu_nick, request_url):
    irc = socket.socket()
    osu_host = 'irc.ppy.sh'
    osu_port = 6667
    irc.connect((osu_host, osu_port))
    irc.send('PASS {}\r\n'.format(osu_irc_pass))
    irc.send('NICK batedurgonnadie\r\n')
    irc.send('PRIVMSG {}: {}'.format(osu_nick, request_url))
    irc.close()
    
def main():
    #Config reader
    config = ConfigParser.SafeConfigParser()
    config.read('channels.ini')
    
    #Handling arrays
    channel_configs = {}
    bots = []
    
    for section_name in config.sections():
        channel_configs[section_name] = {}
        for name, value in config.items(section_name):
            channel_configs[section_name][name] = value
            channel_configs[section_name]['channel'] = section_name
            config.read('config.ini')
            channel_configs[section_name]['osu_api_key'] = config.get('General', 'osu_api_key')
            channel_configs[section_name]['osu_irc_pass'] = config.get('General', 'osu_irc_pass')

    for channels in channel_configs.values():
        bots.append(SaltyBot(channels))

    for bot in bots:
        tmp = threading.Thread(target=bot.twitch_run)
        tmp.daemon = True
        tmp.start()
    
    while True:
        time.sleep(1)
        

if __name__ == '__main__':
    main()
